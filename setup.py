#!/usr/bin/env python3
"""Setup script for google-drive-mcp package."""

from setuptools import setup, find_packages

setup(
    name="google-drive-mcp",
    version="0.1.0",
    description="MCP server for Google Drive, Docs, and Sheets access",
    author="Nick Feamster",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.100.0",
        "mcp>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "google-drive-mcp=google_drive_mcp.server:main",
            "google-drive-mcp-auth=google_drive_mcp.auth:main",
        ],
    },
)
