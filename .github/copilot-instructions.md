# GitLab MCP Server

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

GitLab MCP Server is a Python-based Model Context Protocol (MCP) server that provides tools for fetching GitLab merge request diffs from private GitLab instances. The server implements the MCP protocol specification and can be integrated with MCP clients like Claude Desktop.

## Working Effectively

### Bootstrap and Setup
Run these commands in sequence to set up the development environment:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   - Takes under 5 seconds. NEVER CANCEL.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   - Takes 10-30 seconds depending on network. NEVER CANCEL. Set timeout to 300+ seconds.
   - **Network Issues**: If pip install fails with timeout errors, the system may have network connectivity issues to PyPI. In such cases, you can still proceed with system Python dependencies if available, but virtual environment is strongly recommended for production use.

3. **Verify installation:**
   ```bash
   python3 -m py_compile mcp_server.py test_mcp_server.py
   ```
   - Takes under 2 seconds. NEVER CANCEL.

### Running the Server

**Main MCP Server (Production):**
```bash
source venv/bin/activate
python3 mcp_server.py
# OR directly executable:
./mcp_server.py
```

**Test Server (Development):**
```bash
source venv/bin/activate
python3 test_mcp_server.py
# OR directly executable:
./test_mcp_server.py
```

Both servers support standard input/output communication for MCP protocol messages.

### Testing and Validation

**ALWAYS run these validation steps after making changes:**

1. **Test syntax compilation:**
   ```bash
   source venv/bin/activate
   python3 -m py_compile mcp_server.py test_mcp_server.py
   ```
   - Takes under 2 seconds. NEVER CANCEL.

2. **Test basic functionality:**
   ```bash
   source venv/bin/activate
   echo '{"type":"tools/call","name":"hello_world","params":{}}' | python3 test_mcp_server.py
   ```
   - Should return: `{"type": "tools/call_result", "result": "Hello from your Private GitLab MCP!"}`
   - Takes under 1 second. NEVER CANCEL.

3. **Test main server initialization:**
   ```bash
   source venv/bin/activate
   echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | python3 mcp_server.py
   ```
   - Should return initialization response with server info.
   - Takes under 1 second. NEVER CANCEL.

4. **Test GitLab functionality (requires credentials):**
   ```bash
   source venv/bin/activate
   GITLAB_URL="https://your-gitlab.com" GITLAB_TOKEN="your-token" echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "fetch_merge_request_diff", "arguments": {"project_path": "group/project", "mr_iid": 123}}}' | python3 mcp_server.py
   ```
   - Without credentials, should return connection error (expected).
   - With valid credentials, should return merge request diff data.
   - Takes 1-5 seconds depending on network. NEVER CANCEL. Set timeout to 30+ seconds.

## Manual Validation Scenarios

**CRITICAL**: After making changes, ALWAYS run through these complete end-to-end scenarios to ensure functionality:

### Scenario 1: Basic MCP Server Functionality
1. Start fresh with a clean virtual environment
2. Install dependencies and verify compilation
3. Test hello_world tool execution: should return success message
4. Test main server initialization: should return protocol info
5. **Expected time**: 2-5 minutes total

### Scenario 2: Error Handling Validation  
1. Test GitLab functionality without valid credentials
2. Verify server returns proper error messages (not crashes)
3. Test with malformed JSON input
4. **Expected behavior**: Graceful error responses, no server crashes

### Scenario 3: Network Connectivity Testing
1. Test with various network conditions (timeouts, DNS failures)
2. Verify error messages are descriptive and actionable
3. **Expected behavior**: Clear error messages indicating network issues

## Configuration

### Environment Variables
- `GITLAB_URL` - GitLab instance URL (default: "https://gitlab.example.com")
- `GITLAB_TOKEN` - GitLab personal access token with `read_api` scope

### MCP Client Configuration
Update the `mcp.json` file with:
- Correct `cwd` path pointing to this directory
- Valid `GITLAB_URL` and `GITLAB_TOKEN` in the `env` section

## Project Structure

