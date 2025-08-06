# Private GitLab MCP Server

A Model Context Protocol (MCP) server for fetching GitLab merge request diffs from your private GitLab instance.

## Setup Instructions

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

### `comment_merge_request`
Posts a comment on a GitLab merge request.

**Parameters:**
- `project_path` (string): The GitLab project path (e.g., "group/subgroup/project")
- `mr_iid` (integer): The merge request IID (internal ID)
- `comment` (string): The comment text to post

**Example usage:**
```json
{
  "project_path": "portialinuxdevelopers/sources/apps/core",
  "mr_iid": 9045,
  "comment": "This looks good to me! LGTM 👍"
}
```

## Testing

You can test the server manually:

```bash
# Test hello world
echo '{"type":"tools/call","name":"hello_world","params":{}}' | ./mcp_server.py

# Test merge request diff fetch
echo '{"type":"tools/call","name":"fetch_merge_request_diff","params":{"project_path":"your/project/path","mr_iid":123}}' | ./mcp_server.py

# Test merge request comment
echo '{"type":"tools/call","name":"comment_merge_request","params":{"project_path":"your/project/path","mr_iid":123,"comment":"Great work!"}}' | ./mcp_server.py
```

## Troubleshooting

- **Connection issues**: Make sure you're connected to the VPN if your GitLab instance requires it
- **401 Unauthorized**: Check that your GitLab token is valid and has the correct permissions
- **404 Project Not Found**: Verify the project path is correct and you have access to the project
