#!/usr/bin/env python3
import sys
import json
import requests
import os
import urllib.parse
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.solaredge.com")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
DEFAULT_PROJECT_PATH = os.environ.get("GITLAB_PROJECT_PATH", "portialinuxdevelopers/sources/apps/core")


def fetch_mr_diff(mr_iid):
    project_path = DEFAULT_PROJECT_PATH
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/changes"
    resp = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    resp.raise_for_status()
    data = resp.json()
    # Return a clean list of file and diff only
    return [{"file": c["new_path"], "diff": c["diff"]} for c in data.get("changes", [])]


def fetch_mr_details(mr_iid):
    """Fetch merge request details including diff_refs needed for inline comments"""
    project_path = DEFAULT_PROJECT_PATH
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}"
    resp = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    resp.raise_for_status()
    return resp.json()


def parse_diff_for_line_numbers(diff_content):
    """Parse diff content to extract valid line numbers for comments"""
    lines = diff_content.split('\n')
    valid_lines = []
    
    current_new_line = 0
    current_old_line = 0
    
    for line in lines:
        if line.startswith('@@'):
            # Parse hunk header to get starting line numbers
            # Format: @@ -old_start,old_count +new_start,new_count @@
            import re
            match = re.match(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
            if match:
                current_old_line = int(match.group(1))
                current_new_line = int(match.group(2))
            continue
            
        if line.startswith('+') and not line.startswith('+++'):
            # This is a new line that can be commented on
            valid_lines.append({
                'type': 'new',
                'line_number': current_new_line,
                'content': line[1:]  # Remove the + prefix
            })
            current_new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            # This is a deleted line that can be commented on
            valid_lines.append({
                'type': 'old', 
                'line_number': current_old_line,
                'content': line[1:]  # Remove the - prefix
            })
            current_old_line += 1
        elif line.startswith(' '):
            # Context line - both line numbers advance
            current_new_line += 1
            current_old_line += 1
            
    return valid_lines


def get_mr_commentable_lines(mr_iid):
    """Get a list of lines that can be commented on in a merge request"""
    project_path = DEFAULT_PROJECT_PATH
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/changes"
    resp = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    resp.raise_for_status()
    data = resp.json()
    
    result = []
    for change in data.get("changes", []):
        file_path = change["new_path"]
        diff_content = change["diff"]
        valid_lines = parse_diff_for_line_numbers(diff_content)
        
        result.append({
            "file": file_path,
            "commentable_lines": valid_lines
        })
    
    return result


def add_mr_inline_comment(mr_iid, file_path, line_number, comment_body, line_type="new"):
    """Add an inline comment to a merge request"""
    project_path = DEFAULT_PROJECT_PATH
    encoded_path = urllib.parse.quote_plus(project_path)
    
    # First, get the merge request details to extract diff_refs
    mr_details = fetch_mr_details(mr_iid)
    diff_refs = mr_details.get('diff_refs')
    
    if not diff_refs:
        raise ValueError("Could not get diff_refs from merge request")
    
    # Create the position object for the inline comment
    position = {
        'base_sha': diff_refs['base_sha'],
        'start_sha': diff_refs['start_sha'], 
        'head_sha': diff_refs['head_sha'],
        'position_type': 'text',
        'new_path': file_path
    }
    
    # Add line number based on type
    if line_type == 'new':
        position['new_line'] = line_number
    else:
        position['old_line'] = line_number
        position['old_path'] = file_path
    
    # Create the discussion
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/discussions"
    data = {
        'body': comment_body,
        'position': position
    }
    
    resp = requests.post(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN}, json=data)
    resp.raise_for_status()
    return resp.json()


def add_mr_general_comment(mr_iid, comment_body):
    """Add a general comment to a merge request"""
    project_path = DEFAULT_PROJECT_PATH
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/notes"
    data = {
        'body': comment_body
    }
    
    resp = requests.post(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN}, json=data)
    resp.raise_for_status()
    return resp.json()


def respond(obj):
    """Send a JSON response over stdout"""
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