### Key Files
- `mcp_server.py` - Main MCP server implementation (executable, full JSON-RPC 2.0 protocol)
- `test_mcp_server.py` - Test server implementation (executable, simplified protocol)
- `requirements.txt` - Python dependencies (certifi, charset-normalizer, idna, requests, urllib3)
- `mcp.json` - MCP client configuration template
- `README.md` - User documentation

### Available Tools
1. **hello_world** - Returns a friendly greeting (no parameters)
2. **fetch_merge_request_diff** - Fetches GitLab merge request diff
   - Parameters: `project_path` (string), `mr_iid` (integer)

## Common Tasks

The following are outputs from frequently run commands. Reference them instead of viewing, searching, or running bash commands to save time.

### Repository Root Structure
```
ls -la /path/to/gitlab-mcp-server
.
..
.git/
.github/
README.md
mcp.json
mcp_server.py
requirements.txt
test_mcp_server.py
```

### Key Dependencies
```
cat requirements.txt
certifi==2025.8.3
charset-normalizer==3.4.2
idna==3.10
requests==2.32.4
urllib3==2.5.0
```

### Testing Without Network Access
The server gracefully handles network errors. Test with fake credentials to verify error handling:
```bash
GITLAB_URL="https://example.com" GITLAB_TOKEN="fake-token" echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "fetch_merge_request_diff", "arguments": {"project_path": "test/project", "mr_iid": 1}}}' | python3 mcp_server.py
```

### Development Workflow
1. Make changes to Python files
2. Run syntax compilation check: `python3 -m py_compile mcp_server.py test_mcp_server.py`
3. Test with hello_world tool: `echo '{"type":"tools/call","name":"hello_world","params":{}}' | ./test_mcp_server.py`
4. Test initialization protocol: `echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0"}}}' | ./mcp_server.py`
5. Test GitLab functionality if credentials available
6. **Always run all validation scenarios** before considering changes complete

### Alternative: System Python Usage
If virtual environment setup fails due to network issues, the scripts can run with system Python (if compatible dependencies are installed):
```bash
# Direct execution (no venv activation needed)
./test_mcp_server.py
./mcp_server.py
```

### File Permissions
Both `mcp_server.py` and `test_mcp_server.py` are executable with proper shebangs (`#!/usr/bin/env python3`).

## Timing Expectations

All operations are very fast in this project:
- **Virtual environment creation**: < 5 seconds
- **Dependency installation**: 10-30 seconds (normal network) / may timeout on slow networks
- **Python compilation check**: < 2 seconds  
- **Server startup and basic operations**: < 1 second
- **GitLab API calls**: 1-5 seconds (network dependent)
- **Complete validation workflow**: 2-5 minutes total

**CRITICAL TIMEOUT VALUES:**
- Virtual environment setup: 60+ seconds timeout
- pip install: 300+ seconds timeout (network dependent)  
- All other operations: 30+ seconds timeout
- GitLab API calls: 60+ seconds timeout (network dependent)

**NEVER CANCEL any operation** - they complete quickly, but allow generous timeouts for network dependencies.

## Troubleshooting

### Common Issues
- **pip install timeout**: Network connectivity issues to PyPI. Try with longer timeout or check network connection.
- **GitLab connection errors**: Expected behavior when testing without valid credentials. Verify GITLAB_URL and GITLAB_TOKEN for real usage.
- **Permission denied on scripts**: Ensure mcp_server.py and test_mcp_server.py have execute permissions (`chmod +x *.py`).

### Network Dependencies
- PyPI access required for fresh dependency installation
- GitLab instance access required for production functionality
- DNS resolution needed for both PyPI and GitLab URLs

## System Requirements

- Python 3.12+ (tested with 3.12.3)
- Network access to GitLab instance (for production use)
- Valid GitLab personal access token with `read_api` scope

## Notes

- The project has minimal dependencies and no complex build system
- No linting tools are configured (flake8, pytest not included)
- No CI/CD pipelines configured
- Both servers handle JSON protocol communication via stdin/stdout
- System Python may have compatible dependencies, but virtual environment is recommended
- Error handling is implemented for network failures and invalid requests