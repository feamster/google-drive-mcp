#!/usr/bin/env python3
"""Google Drive & Docs API client."""

import sys
from typing import Optional, Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import get_authenticated_credentials


class DocsClient:
    """Client for Google Drive, Docs, and Sheets APIs."""

    def __init__(self):
        """Initialize the Docs client."""
        self.creds = get_authenticated_credentials()
        if not self.creds:
            raise RuntimeError(
                "No valid credentials found. Please run authentication first:\n"
                "  python -m google_drive_mcp.auth"
            )

        # Build API services
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)

    # ========== Drive Operations ==========

    def list_files(
        self,
        query: Optional[str] = None,
        max_results: int = 50,
        order_by: str = "modifiedTime desc"
    ) -> List[Dict[str, Any]]:
        """List files from Google Drive.

        Args:
            query: Search query (e.g., "mimeType='application/vnd.google-apps.document'")
            max_results: Maximum number of results to return
            order_by: Sort order (e.g., "modifiedTime desc", "name")

        Returns:
            List of file metadata dictionaries
        """
        try:
            results = self.drive_service.files().list(
                pageSize=max_results,
                q=query,
                orderBy=order_by,
                fields="files(id, name, mimeType, modifiedTime, createdTime, webViewLink, owners)"
            ).execute()

            return results.get('files', [])

        except HttpError as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            raise

    def list_documents(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """List Google Docs documents.

        Args:
            max_results: Maximum number of results

        Returns:
            List of document metadata
        """
        query = "mimeType='application/vnd.google-apps.document'"
        return self.list_files(query=query, max_results=max_results)

    def list_spreadsheets(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """List Google Sheets spreadsheets.

        Args:
            max_results: Maximum number of results

        Returns:
            List of spreadsheet metadata
        """
        query = "mimeType='application/vnd.google-apps.spreadsheet'"
        return self.list_files(query=query, max_results=max_results)

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file.

        Args:
            file_id: The file ID

        Returns:
            File metadata dictionary
        """
        try:
            result = self.drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, createdTime, webViewLink, owners, description"
            ).execute()
            return result

        except HttpError as e:
            print(f"Error getting file metadata: {e}", file=sys.stderr)
            raise

    def search_files(self, search_term: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for files by name or content.

        Args:
            search_term: Search term
            max_results: Maximum number of results

        Returns:
            List of matching files
        """
        query = f"fullText contains '{search_term}'"
        return self.list_files(query=query, max_results=max_results)

    # ========== Document Operations ==========

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a Google Docs document.

        Args:
            document_id: The document ID

        Returns:
            Document object with full content and structure
        """
        try:
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            return document

        except HttpError as e:
            print(f"Error getting document: {e}", file=sys.stderr)
            raise

    def get_document_text(self, document_id: str) -> str:
        """Get plain text content from a document.

        Args:
            document_id: The document ID

        Returns:
            Plain text content
        """
        doc = self.get_document(document_id)
        content = doc.get('body', {}).get('content', [])

        text_parts = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_parts.append(elem['textRun'].get('content', ''))

        return ''.join(text_parts)

    def create_document(self, title: str) -> Dict[str, Any]:
        """Create a new Google Docs document.

        Args:
            title: Document title

        Returns:
            Created document object with documentId
        """
        try:
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()

            return document

        except HttpError as e:
            print(f"Error creating document: {e}", file=sys.stderr)
            raise

    def batch_update_document(
        self,
        document_id: str,
        requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute batch updates on a document.

        Args:
            document_id: The document ID
            requests: List of update requests

        Returns:
            Response from the batch update
        """
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return result

        except HttpError as e:
            print(f"Error updating document: {e}", file=sys.stderr)
            raise

    def insert_text(
        self,
        document_id: str,
        text: str,
        index: int = 1
    ) -> Dict[str, Any]:
        """Insert text at a specific index in the document.

        Args:
            document_id: The document ID
            text: Text to insert
            index: Character index (1 = beginning of document)

        Returns:
            Update response
        """
        requests = [{
            'insertText': {
                'location': {'index': index},
                'text': text
            }
        }]
        return self.batch_update_document(document_id, requests)

    def replace_all_text(
        self,
        document_id: str,
        find_text: str,
        replace_text: str,
        match_case: bool = False
    ) -> Dict[str, Any]:
        """Replace all occurrences of text in a document.

        Args:
            document_id: The document ID
            find_text: Text to find
            replace_text: Replacement text
            match_case: Whether to match case

        Returns:
            Update response
        """
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': match_case
                },
                'replaceText': replace_text
            }
        }]
        return self.batch_update_document(document_id, requests)

    def delete_content_range(
        self,
        document_id: str,
        start_index: int,
        end_index: int
    ) -> Dict[str, Any]:
        """Delete content in a specific range.

        Args:
            document_id: The document ID
            start_index: Start character index
            end_index: End character index

        Returns:
            Update response
        """
        requests = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                }
            }
        }]
        return self.batch_update_document(document_id, requests)

    def append_text(self, document_id: str, text: str) -> Dict[str, Any]:
        """Append text to the end of a document.

        Args:
            document_id: The document ID
            text: Text to append

        Returns:
            Update response
        """
        # Get document to find the end index
        doc = self.get_document(document_id)
        end_index = doc['body']['content'][-1]['endIndex'] - 1

        return self.insert_text(document_id, text, end_index)

    def format_text(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        font_size: Optional[int] = None,
        font_family: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply formatting to a text range.

        Args:
            document_id: The document ID
            start_index: Start character index
            end_index: End character index
            bold: Make text bold
            italic: Make text italic
            underline: Underline text
            font_size: Font size in points
            font_family: Font family name

        Returns:
            Update response
        """
        text_style = {}
        fields = []

        if bold is not None:
            text_style['bold'] = bold
            fields.append('bold')

        if italic is not None:
            text_style['italic'] = italic
            fields.append('italic')

        if underline is not None:
            text_style['underline'] = underline
            fields.append('underline')

        if font_size is not None:
            text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
            fields.append('fontSize')

        if font_family is not None:
            text_style['weightedFontFamily'] = {'fontFamily': font_family}
            fields.append('weightedFontFamily')

        requests = [{
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': text_style,
                'fields': ','.join(fields)
            }
        }]

        return self.batch_update_document(document_id, requests)

    # ========== Spreadsheet Operations ==========

    def get_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Get a Google Sheets spreadsheet.

        Args:
            spreadsheet_id: The spreadsheet ID

        Returns:
            Spreadsheet object
        """
        try:
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            return spreadsheet

        except HttpError as e:
            print(f"Error getting spreadsheet: {e}", file=sys.stderr)
            raise

    def get_sheet_values(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> List[List[Any]]:
        """Get values from a spreadsheet range.

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range (e.g., "Sheet1!A1:D10")

        Returns:
            List of rows, each row is a list of cell values
        """
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            return result.get('values', [])

        except HttpError as e:
            print(f"Error getting sheet values: {e}", file=sys.stderr)
            raise

    def update_sheet_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """Update values in a spreadsheet range.

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range
            values: List of rows to write

        Returns:
            Update response
        """
        try:
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            return result

        except HttpError as e:
            print(f"Error updating sheet values: {e}", file=sys.stderr)
            raise

    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        """Create a new Google Sheets spreadsheet.

        Args:
            title: Spreadsheet title

        Returns:
            Created spreadsheet object
        """
        try:
            spreadsheet = self.sheets_service.spreadsheets().create(
                body={'properties': {'title': title}}
            ).execute()

            return spreadsheet

        except HttpError as e:
            print(f"Error creating spreadsheet: {e}", file=sys.stderr)
            raise
