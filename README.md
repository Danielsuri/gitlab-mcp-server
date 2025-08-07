# Private GitLab MCP Server

A Model Context Protocol (MCP) server for fetching GitLab merge request diffs from your private GitLab instance.

## Installation

### Binary Package (Recommended)

Install the pre-compiled binary package from GitHub Packages:

```bash
pip install --extra-index-url https://pypi.pkg.github.com/Danielsuri/ gitlab-mcp-server
```

The binary package provides:
- ✅ **Source code protection**: No Python source files included
- ✅ **Fast startup**: Pre-compiled C extensions
- ✅ **Easy installation**: Single pip command
- ✅ **Cross-platform**: Wheels available for Python 3.8-3.12

### From Source (Development)

For development or if you prefer to build from source:

### 1. Install Dependencies

First, create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Using the Binary Package

After installing the binary package, you can use the server directly:

```bash
# Run the server
gitlab-mcp-server

# Or use it programmatically
python -c "from gitlab_mcp_server import mcp_server; mcp_server.main()"
```

### 2. Configure GitLab Access

You need to set up your GitLab personal access token and URL:

1. **Get your GitLab Personal Access Token:**
   - Go to your GitLab instance (e.g., https://gitlab.example.com)
   - Navigate to User Settings → Access Tokens
   - Create a new token with `read_api` scope
   - Copy the generated token

2. **Update the configuration:**
   - Open `mcp.json`
   - Replace `YOUR_GITLAB_TOKEN_HERE` with your actual GitLab token
   - Update the `GITLAB_URL` if you're using a different GitLab instance (default is `https://gitlab.example.com`)

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
  "project_path": "your-group/your-project",
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