while True:
    line = sys.stdin.readline()
    if not line:
        break

    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue  # Ignore malformed messages

    msg_type = msg.get("method")

    if msg_type == "initialize":
        respond({
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Private GitLab MCP",
                    "version": "0.1"
                }
            }
        })

    elif msg_type == "tools/list":
        respond({
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "hello_world",
                        "description": "Returns a friendly hello message",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "fetch_merge_request_diff",
                        "description": "Fetches the diff of a given merge request for a GitLab project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mr_iid": {"type": "integer"}
                            },
                            "required": ["mr_iid"]
                        }
                    },
                    {
                        "name": "add_merge_request_inline_comment",
                        "description": "Adds an inline comment to a specific line in a merge request diff",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mr_iid": {"type": "integer", "description": "Merge request IID"},
                                "file_path": {"type": "string", "description": "Path to the file in the diff"},
                                "line_number": {"type": "integer", "description": "Line number to comment on"},
                                "comment_body": {"type": "string", "description": "The comment text"},
                                "line_type": {"type": "string", "enum": ["new", "old"], "default": "new", "description": "Whether to comment on new line (added) or old line (removed)"}
                            },
                            "required": ["mr_iid", "file_path", "line_number", "comment_body"]
                        }
                    },
                    {
                        "name": "get_merge_request_commentable_lines",
                        "description": "Gets a list of lines that can be commented on in a merge request diff",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mr_iid": {"type": "integer", "description": "Merge request IID"}
                            },
                            "required": ["mr_iid"]
                        }
                    },
                    {
                        "name": "add_merge_request_general_comment",
                        "description": "Adds a general comment to a merge request (appears in Overview tab)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mr_iid": {"type": "integer", "description": "Merge request IID"},
                                "comment_body": {"type": "string", "description": "The comment text"}
                            },
                            "required": ["mr_iid", "comment_body"]
                        }
                    }
                ]
            }
        })

    elif msg_type == "tools/call":
        if msg.get("params", {}).get("name") == "hello_world":
            respond({
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "Hello from your Private GitLab MCP!"
                        }
                    ]
                }
            })
        elif msg.get("params", {}).get("name") == "fetch_merge_request_diff":
            try:
                params = msg.get("params", {}).get("arguments", {})
                mr_iid = params["mr_iid"]
                result = fetch_mr_diff(mr_iid)
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                })
            except Exception as e:
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"fetch_merge_request_diff failed: {e}"
                    }
                })
        elif msg.get("params", {}).get("name") == "add_merge_request_inline_comment":
            try:
                params = msg.get("params", {}).get("arguments", {})
                mr_iid = params.get("mr_iid")
                file_path = params.get("file_path")
                line_number = params.get("line_number")
                comment_body = params.get("comment_body")
                line_type = params.get("line_type", "new")
                
                if not all([mr_iid, file_path, line_number, comment_body]):
                    raise ValueError("Missing required parameters")
                
                result = add_mr_inline_comment(mr_iid, file_path, line_number, comment_body, line_type)
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully added inline comment to {file_path} at line {line_number}. Discussion ID: {result.get('id')}"
                            }
                        ]
                    }
                })
            except Exception as e:
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"add_merge_request_inline_comment failed: {e}"
                    }
                })
        elif msg.get("params", {}).get("name") == "get_merge_request_commentable_lines":
            try:
                params = msg.get("params", {}).get("arguments", {})
                mr_iid = params.get("mr_iid")
                
                if not mr_iid:
                    raise ValueError("Missing required parameter: mr_iid")
                
                result = get_mr_commentable_lines(mr_iid)
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                })
            except Exception as e:
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"get_merge_request_commentable_lines failed: {e}"
                    }
                })
        elif msg.get("params", {}).get("name") == "add_merge_request_general_comment":
            try:
                params = msg.get("params", {}).get("arguments", {})
                mr_iid = params.get("mr_iid")
                comment_body = params.get("comment_body")
                
                if not all([mr_iid, comment_body]):
                    raise ValueError("Missing required parameters: mr_iid and comment_body")
                
                result = add_mr_general_comment(mr_iid, comment_body)
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully added general comment to merge request {mr_iid}. Note ID: {result.get('id')}"
                            }
                        ]
                    }
                })
            except Exception as e:
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"add_merge_request_general_comment failed: {e}"
                    }
                })

    else:
        respond({
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "error": {
                "code": -32601,
                "message": f"Unknown message type: {msg_type}"
            }
        })
