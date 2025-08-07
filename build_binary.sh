#!/bin/bash

# Build script for GitLab MCP Server binary
# This script creates a standalone executable using PyInstaller

set -e

echo "Building GitLab MCP Server binary..."

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Activate virtual environment and build
if [ -f "./venv/bin/python3.13" ]; then
    echo "Using virtual environment..."
    ./venv/bin/python3.13 -m PyInstaller \
        --onefile \
        --name gitlab-mcp-server \
        --clean \
        mcp_server.py
else
    echo "Virtual environment not found, using system Python..."
    python3 -m PyInstaller \
        --onefile \
        --name gitlab-mcp-server \
        --clean \
        mcp_server.py
fi

# Test the binary
echo "Testing the binary..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | ./dist/gitlab-mcp-server > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Binary built successfully!"
    echo "📦 Location: ./dist/gitlab-mcp-server"
    echo "📏 Size: $(ls -lh dist/gitlab-mcp-server | awk '{print $5}')"
    echo ""
    echo "You can now use the binary directly:"
    echo "  ./dist/gitlab-mcp-server"
    echo ""
    echo "Or copy it to your PATH:"
    echo "  cp dist/gitlab-mcp-server /usr/local/bin/"
else
    echo "❌ Binary test failed!"
    exit 1
fi
