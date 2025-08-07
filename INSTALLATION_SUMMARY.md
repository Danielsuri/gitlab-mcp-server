# Installation Files Summary

This directory contains multiple installation methods for the GitLab MCP Server:

## Files Overview

### Configuration Files
- **`mcp-manifest.json`** - Server metadata and capabilities for MCP registries
- **`mcp.json`** - Template MCP client configuration

### Installation Scripts
- **`install.py`** - Interactive Python installation script
- **`setup.sh`** - All-in-one shell setup script (includes venv, dependencies, and config)

### Documentation
- **`README.md`** - Main documentation with quick install options
- **`INSTALL.md`** - Comprehensive installation guide
- **`install.html`** - Web-based installation interface with custom URL generator

## Installation Methods

### 1. One-Click Install (VS Code)
Click the badge in README.md or use this URL:
```
vscode:mcp/install?[encoded-configuration]
```

### 2. Quick Setup Script
```bash
git clone https://github.com/Danielsuri/gitlab-mcp-server.git
cd gitlab-mcp-server
./setup.sh
```

### 3. Interactive Python Setup
```bash
git clone https://github.com/Danielsuri/gitlab-mcp-server.git
cd gitlab-mcp-server
python3 install.py
```

### 4. Manual Installation
Follow the detailed steps in `INSTALL.md`

### 5. Web Interface
Open `install.html` in a browser for a graphical installation experience

## Features
- ✅ One-click VS Code MCP extension integration
- ✅ Interactive configuration with sensible defaults
- ✅ Custom URL generation for different GitLab instances
- ✅ Automated dependency management
- ✅ Multiple installation paths for different user preferences
- ✅ Comprehensive documentation and guides