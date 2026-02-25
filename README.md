# Google Drive MCP Server

A custom Model Context Protocol (MCP) server for Google Drive, Docs, and Sheets. Built for powerful document editing and file management with Claude Code.

**Author:** Nick Feamster

## Features

### Drive Operations
- List files with filtering and sorting
- Search files by content or name
- Get file metadata
- List documents and spreadsheets

### Document Operations
- Get full document structure and content
- Extract plain text from documents
- Create new documents
- Insert, append, and replace text
- Delete content ranges
- Apply text formatting (bold, italic, underline, font size/family)
- Batch update documents with custom requests

### Spreadsheet Operations
- Get spreadsheet metadata and structure
- Read cell values from ranges
- Update cell values
- Create new spreadsheets

## Prerequisites

- Python 3.10+
- Box Drive sync (for credential storage)
- A Google Cloud project with OAuth credentials
- Claude Code installed

## Architecture Overview

This MCP server uses a distributed credential storage approach:

1. **Code Repository** (`~/src/google-drive-mcp/`) - Cloned from GitHub
2. **Credentials Storage** (`~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/`) - OAuth credentials in Box (synced across machines)
3. **MCP Configuration** (`~/.claude/.mcp.json`) - Can be managed via dotfiles repo

This allows:
- Code updates via git pull
- Automatic credential sync via Box
- Easy setup on new machines

## Google Cloud Setup (One-time)

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the following APIs:
    - Google Docs API
    - Google Drive API
    - Google Sheets API

### 2. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in required app info:
    - App name: "Google Drive MCP"
    - Support email: your email
4. Add scopes:
    - `https://www.googleapis.com/auth/documents`
    - `https://www.googleapis.com/auth/drive`
    - `https://www.googleapis.com/auth/spreadsheets`
    - `https://www.googleapis.com/auth/script.external_request`
5. Add your email as a **Test User** (important!)
6. Save and continue

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: **Desktop app**
4. Name it (e.g., "Google Drive MCP Client")
5. Click "Create"
6. Save the **Client ID** and **Client Secret**

## Credentials Storage in Box

All OAuth credentials are stored in Box for automatic sync across machines.

### Directory Structure

```
~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/
├── credentials.json       # OAuth Client ID and Secret
└── tokens/
    └── token.json        # OAuth refresh token (auto-generated)
```

### Create credentials.json

Create the file in Box with your OAuth credentials:

```bash
# Create directory structure
mkdir -p ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens

# Create credentials.json (replace with your actual credentials from Google Cloud Console)
cat > ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/credentials.json <<'EOF'
{
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET"
}
EOF
```

**Important:** The credentials.json file contains the OAuth Client ID and Secret from your Google Cloud project. These are the same credentials used across all your machines.

## Installation

### First Machine Setup

1. **Clone the repository:**
```bash
cd ~/src
git clone https://github.com/feamster/google-drive-mcp.git
cd google-drive-mcp
```

2. **Install the package:**
```bash
python3 -m pip install -e .
```

3. **Verify Box credentials exist:**
```bash
ls -la ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/
# Should show: credentials.json and tokens/ directory
```

4. **Run authentication:**
```bash
python3 -m google_drive_mcp.auth
```

This will:
- Open a browser for Google authorization
- Ask you to sign in and grant permissions
- Save the refresh token to Box at `~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/token.json`

5. **Configure Claude Code:**

Add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "python",
      "args": ["-m", "google_drive_mcp.server"],
      "cwd": "/Users/YOUR_USERNAME/src/google-drive-mcp"
    }
  }
}
```

**Note:** If you manage `.mcp.json` via a dotfiles repo, add this configuration there instead.

6. **Restart Claude Code**

### New Machine Setup

When setting up on a new machine (assuming Box is already synced):

1. **Clone the repository:**
```bash
cd ~/src
git clone https://github.com/feamster/google-drive-mcp.git
cd google-drive-mcp
```

2. **Install the package:**
```bash
python3 -m pip install -e .
```

3. **Verify Box is synced with credentials:**
```bash
ls -la ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/
# Should show: credentials.json and tokens/token.json
```

If the token exists in Box, you're done! The server will use it automatically.

If the token is missing (first-time Box sync), run authentication:
```bash
python3 -m google_drive_mcp.auth
```

4. **Configure Claude Code** (if not using dotfiles):

Add to `~/.claude/.mcp.json` (adjust username):

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "python",
      "args": ["-m", "google_drive_mcp.server"],
      "cwd": "/Users/YOUR_USERNAME/src/google-drive-mcp"
    }
  }
}
```

