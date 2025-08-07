# Installation Guide - GitLab MCP Server (Binary Distribution)

This guide covers installing the GitLab MCP Server from the binary-only wheel package distributed through GitHub Packages.

## Quick Installation

### Prerequisites

- Python 3.8 or higher
- Access to this private GitHub repository
- GitHub Personal Access Token with `read:packages` permission

### Step 1: Generate GitHub Personal Access Token

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the following scopes:
   - `read:packages` (required for downloading)
   - `repo` (if repository is private)
4. Copy the generated token

### Step 2: Install the Package

**Option A: Direct installation with token**
```bash
pip install --extra-index-url https://USERNAME:TOKEN@pypi.pkg.github.com/Danielsuri gitlab-mcp-server
```

**Option B: Using pip configuration file**

Create `~/.pip/pip.conf` (Linux/Mac) or `%APPDATA%\pip\pip.ini` (Windows):
```ini
[global]
extra-index-url = https://USERNAME:TOKEN@pypi.pkg.github.com/Danielsuri
```

Then install normally:
```bash
pip install gitlab-mcp-server
```

**Option C: Using environment variables**
```bash
export PIP_EXTRA_INDEX_URL=https://USERNAME:TOKEN@pypi.pkg.github.com/Danielsuri
pip install gitlab-mcp-server
```

Replace `USERNAME` with your GitHub username and `TOKEN` with your personal access token.

## Verification

After installation, verify the package works:

```bash
# Check if console script is available
which gitlab-mcp-server

# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | gitlab-mcp-server

# Check version
python -c "import gitlab_mcp_server; print(gitlab_mcp_server.__version__)"
```

## Configuration

The binary package includes the same functionality as the source version. Configure it by setting environment variables:

```bash
export GITLAB_URL="https://your-gitlab-instance.com"
export GITLAB_TOKEN="your-gitlab-personal-access-token"
export GITLAB_PROJECT_PATH="group/project"
```

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitlab-mcp-server": {
      "command": "gitlab-mcp-server",
      "env": {
        "GITLAB_URL": "https://your-gitlab-instance.com",
        "GITLAB_TOKEN": "your-gitlab-token",
        "GITLAB_PROJECT_PATH": "group/project"
      }
    }
  }
}
```

### Other MCP Clients

For other MCP clients, use:
- **Command:** `gitlab-mcp-server` 
- **Arguments:** None (configured via environment variables)

## Troubleshooting

### Installation Issues

**Error: "No matching distribution found"**
- Verify your GitHub token has `read:packages` permission
- Check that the USERNAME:TOKEN format is correct
- Ensure you have access to the private repository

**Error: "403 Forbidden"**
- Token may be expired or lack proper permissions
- Try regenerating your GitHub Personal Access Token

### Runtime Issues

**Error: "ModuleNotFoundError"**
- Dependencies may not have installed correctly
- Try: `pip install --upgrade gitlab-mcp-server`

**Error: "gitlab-mcp-server: command not found"**
- Package may have installed in user directory
- Try: `python -m gitlab_mcp_server` instead

### Network/Connection Issues

**Error: "Connection timeout" or "Read timed out"**
- Check your network connection
- If behind corporate firewall, ensure PyPI and GitHub Packages are accessible
- Try installing with `--timeout 300` for slower connections

## Advanced Installation

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv gitlab-mcp-env
source gitlab-mcp-env/bin/activate  # Linux/Mac
# gitlab-mcp-env\Scripts\activate  # Windows

# Install package
pip install --extra-index-url https://USERNAME:TOKEN@pypi.pkg.github.com/Danielsuri gitlab-mcp-server

# Verify installation
gitlab-mcp-server --help 2>/dev/null || echo "Package installed successfully"
```

### Docker Installation

```dockerfile
FROM python:3.12-slim

# Install package
ARG GITHUB_USERNAME
ARG GITHUB_TOKEN
RUN pip install --extra-index-url https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@pypi.pkg.github.com/Danielsuri gitlab-mcp-server

# Set environment variables
ENV GITLAB_URL="https://your-gitlab-instance.com"
ENV GITLAB_TOKEN=""
ENV GITLAB_PROJECT_PATH=""

# Run server
CMD ["gitlab-mcp-server"]
```

Build and run:
```bash
docker build --build-arg GITHUB_USERNAME=your-username --build-arg GITHUB_TOKEN=your-token -t gitlab-mcp-server .
docker run -e GITLAB_TOKEN=your-gitlab-token gitlab-mcp-server
```

## Package Information

- **Package Name:** `gitlab-mcp-server`
- **Distribution:** Binary-only wheel (no source code exposed)
- **Supported Python:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Supported Platforms:** Linux x86_64 (additional platforms available on request)
- **Dependencies:** Automatically installed by pip

## Security Notes

- The binary distribution contains no source code - only compiled extensions
- All Python source files are compiled to `.so` (Linux) or `.pyd` (Windows) format
- Package dependencies are pinned to specific versions for security
- Regular security updates are provided through new releases

## Support

For installation issues or questions:
1. Check this installation guide
2. Review the troubleshooting section
3. Create an issue in the repository with:
   - Python version (`python --version`)
   - Operating system
   - Complete error message
   - Installation command used