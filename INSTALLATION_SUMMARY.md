# Installation Files Summary

This directory contains multiple installation methods for the GitLab MCP Server:

## Files Overview

### Configuration Files
- **`mcp-manifest.json`** - Server metadata and capabilities for MCP registries
- **`mcp.json`** - Template MCP client configuration

### Installation Scripts
- **`install-oneclick.sh`** - Complete one-click installation script (downloads repo, sets up everything)
- **`install.py`** - Interactive Python installation script  
- **`setup.sh`** - All-in-one shell setup script (requires manual repo clone first)

### Build and Deployment
- **`build-docker.sh`** - Docker-based build script for standalone binary
- **`.github/workflows/build.yml`** - GitHub Actions workflow for automated builds

### Documentation
- **`README.md`** - Main documentation with quick install options
- **`INSTALL.md`** - Comprehensive installation guide
- **`install.html`** - Web-based installation interface with custom URL generator

## Installation Methods

### 1. One-Click Full Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/Danielsuri/gitlab-mcp-server/main/install-oneclick.sh | bash
```
**Features:**
- ✅ Downloads repository or binary automatically
- ✅ Sets up virtual environment and dependencies  
- ✅ Creates MCP configuration file
- ✅ Handles both source and binary installations
- ✅ Installs to `~/.mcp/gitlab-mcp-server/`

### 2. VS Code MCP Integration
After using method 1, use this VS Code link:
```
vscode:mcp/install?[encoded-configuration]
```
**Note:** Only adds configuration - requires actual files from method 1 first.

### 3. Manual Repository Clone + Automated Setup
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