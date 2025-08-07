#!/bin/bash

# GitLab MCP Server Quick Setup Script
# This script automates the installation process

set -e

echo "🚀 GitLab MCP Server Quick Setup"
echo "================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is required but not available."
    echo "   Please install pip and try again."
    exit 1
fi

echo "✅ pip found: $(python3 -m pip --version)"

# Create virtual environment
echo
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Test the installation
echo
echo "🧪 Testing installation..."
if echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | python3 mcp_server.py > /dev/null 2>&1; then
    echo "✅ MCP server is working correctly"
else
    echo "❌ MCP server test failed"
    exit 1
fi

# Run the interactive setup
echo
echo "🔧 Starting interactive configuration..."
echo "   (You can press Enter to use defaults)"
echo
python3 install.py

echo
echo "🎉 Installation complete!"
echo
echo "Next steps:"
echo "1. Update your GitLab token in the generated mcp.json file"
echo "2. Add the configuration to your MCP client (VS Code, Claude Desktop, etc.)"
echo "3. Or use the one-click install URL shown above"
echo
echo "For more information, see:"
echo "- README.md - Basic usage guide"
echo "- INSTALL.md - Detailed installation instructions"
echo "- install.html - Web-based installation page"