# Google Docs MCP Server Setup

This directory contains setup instructions for the [google-docs-mcp](https://github.com/a-bonus/google-docs-mcp) server, which enables Claude Code to read, edit, and manage Google Docs, Drive files, and Sheets.

## Prerequisites

- Node.js v18+
- A Google Cloud project with OAuth credentials
- Claude Code installed

## Google Cloud Setup (One-time)

If you haven't already set up the Google Cloud project:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable APIs:
    - Google Docs API
    - Google Drive API
    - Google Sheets API (optional)
4. Configure OAuth consent screen:
    - Choose "External" user type
    - Add required app info (name, support email)
    - Add scopes: `../auth/documents`, `../auth/drive`, `../auth/spreadsheets`
    - Add your email as a Test User
5. Create OAuth 2.0 credentials:
    - Type: Desktop app
    - Save the Client ID and Client Secret

## Credentials Storage

Credentials are stored in Box for backup and sync across machines:

```
~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/
├── credentials.json       # Client ID and Secret
└── tokens/
    └── token.json        # OAuth refresh token
```

The `credentials.json` file should look like:
```json
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "client_secret": "your-client-secret"
}
```

## Installation on New Machine

### Step 1: Verify Box Sync

Ensure Box is synced and the credentials exist:
```bash
ls -la ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/
```

### Step 2: Create Symlink for Token

The MCP server expects the token at `~/.config/google-docs-mcp/token.json`. Create a symlink to the Box location:

```bash
mkdir -p ~/.config/google-docs-mcp
ln -s ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/token.json ~/.config/google-docs-mcp/token.json
```

### Step 3: Configure Claude Code

Create or edit `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "npx",
      "args": ["-y", "@a-bonus/google-docs-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "YOUR_CLIENT_SECRET"
      }
    }
  }
}
```

### Step 4: Authenticate (if token doesn't exist yet)

If this is the first machine or the token is missing, run authentication:

```bash
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com" \
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
npx -y @a-bonus/google-docs-mcp auth
```

This will:
- Open a browser for Google authorization
- Store the refresh token at `~/.config/google-docs-mcp/token.json`
- Since this is a symlink, the token will be saved to Box automatically

### Step 5: Restart Claude Code

Restart Claude Code to load the MCP server.

## Verification

After restart, test the connection:
```
Ask Claude Code to list your Google Docs or read a specific document.
```

## Available Tools

Once configured, these tools are available:

| Tool | Description |
|------|-------------|
| `get_document` | Fetch document content by ID |
| `create_document` | Create a new Google Doc |
| `edit_document` | Make changes to a document |
| `list_documents` | List documents in Drive |
| `get_comments` | Retrieve document comments |
| `resolve_comment` | Mark comments as resolved |

## Troubleshooting

### Token not found
- Verify Box is synced: `ls ~/Library/CloudStorage/Box-Box/mcp-auth/google-drive-mcp/tokens/`
- Check symlink: `ls -la ~/.config/google-docs-mcp/token.json`
- Re-run authentication if needed

### MCP server not loading
- Check `.mcp.json` syntax: `cat ~/.claude/.mcp.json | jq`
- Verify credentials are correct
- Check Claude Code logs

### Authentication failures
- Ensure your email is listed as a Test User in OAuth consent screen
- Verify all required APIs are enabled
- Try deleting token and re-authenticating

## Resources

- [google-docs-mcp GitHub](https://github.com/a-bonus/google-docs-mcp)
- [Claude Code MCP Docs](https://docs.claude.com/en/docs/claude-code/mcp)
- [Google Cloud Console](https://console.cloud.google.com/)
