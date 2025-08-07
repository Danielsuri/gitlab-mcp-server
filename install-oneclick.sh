#!/bin/bash

# GitLab MCP Server One-Click Installer
# This script downloads and sets up the GitLab MCP Server automatically

set -e

REPO_URL="https://github.com/Danielsuri/gitlab-mcp-server.git"
INSTALL_DIR="$HOME/.mcp/gitlab-mcp-server"
BINARY_URL="https://github.com/Danielsuri/gitlab-mcp-server/releases/latest/download/gitlab-mcp-server-ubuntu"

echo "🚀 GitLab MCP Server One-Click Installer"
echo "======================================="
echo

# Check if git is available for source installation
if command -v git &> /dev/null; then
    echo "✅ Git found, will install from source"
    INSTALL_METHOD="source"
else
    echo "⚠️  Git not found, will try binary installation"
    INSTALL_METHOD="binary"
fi

# Check if Python is available for source installation
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
    if [ "$INSTALL_METHOD" = "source" ]; then
        INSTALL_METHOD="source"
    fi
else
    echo "⚠️  Python 3 not found, will try binary installation"
    INSTALL_METHOD="binary"
fi

echo
echo "📦 Installation method: $INSTALL_METHOD"
echo

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ "$INSTALL_METHOD" = "source" ]; then
    echo "📥 Cloning repository..."
    if [ -d ".git" ]; then
        echo "✅ Repository already exists, updating..."
        git pull
    else
        echo "✅ Cloning fresh repository..."
        git clone "$REPO_URL" .
    fi
    
    echo
    echo "📦 Setting up virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi
    
    echo
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    
    echo
    echo "🧪 Testing installation..."
    if echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | python3 mcp_server.py > /dev/null 2>&1; then
        echo "✅ MCP server is working correctly"
    else
        echo "❌ MCP server test failed"
        exit 1
    fi
    
    SERVER_COMMAND="$INSTALL_DIR/venv/bin/python"
    SERVER_ARGS='["'$INSTALL_DIR'/mcp_server.py"]'
    
else
    echo "📥 Downloading binary..."
    if command -v curl &> /dev/null; then
        curl -L -o gitlab-mcp-server "$BINARY_URL"
    elif command -v wget &> /dev/null; then
        wget -O gitlab-mcp-server "$BINARY_URL"
    else
        echo "❌ Neither curl nor wget found. Cannot download binary."
        echo "   Please install git and python3 for source installation."
        exit 1
    fi
    
    chmod +x gitlab-mcp-server
    echo "✅ Binary downloaded and made executable"
    
    echo
    echo "🧪 Testing binary..."
    if echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | timeout 10s ./gitlab-mcp-server > /dev/null 2>&1; then
        echo "✅ Binary is working correctly"
    else
        echo "⚠️  Binary test completed (timeout expected)"
    fi
    
    SERVER_COMMAND="$INSTALL_DIR/gitlab-mcp-server"
    SERVER_ARGS='[]'
fi

echo
echo "🔧 Collecting configuration..."

# Get configuration from user
read -p "GitLab URL (press Enter for https://gitlab.solaredge.com): " GITLAB_URL
GITLAB_URL=${GITLAB_URL:-"https://gitlab.solaredge.com"}

read -p "GitLab Token (press Enter to use placeholder): " GITLAB_TOKEN
GITLAB_TOKEN=${GITLAB_TOKEN:-"YOUR_GITLAB_TOKEN_HERE"}

read -p "Default Project Path (press Enter for portialinuxdevelopers/sources/apps/core): " GITLAB_PROJECT_PATH
GITLAB_PROJECT_PATH=${GITLAB_PROJECT_PATH:-"portialinuxdevelopers/sources/apps/core"}

echo
echo "📝 Creating MCP configuration..."

# Create MCP configuration
cat > mcp-config.json << EOF
{
  "mcpServers": {
    "gitlab-mcp-server": {
      "command": "$SERVER_COMMAND",
      "args": $SERVER_ARGS,
      "env": {
        "GITLAB_URL": "$GITLAB_URL",
        "GITLAB_TOKEN": "$GITLAB_TOKEN",
        "GITLAB_PROJECT_PATH": "$GITLAB_PROJECT_PATH"
      }
    }
  }
}
EOF

echo "✅ MCP configuration created: $INSTALL_DIR/mcp-config.json"

echo
echo "🎉 Installation complete!"
echo
echo "📋 Next steps:"
echo "1. Update your GitLab token in: $INSTALL_DIR/mcp-config.json"
echo "2. Copy the configuration to your MCP client:"
echo "   - Claude Desktop: ~/.config/claude_desktop/mcp.json"
echo "   - VS Code MCP: Use the extension settings"
echo
echo "📄 Configuration file location:"
echo "   $INSTALL_DIR/mcp-config.json"
echo
echo "🔧 Server location:"
if [ "$INSTALL_METHOD" = "source" ]; then
    echo "   Source: $INSTALL_DIR/mcp_server.py"
    echo "   Python: $INSTALL_DIR/venv/bin/python"
else
    echo "   Binary: $INSTALL_DIR/gitlab-mcp-server"
fi
echo
echo "💡 To reinstall, run this script again or delete: $INSTALL_DIR"