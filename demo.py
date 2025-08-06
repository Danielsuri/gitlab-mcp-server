#!/usr/bin/env python3
"""
Demonstration script for inline comment functionality
This script shows how to use the new tools for adding inline comments to GitLab MRs
"""

import json
import subprocess
import sys

def call_mcp_tool(tool_name, arguments):
    """Call an MCP tool and return the result"""
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        # Use timeout to prevent hanging
        result = subprocess.run(
            ["python3", "mcp_server.py"],
            input=json.dumps(message),
            text=True,
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response
        else:
            return {"error": f"Process failed: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"error": "Tool call timed out"}
    except Exception as e:
        return {"error": f"Failed to call tool: {e}"}

def main():
    print("GitLab MCP Server - Inline Comment Demonstration")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1. Listing available tools...")
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    try:
        result = subprocess.run(
            ["python3", "mcp_server.py"],
            input=json.dumps(message),
            text=True,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            tools = response.get("result", {}).get("tools", [])
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Test 2: Hello World
    print("\n2. Testing hello_world tool...")
    result = call_mcp_tool("hello_world", {})
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        content = result.get("result", {}).get("content", [])
        if content:
            print(f"Response: {content[0]['text']}")
    
    print("\n3. Example usage for inline comments:")
    print("\nTo get commentable lines:")
    print('call_mcp_tool("get_merge_request_commentable_lines", {')
    print('    "project_path": "your/project",')
    print('    "mr_iid": 123')
    print('})')
    
    print("\nTo add an inline comment:")
    print('call_mcp_tool("add_merge_request_inline_comment", {')
    print('    "project_path": "your/project",')
    print('    "mr_iid": 123,')
    print('    "file_path": "src/main.py",')
    print('    "line_number": 15,')
    print('    "comment_body": "This needs optimization",')
    print('    "line_type": "new"')
    print('})')
    
    print("\nNote: For the actual commenting to work, you need:")
    print("1. Valid GITLAB_TOKEN environment variable")
    print("2. GITLAB_URL environment variable (optional, defaults to https://gitlab.solaredge.com)")
    print("3. Access to the specified GitLab project")
    print("4. A valid merge request with changes")

if __name__ == "__main__":
    main()