5. **Restart Claude Code**

## Testing

Test the server before using it with Claude Code:

```bash
cd ~/src/google-drive-mcp
python3 test_server.py
```

This will:
- Initialize the DocsClient
- List your recent Google Docs and Sheets
- Read content from your first document
- Verify all capabilities are working

Expected output:
```
Testing Google Drive MCP Server
==================================================

1. Initializing DocsClient...
   ✓ Client initialized successfully

2. Listing recent Google Docs...
   ✓ Found 5 documents
   ...

All tests passed! ✓
```

## Available Tools (18 total)

### Drive Tools (5)
- `list_files(query?, maxResults?, orderBy?)` - List files with optional filtering and sorting
- `list_documents(maxResults?)` - List Google Docs documents
- `list_spreadsheets(maxResults?)` - List Google Sheets spreadsheets
- `search_files(searchTerm, maxResults?)` - Search for files by name or content
- `get_file_metadata(fileId)` - Get metadata for a specific file

### Document Tools (9)
- `get_document(documentId)` - Get full document structure and content
- `get_document_text(documentId)` - Get plain text content from a document
- `create_document(title)` - Create a new Google Docs document
- `insert_text(documentId, text, index?)` - Insert text at a specific index
- `append_text(documentId, text)` - Append text to the end of a document
- `replace_all_text(documentId, findText, replaceText, matchCase?)` - Replace all occurrences of text
- `delete_content_range(documentId, startIndex, endIndex)` - Delete content in a specific range
- `format_text(documentId, startIndex, endIndex, bold?, italic?, underline?, fontSize?, fontFamily?)` - Apply formatting to a text range
- `batch_update_document(documentId, requests)` - Execute batch updates (advanced - requires knowledge of Docs API)

### Spreadsheet Tools (4)
- `get_spreadsheet(spreadsheetId)` - Get spreadsheet metadata and structure
- `get_sheet_values(spreadsheetId, range)` - Get values from a spreadsheet range (A1 notation)
- `update_sheet_values(spreadsheetId, range, values)` - Update values in a spreadsheet range
- `create_spreadsheet(title)` - Create a new Google Sheets spreadsheet

## Usage Examples

### List Recent Documents
```
Claude: "List my 10 most recent Google Docs"
```

### Read a Document
```
Claude: "Read the content of document ID 1Bdjo1UJSoxUMyr__zaaNU8Dgmlkmtoq3tRCdGcQLM0k"
```

### Edit a Document
```
Claude: "In document 1Bdjo1UJSoxUMyr__zaaNU8Dgmlkmtoq3tRCdGcQLM0k, replace all instances of 'old text' with 'new text'"
```

### Format Text
```
Claude: "Make the first paragraph of document XYZ bold and increase font size to 14pt"
```

### Create a New Document
```
Claude: "Create a new Google Doc titled 'Meeting Notes' and add an agenda with 3 bullet points"
```

### Work with Spreadsheets
```
Claude: "Read cells A1:D10 from spreadsheet 1IkXxxTBw7onokE0ZEH4RAVrFZBQQOtOEb2F9U6xZ_DE"
Claude: "Update cell A1 in that spreadsheet to say 'Total Revenue'"
```

## Development

