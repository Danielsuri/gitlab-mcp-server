#!/bin/bash

# GitLab MCP Server Installer - Public Script
# This script provides installation instructions for the private repository

set -e

echo "🚀 GitLab MCP Server Installer"
echo "=============================="
echo
echo "⚠️  This is a private repository installer."
echo "   You need to have access to the repository first."
echo
echo "📋 Installation Steps:"
echo
echo "1️⃣  Clone the repository:"
echo "   git clone https://github.com/Danielsuri/gitlab-mcp-server.git"
echo
echo "2️⃣  Enter the directory:"
echo "   cd gitlab-mcp-server"
echo
echo "3️⃣  Run the one-click installer:"
echo "   ./install-oneclick.sh"
echo
echo "🔐 Authentication Required:"
echo "   Make sure you have GitHub access configured:"
echo "   - SSH key: git@github.com:Danielsuri/gitlab-mcp-server.git"
echo "   - HTTPS with token: https://github.com/Danielsuri/gitlab-mcp-server.git"
echo
echo "🤔 Don't have access? Contact the repository owner for access."
echo
echo "❓ Want to try anyway? Run:"
echo "   git clone https://github.com/Danielsuri/gitlab-mcp-server.git && cd gitlab-mcp-server && ./install-oneclick.sh"