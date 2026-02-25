#!/usr/bin/env python3
"""OAuth2 authentication for Google Drive & Docs API."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for Google Drive and Docs - full access
SCOPES = [
    'https://www.googleapis.com/auth/documents',  # Google Docs
    'https://www.googleapis.com/auth/drive',      # Google Drive
    'https://www.googleapis.com/auth/spreadsheets',  # Google Sheets
    'https://www.googleapis.com/auth/script.external_request',  # Apps Script
]

# Config directories
# Auth data (sensitive) stored in Box for sync
BOX_MCP_AUTH_DIR = Path.home() / "Library" / "CloudStorage" / "Box-Box" / "mcp-auth" / "google-drive-mcp"
TOKENS_DIR = BOX_MCP_AUTH_DIR / "tokens"
CREDENTIALS_FILE = BOX_MCP_AUTH_DIR / "credentials.json"

# Local symlink location for token (for compatibility)
LOCAL_CONFIG_DIR = Path.home() / ".config" / "google-drive-mcp"
LOCAL_TOKEN_FILE = LOCAL_CONFIG_DIR / "token.json"


def get_auth_dir() -> Path:
    """Ensure auth directory exists."""
    BOX_MCP_AUTH_DIR.mkdir(parents=True, exist_ok=True)
    return BOX_MCP_AUTH_DIR


def get_tokens_dir() -> Path:
    """Ensure tokens directory exists."""
    get_auth_dir()  # Ensure parent exists
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    return TOKENS_DIR


def get_credentials_file() -> Path:
    """Get credentials file path."""
    return CREDENTIALS_FILE


def get_token_file() -> Path:
    """Get the token file path (from Box storage or fallback to local)."""
    # First check if Box location exists
    box_token = TOKENS_DIR / "token.json"
    if box_token.exists():
        return box_token

    # Fallback to local config
    if LOCAL_TOKEN_FILE.exists():
        return LOCAL_TOKEN_FILE

    # Default to Box location for new tokens
    get_tokens_dir()  # Ensure directory exists
    return box_token


def load_credentials_json() -> dict:
    """Load OAuth client credentials from credentials.json."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"Credentials file not found at {CREDENTIALS_FILE}. "
            f"Please create it with your Google OAuth client ID and secret."
        )

    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)


def get_authenticated_credentials() -> Optional[Credentials]:
    """Get authenticated credentials, refreshing if needed.

    Returns:
        Credentials object if authenticated, None if needs initial auth
    """
    creds = None
    token_file = get_token_file()

    # Load existing token if available
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}", file=sys.stderr)
            creds = None

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed token
            save_credentials(creds)
        except Exception as e:
            print(f"Error refreshing token: {e}", file=sys.stderr)
            return None

    # Return valid creds or None if needs auth
    if creds and creds.valid:
        return creds

    return None


def save_credentials(creds: Credentials):
    """Save credentials to token file."""
    token_file = get_token_file()
    with open(token_file, 'w') as f:
        f.write(creds.to_json())
    print(f"Token saved to {token_file}", file=sys.stderr)


def authenticate_user() -> Credentials:
    """Run OAuth flow to authenticate user.

    Returns:
        Credentials object
    """
    # Load client credentials
    creds_data = load_credentials_json()

    # Create installed app config
    client_config = {
        "installed": {
            "client_id": creds_data["client_id"],
            "client_secret": creds_data["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"]
        }
    }

    # Run OAuth flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save credentials
    save_credentials(creds)

    return creds


def main():
    """CLI tool for authenticating with Google."""
    print("Google Drive & Docs MCP Authentication")
    print("=" * 50)
    print(f"Credentials file: {CREDENTIALS_FILE}")
    print(f"Token file: {get_token_file()}")
    print()

    try:
        # Check for existing valid credentials
        creds = get_authenticated_credentials()

        if creds:
            print("✓ Already authenticated!")
            print(f"Token valid until: {creds.expiry}")
        else:
            print("No valid credentials found. Starting authentication...")
            creds = authenticate_user()
            print("✓ Authentication successful!")

        print(f"\nToken saved to: {get_token_file()}")
        print("\nYou can now use the Google Drive MCP server.")

    except Exception as e:
        print(f"✗ Authentication failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
