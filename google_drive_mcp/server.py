#!/usr/bin/env python3
"""Google Drive & Docs MCP Server."""

import asyncio
import json
import sys
import traceback
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .docs_client import DocsClient


# Initialize docs client with error handling
try:
    docs = DocsClient()
except Exception as e:
    error_msg = f"Failed to initialize DocsClient: {str(e)}\n"
    error_msg += f"Error type: {type(e).__name__}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr, flush=True)
    raise RuntimeError(f"Google Drive MCP initialization failed: {str(e)}") from e


# Create server instance
server = Server("google-drive-mcp-server")


# Define tools
TOOLS: list[Tool] = [
    # Drive/File listing tools
    Tool(
        name="list_files",
        description="List files from Google Drive with optional filtering and sorting",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g., \"mimeType='application/vnd.google-apps.document'\")"},
                "maxResults": {"type": "number", "description": "Max results (default: 50)", "default": 50},
                "orderBy": {"type": "string", "description": "Sort order (default: 'modifiedTime desc')", "default": "modifiedTime desc"}
            }
        }
    ),
    Tool(
        name="list_documents",
        description="List Google Docs documents",
        inputSchema={
            "type": "object",
            "properties": {
                "maxResults": {"type": "number", "description": "Max results (default: 50)", "default": 50}
            }
        }
    ),
    Tool(
        name="list_spreadsheets",
        description="List Google Sheets spreadsheets",
        inputSchema={
            "type": "object",
            "properties": {
                "maxResults": {"type": "number", "description": "Max results (default: 50)", "default": 50}
            }
        }
    ),
    Tool(
        name="search_files",
        description="Search for files by name or content",
        inputSchema={
            "type": "object",
            "properties": {
                "searchTerm": {"type": "string", "description": "Search term"},
                "maxResults": {"type": "number", "description": "Max results (default: 20)", "default": 20}
            },
            "required": ["searchTerm"]
        }
    ),
    Tool(
        name="get_file_metadata",
        description="Get metadata for a specific file",
        inputSchema={
            "type": "object",
            "properties": {
                "fileId": {"type": "string", "description": "The file ID"}
            },
            "required": ["fileId"]
        }
    ),

    # Document tools
    Tool(
        name="get_document",
        description="Get full document structure and content",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"}
            },
            "required": ["documentId"]
        }
    ),
    Tool(
        name="get_document_text",
        description="Get plain text content from a document",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"}
            },
            "required": ["documentId"]
        }
    ),
    Tool(
        name="create_document",
        description="Create a new Google Docs document",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Document title"}
            },
            "required": ["title"]
        }
    ),
    Tool(
        name="insert_text",
        description="Insert text at a specific index in the document",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "text": {"type": "string", "description": "Text to insert"},
                "index": {"type": "number", "description": "Character index (1 = beginning)", "default": 1}
            },
            "required": ["documentId", "text"]
        }
    ),
    Tool(
        name="append_text",
        description="Append text to the end of a document",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "text": {"type": "string", "description": "Text to append"}
            },
            "required": ["documentId", "text"]
        }
    ),
    Tool(
        name="replace_all_text",
        description="Replace all occurrences of text in a document",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "findText": {"type": "string", "description": "Text to find"},
                "replaceText": {"type": "string", "description": "Replacement text"},
                "matchCase": {"type": "boolean", "description": "Match case (default: false)", "default": False}
            },
            "required": ["documentId", "findText", "replaceText"]
        }
    ),
    Tool(
        name="delete_content_range",
        description="Delete content in a specific character range",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "startIndex": {"type": "number", "description": "Start character index"},
                "endIndex": {"type": "number", "description": "End character index"}
            },
            "required": ["documentId", "startIndex", "endIndex"]
        }
    ),
    Tool(
        name="format_text",
        description="Apply formatting to a text range",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "startIndex": {"type": "number", "description": "Start character index"},
                "endIndex": {"type": "number", "description": "End character index"},
                "bold": {"type": "boolean", "description": "Make text bold"},
                "italic": {"type": "boolean", "description": "Make text italic"},
                "underline": {"type": "boolean", "description": "Underline text"},
                "fontSize": {"type": "number", "description": "Font size in points"},
                "fontFamily": {"type": "string", "description": "Font family name"}
            },
            "required": ["documentId", "startIndex", "endIndex"]
        }
    ),
    Tool(
        name="batch_update_document",
        description="Execute batch updates on a document (advanced - requires knowledge of Docs API request format)",
        inputSchema={
            "type": "object",
            "properties": {
                "documentId": {"type": "string", "description": "The document ID"},
                "requests": {"type": "array", "description": "List of update request objects"}
            },
            "required": ["documentId", "requests"]
        }
    ),

    # Spreadsheet tools
    Tool(
        name="get_spreadsheet",
        description="Get spreadsheet metadata and structure",
        inputSchema={
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string", "description": "The spreadsheet ID"}
            },
            "required": ["spreadsheetId"]
        }
    ),
    Tool(
        name="get_sheet_values",
        description="Get values from a spreadsheet range",
        inputSchema={
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string", "description": "The spreadsheet ID"},
                "range": {"type": "string", "description": "A1 notation range (e.g., 'Sheet1!A1:D10')"}
            },
            "required": ["spreadsheetId", "range"]
        }
    ),
    Tool(
        name="update_sheet_values",
        description="Update values in a spreadsheet range",
        inputSchema={
            "type": "object",
            "properties": {
                "spreadsheetId": {"type": "string", "description": "The spreadsheet ID"},
                "range": {"type": "string", "description": "A1 notation range"},
                "values": {"type": "array", "description": "List of rows to write"}
            },
            "required": ["spreadsheetId", "range", "values"]
        }
    ),
    Tool(
        name="create_spreadsheet",
        description="Create a new Google Sheets spreadsheet",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Spreadsheet title"}
            },
            "required": ["title"]
        }
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        # Drive/File listing tools
        if name == "list_files":
            result = docs.list_files(
                query=arguments.get("query"),
                max_results=arguments.get("maxResults", 50),
                order_by=arguments.get("orderBy", "modifiedTime desc")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_documents":
            result = docs.list_documents(
                max_results=arguments.get("maxResults", 50)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_spreadsheets":
            result = docs.list_spreadsheets(
                max_results=arguments.get("maxResults", 50)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_files":
            result = docs.search_files(
                search_term=arguments["searchTerm"],
                max_results=arguments.get("maxResults", 20)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_file_metadata":
            result = docs.get_file_metadata(arguments["fileId"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Document tools
        elif name == "get_document":
            result = docs.get_document(arguments["documentId"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_document_text":
            result = docs.get_document_text(arguments["documentId"])
            return [TextContent(type="text", text=result)]

        elif name == "create_document":
            result = docs.create_document(arguments["title"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "insert_text":
            result = docs.insert_text(
                document_id=arguments["documentId"],
                text=arguments["text"],
                index=arguments.get("index", 1)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "append_text":
            result = docs.append_text(
                document_id=arguments["documentId"],
                text=arguments["text"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "replace_all_text":
            result = docs.replace_all_text(
                document_id=arguments["documentId"],
                find_text=arguments["findText"],
                replace_text=arguments["replaceText"],
                match_case=arguments.get("matchCase", False)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_content_range":
            result = docs.delete_content_range(
                document_id=arguments["documentId"],
                start_index=arguments["startIndex"],
                end_index=arguments["endIndex"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "format_text":
            result = docs.format_text(
                document_id=arguments["documentId"],
                start_index=arguments["startIndex"],
                end_index=arguments["endIndex"],
                bold=arguments.get("bold"),
                italic=arguments.get("italic"),
                underline=arguments.get("underline"),
                font_size=arguments.get("fontSize"),
                font_family=arguments.get("fontFamily")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "batch_update_document":
            result = docs.batch_update_document(
                document_id=arguments["documentId"],
                requests=arguments["requests"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Spreadsheet tools
        elif name == "get_spreadsheet":
            result = docs.get_spreadsheet(arguments["spreadsheetId"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_sheet_values":
            result = docs.get_sheet_values(
                spreadsheet_id=arguments["spreadsheetId"],
                range_name=arguments["range"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "update_sheet_values":
            result = docs.update_sheet_values(
                spreadsheet_id=arguments["spreadsheetId"],
                range_name=arguments["range"],
                values=arguments["values"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "create_spreadsheet":
            result = docs.create_spreadsheet(arguments["title"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
