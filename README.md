# Private GitLab MCP Server

[![One-Click Install](https://img.shields.io/badge/One--Click-Install-green?style=for-the-badge&logo=download)](https://raw.githubusercontent.com/Danielsuri/gitlab-mcp-server/main/install-oneclick.sh)

A Model Context Protocol (MCP) server for fetching GitLab merge request diffs from your private GitLab instance.

## Quick Installation

### 🚀 One-Click Full Install

Run this single command to download, install, and configure everything automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/Danielsuri/gitlab-mcp-server/main/install-oneclick.sh | bash
```

**Or download and run the script:**

```bash
wget https://raw.githubusercontent.com/Danielsuri/gitlab-mcp-server/main/install-oneclick.sh
chmod +x install-oneclick.sh
./install-oneclick.sh
```

This script will:
- ✅ Download the repository or binary automatically
- ✅ Set up virtual environment and dependencies (if using source)
- ✅ Create MCP configuration file
- ✅ Guide you through GitLab token setup

### 🖥️ VS Code MCP Integration

After running the one-click installer above, you can use this VS Code link to quickly add the server to VS Code MCP extension:

**[Add to VS Code MCP](vscode:mcp/install?%7B%22name%22%3A%20%22gitlab-mcp-server%22%2C%20%22displayName%22%3A%20%22GitLab%20MCP%20Server%22%2C%20%22repository%22%3A%20%22https%3A//github.com/Danielsuri/gitlab-mcp-server%22%2C%20%22command%22%3A%20%22python3%22%2C%20%22args%22%3A%20%5B%22mcp_server.py%22%5D%2C%20%22env%22%3A%20%7B%22GITLAB_URL%22%3A%20%22https%3A//gitlab.solaredge.com%22%2C%20%22GITLAB_TOKEN%22%3A%20%22YOUR_GITLAB_TOKEN_HERE%22%2C%20%22GITLAB_PROJECT_PATH%22%3A%20%22portialinuxdevelopers/sources/apps/core%22%7D%7D)**

> **Important:** The VS Code link only adds configuration - you still need to run the one-click installer above first to download the actual server files.

### 🔧 Automated Setup Script

For an interactive installation experience:

```bash
git clone https://github.com/Danielsuri/gitlab-mcp-server.git
cd gitlab-mcp-server
python3 install.py
```

**Or use the all-in-one setup script:**

```bash
git clone https://github.com/Danielsuri/gitlab-mcp-server.git
cd gitlab-mcp-server
./setup.sh
```

This will automatically handle virtual environment setup, dependency installation, and interactive configuration.

## Manual Setup Instructions

### 1. Install Dependencies

First, create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure GitLab Access

You need to set up your GitLab personal access token and URL:

1. **Get your GitLab Personal Access Token:**
   - Go to your GitLab instance (e.g., https://gitlab.solaredge.com)
   - Navigate to User Settings → Access Tokens
   - Create a new token with `read_api` scope
   - Copy the generated token

2. **Update the configuration:**
   - Open `mcp.json`
   - Replace `YOUR_GITLAB_TOKEN_HERE` with your actual GitLab token
   - Update the `GITLAB_URL` if you're using a different GitLab instance (default is `https://gitlab.solaredge.com`)

### 3. Configure MCP Client

Add the server configuration to your MCP client (e.g., Claude Desktop):

Copy the contents of `mcp.json` to your MCP client configuration file.

**For Claude Desktop:**
- On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Make sure to update the `cwd` path in the configuration to match your actual project directory.

## Available Tools

### `hello_world`
Returns a friendly hello message to test the connection.

### `fetch_merge_request_diff`
Fetches the diff of a GitLab merge request.

**Parameters:**
- `project_path` (string): The GitLab project path (e.g., "group/subgroup/project")
- `mr_iid` (integer): The merge request IID (internal ID)

**Example usage:**
```json
{
  "project_path": "portialinuxdevelopers/sources/apps/core",
  "mr_iid": 9045
}
```

### `get_merge_request_commentable_lines`
Gets a list of lines that can be commented on in a merge request diff. This is useful to identify valid line numbers before adding inline comments.

**Parameters:**
- `project_path` (string): The GitLab project path (e.g., "group/subgroup/project")
- `mr_iid` (integer): The merge request IID (internal ID)

**Returns:**
A list of files with their commentable lines, including:
- `type`: "new" for added lines, "old" for removed lines
- `line_number`: The line number in the file
- `content`: The actual line content

### `add_merge_request_inline_comment`
Adds an inline comment to a specific line in a merge request diff. Only lines that have been changed (added or removed) can be commented on.

**Parameters:**
- `project_path` (string): The GitLab project path
- `mr_iid` (integer): The merge request IID
- `file_path` (string): Path to the file in the diff
- `line_number` (integer): Line number to comment on (use `get_merge_request_commentable_lines` to find valid lines)
- `comment_body` (string): The comment text
- `line_type` (string, optional): "new" for added lines or "old" for removed lines (default: "new")

**Example usage:**
```json
{
  "project_path": "group/project",
  "mr_iid": 123,
  "file_path": "src/main.py",
  "line_number": 15,
  "comment_body": "This function could be optimized",
  "line_type": "new"
}
```

## Testing

You can test the server manually:

```bash
# Test hello world
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "hello_world", "arguments": {}}}' | python3 mcp_server.py

# Test merge request diff fetch
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "fetch_merge_request_diff", "arguments": {"project_path": "your/project/path", "mr_iid": 123}}}' | python3 mcp_server.py

# Test getting commentable lines
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_merge_request_commentable_lines", "arguments": {"project_path": "your/project/path", "mr_iid": 123}}}' | python3 mcp_server.py

# Test adding an inline comment (requires valid GitLab credentials)
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add_merge_request_inline_comment", "arguments": {"project_path": "your/project/path", "mr_iid": 123, "file_path": "src/main.py", "line_number": 15, "comment_body": "Test comment"}}}' | python3 mcp_server.py
```

### Running Unit Tests

```bash
# Test diff parsing functionality
python3 test_diff_parsing.py
```

## Troubleshooting

- **Connection issues**: Make sure you're connected to the VPN if your GitLab instance requires it
- **401 Unauthorized**: Check that your GitLab token is valid and has the correct permissions
- **404 Project Not Found**: Verify the project path is correct and you have access to the project
