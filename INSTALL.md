# GitLab MCP Server Installation Guide

This guide provides multiple ways to install and configure the GitLab MCP Server.

## Quick Installation Options

### Option 1: One-Click Install for VS Code

**For VS Code with MCP Extension:**

Click this link to install directly:
```
vscode:mcp/install?%7B%22name%22%3A%20%22gitlab-mcp-server%22%2C%20%22displayName%22%3A%20%22GitLab%20MCP%20Server%22%2C%20%22repository%22%3A%20%22https%3A//github.com/Danielsuri/gitlab-mcp-server%22%2C%20%22command%22%3A%20%22python3%22%2C%20%22args%22%3A%20%5B%22mcp_server.py%22%5D%2C%20%22env%22%3A%20%7B%22GITLAB_URL%22%3A%20%22https%3A//gitlab.solaredge.com%22%2C%20%22GITLAB_TOKEN%22%3A%20%22YOUR_GITLAB_TOKEN_HERE%22%2C%20%22GITLAB_PROJECT_PATH%22%3A%20%22portialinuxdevelopers/sources/apps/core%22%7D%7D
```

### Option 2: Automated Setup Script

1. Clone the repository:
   ```bash
   git clone https://github.com/Danielsuri/gitlab-mcp-server.git
   cd gitlab-mcp-server
   ```

2. Run the installation script:
   ```bash
   python3 install.py
   ```

3. Follow the prompts to configure your GitLab settings.

### Option 3: Manual Configuration

1. **Clone and setup:**
   ```bash
   git clone https://github.com/Danielsuri/gitlab-mcp-server.git
   cd gitlab-mcp-server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   export GITLAB_URL="https://your-gitlab-instance.com"
   export GITLAB_TOKEN="your_gitlab_token_here"
   export GITLAB_PROJECT_PATH="your/default/project/path"
   ```

3. **Add to your MCP client configuration:**
   
   **For Claude Desktop:**
   Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):
   
   ```json
   {
     "mcpServers": {
       "gitlab-mcp-server": {
         "command": "python3",
         "args": ["mcp_server.py"],
         "cwd": "/path/to/gitlab-mcp-server",
         "env": {
           "GITLAB_URL": "https://your-gitlab-instance.com",
           "GITLAB_TOKEN": "your_gitlab_token_here",
           "GITLAB_PROJECT_PATH": "your/default/project/path"
         }
       }
     }
   }
   ```

## Configuration Details

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITLAB_URL` | Your GitLab instance URL | No | `https://gitlab.solaredge.com` |
| `GITLAB_TOKEN` | GitLab personal access token | Yes | - |
| `GITLAB_PROJECT_PATH` | Default project path | No | `portialinuxdevelopers/sources/apps/core` |

### GitLab Token Setup

1. Go to your GitLab instance
2. Navigate to User Settings → Access Tokens
3. Create a new token with `read_api` scope (and `api` scope if you want to add comments)
4. Copy the generated token and use it as `GITLAB_TOKEN`

## Verification

Test your installation:

```bash
# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | python3 mcp_server.py

# Test tools listing
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python3 mcp_server.py
```

## Troubleshooting

- **Connection issues**: Ensure you're connected to your organization's VPN if required
- **401 Unauthorized**: Verify your GitLab token is valid and has correct permissions
- **404 Project Not Found**: Check that the project path is correct and accessible
- **Python not found**: Make sure Python 3.8+ is installed and in your PATH

## Files Created

- `mcp.json` - MCP client configuration
- `mcp-manifest.json` - Server metadata and capabilities
- `install.py` - Interactive installation script