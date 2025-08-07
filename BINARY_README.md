# GitLab MCP Server - Binary Distribution

## Quick Start with Pre-built Binaries

The GitLab MCP Server provides pre-built binaries for multiple platforms built automatically using GitHub Actions.

### Download Pre-built Binaries

**Recommended**: Download pre-built binaries from GitHub Actions:

1. **Visit GitHub Actions**: https://github.com/Danielsuri/gitlab-mcp-server/actions/workflows/build-binaries.yml
2. **Click on latest successful run** (green checkmark)
3. **Download the artifact** for your platform:
   - `gitlab-mcp-server-linux` - Ubuntu/Linux x86_64
   - `gitlab-mcp-server-macos` - macOS (Intel & Apple Silicon)
   - `gitlab-mcp-server-windows.exe` - Windows x86_64

### Manual Build (Optional)

If you prefer to build locally:

```bash
# Setup environment
python3 -m venv venv
./venv/bin/python3.13 -m pip install -r requirements.txt
./venv/bin/python3.13 -m pip install pyinstaller

# Build binary
./build_binary.sh
```

### Using the Binary

**Ubuntu/Linux Configuration** (`mcp-ubuntu.json`):
```json
{
  "mcpServers": {
    "private-gitlab": {
      "command": "./gitlab-mcp-server-linux",
      "args": [],
      "env": {
        "GITLAB_URL": "https://gitlab.solaredge.com",
        "GITLAB_TOKEN": "YOUR_GITLAB_TOKEN_HERE"
      }
    }
  }
}
```

**macOS Configuration** (`mcp-binary.json`):
```json
{
  "mcpServers": {
    "private-gitlab": {
      "command": "/Users/danielsurizon/Projects/gitlab-mcp/gitlab-mcp-server-macos",
      "args": [],
      "env": {
        "GITLAB_URL": "https://gitlab.solaredge.com",
        "GITLAB_TOKEN": "YOUR_GITLAB_TOKEN_HERE"
      }
    }
  }
}
```

### Installation Steps

1. **Download binary** from GitHub Actions artifacts
2. **Make executable** (Linux/macOS only):
   ```bash
   chmod +x gitlab-mcp-server-linux  # or gitlab-mcp-server-macos
   ```
3. **Test the binary**:
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | ./gitlab-mcp-server-linux
   ```
4. **Update MCP configuration** with the correct path to your binary

### Environment Variables

- `GITLAB_URL`: Your GitLab instance URL (default: "https://gitlab.solaredge.com")
- `GITLAB_TOKEN`: Your GitLab personal access token with `read_api` scope

### Available Tools

1. **hello_world** - Returns a friendly greeting
2. **fetch_merge_request_diff** - Fetches GitLab merge request diff
3. **add_merge_request_inline_comment** - Adds inline comments to MR diffs
4. **get_merge_request_commentable_lines** - Gets commentable lines in MR diffs  
5. **add_merge_request_general_comment** - Adds general comments to MRs

### Binary Details

- **Ubuntu/Linux**: Built on Ubuntu 20.04 (GLIBC 2.31 compatibility)
- **macOS**: Universal binary (Intel & Apple Silicon)
- **Windows**: x86_64 executable
- **Size**: ~11MB per binary
- **Dependencies**: None (self-contained)

### Troubleshooting

**GLIBC Version Error** (Linux):
- The Linux binary is built on Ubuntu 20.04 for maximum compatibility
- If you encounter GLIBC errors, your system may be older than Ubuntu 20.04
- Consider building locally or updating your system

**Permission Denied** (Linux/macOS):
```bash
chmod +x gitlab-mcp-server-linux  # or gitlab-mcp-server-macos
```

**Binary Not Found**:
- Use absolute paths in MCP configuration
- Verify the binary downloaded correctly and is in the expected location
