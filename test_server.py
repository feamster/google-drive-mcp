#!/usr/bin/env python3
"""Quick test of the Google Drive MCP server."""

import asyncio
import sys
from google_drive_mcp.docs_client import DocsClient

async def main():
    print("Testing Google Drive MCP Server")
    print("=" * 50)

    try:
        # Initialize client
        print("\n1. Initializing DocsClient...")
        client = DocsClient()
        print("   ✓ Client initialized successfully")

        # Test listing documents
        print("\n2. Listing recent Google Docs...")
        docs = client.list_documents(max_results=5)
        print(f"   ✓ Found {len(docs)} documents")
        for i, doc in enumerate(docs, 1):
            print(f"   {i}. {doc['name']} (ID: {doc['id']})")

        # Test listing spreadsheets
        print("\n3. Listing recent Google Sheets...")
        sheets = client.list_spreadsheets(max_results=5)
        print(f"   ✓ Found {len(sheets)} spreadsheets")
        for i, sheet in enumerate(sheets, 1):
            print(f"   {i}. {sheet['name']} (ID: {sheet['id']})")

        # Test getting document text
        if docs:
            print(f"\n4. Reading first document: {docs[0]['name']}")
            text = client.get_document_text(docs[0]['id'])
            preview = text[:200] if len(text) > 200 else text
            print(f"   ✓ Retrieved {len(text)} characters")
            print(f"   Preview: {preview}...")

        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("\nAvailable capabilities:")
        print("  • List/search files")
        print("  • Read document content")
        print("  • Create/edit documents")
        print("  • Format text (bold, italic, fonts)")
        print("  • Replace text")
        print("  • Read/write spreadsheets")

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