### Project Structure
```
google-drive-mcp/
├── google_drive_mcp/
│   ├── __init__.py       # Package initialization
│   ├── auth.py           # OAuth2 authentication with Box integration
│   ├── docs_client.py    # Google API client (Drive, Docs, Sheets)
│   └── server.py         # MCP server implementation
├── test_server.py        # Testing script
├── setup.py              # Package setup
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

### Adding New Features

The client (`docs_client.py`) can be extended with additional Google API methods. The server (`server.py`) exposes these as MCP tools.

**Steps to add a new tool:**

1. Add method to `DocsClient` class in `google_drive_mcp/docs_client.py`:
```python
def my_new_feature(self, document_id: str, param: str) -> Dict[str, Any]:
    """Description of what this does."""
    # Implementation using Google API
    ...
```

2. Add tool definition to `TOOLS` list in `google_drive_mcp/server.py`:
```python
Tool(
    name="my_new_feature",
    description="Brief description for Claude",
    inputSchema={
        "type": "object",
        "properties": {
            "documentId": {"type": "string", "description": "Document ID"},
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["documentId", "param"]
    }
)
```

3. Add handler in `call_tool()` function in `google_drive_mcp/server.py`:
```python
elif name == "my_new_feature":
    result = docs.my_new_feature(
        document_id=arguments["documentId"],
        param=arguments["param"]
    )
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

4. Test and commit:
```bash
python3 test_server.py  # Verify it works
git add .
git commit -m "Add my_new_feature capability"
git push
```

### Planned Features

Features to add (based on comparison with other MCP servers):

**Priority 1:**
- [ ] Comments system (list, create, reply, resolve, delete)
- [ ] Image insertion (from URLs or files)
- [ ] Tables and page breaks
- [ ] Advanced text formatting (colors, links, alignment, spacing)
- [ ] File management (move, copy, rename, delete, folders)

**Priority 2:**
- [ ] Markdown conversion and round-trip
- [ ] Sheets formatting (cell colors, alignment, freeze panes, dropdowns)
- [ ] Template support
- [ ] Multi-tab document support

## Troubleshooting

### Authentication Issues

**Problem:** "No valid credentials found"

**Solution:**
1. Verify Box is synced: `ls ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/`
2. Check credentials.json exists and is valid JSON
3. Ensure your email is listed as a Test User in OAuth consent screen
4. Verify all required APIs are enabled in Google Cloud Console
5. Re-run authentication: `python3 -m google_drive_mcp.auth`

### Token Not Found

```bash
# Verify Box is synced
ls ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/

# Check token contents (should have refresh_token)
cat ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/token.json

# Re-authenticate if needed
python3 -m google_drive_mcp.auth
```

### MCP Server Not Loading

1. Check Claude Code logs for errors
2. Verify the `cwd` path in `.mcp.json` matches your username:
   ```bash
   whoami  # Check your username
   cat ~/.claude/.mcp.json | grep google-drive
   ```
3. Test the server manually:
   ```bash
   cd ~/src/google-drive-mcp
   python3 -m google_drive_mcp.server
   # Should start without errors (use Ctrl+C to exit)
   ```
4. Verify package is installed:
   ```bash
   python3 -c "import google_drive_mcp; print(google_drive_mcp.__version__)"
   # Should print: 0.1.0
   ```

### Box Sync Issues

**Problem:** Credentials or tokens not syncing

**Solution:**
1. Verify Box is running and synced
2. Check Box preferences for selective sync settings
3. Manually verify file exists on Box.com web interface
4. Force sync by touching the file: `touch ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/token.json`

### Dotfiles Repo Integration

If you manage your Claude Code configuration via a dotfiles repo:

1. Add `.mcp.json` to your dotfiles repo
2. Symlink it: `ln -s ~/dotfiles/.claude/.mcp.json ~/.claude/.mcp.json`
3. Commit and push the configuration
4. On new machines, your dotfiles setup script should handle the symlink

## Resources

- [Google Docs API Reference](https://developers.google.com/docs/api)
- [Google Drive API Reference](https://developers.google.com/drive/api)
- [Google Sheets API Reference](https://developers.google.com/sheets/api)
- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [Google Cloud Console](https://console.cloud.google.com/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)

## License

MIT

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Google API documentation
3. Test with `test_server.py` to isolate the problem
4. Check Claude Code logs for detailed error messages
