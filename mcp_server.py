#!/usr/bin/env python3
import sys
import json
import requests
import os
import urllib.parse
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.solaredge.com")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")


def fetch_mr_diff(project_path, mr_iid):
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/changes"
    resp = requests.get(url, headers={"PRIVATE-TOKEN": GITLAB_TOKEN})
    resp.raise_for_status()
    data = resp.json()
    # Return a clean list of file and diff only
    return [{"file": c["new_path"], "diff": c["diff"]} for c in data.get("changes", [])]


def comment_merge_request(project_path, mr_iid, comment):
    encoded_path = urllib.parse.quote_plus(project_path)
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/notes"
    data = {"body": comment}
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
                                "project_path": {"type": "string"},
                                "mr_iid": {"type": "integer"}
                            },
                            "required": ["project_path", "mr_iid"]
                        }
                    },
                    {
                        "name": "comment_merge_request",
                        "description": "Posts a comment on a GitLab merge request",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_path": {"type": "string"},
                                "mr_iid": {"type": "integer"},
                                "comment": {"type": "string"}
                            },
                            "required": ["project_path", "mr_iid", "comment"]
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
                project_path = params.get("project_path") or "portialinuxdevelopers/sources/apps/core"
                mr_iid = params["mr_iid"]
                result = fetch_mr_diff(project_path, mr_iid)
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
        elif msg.get("params", {}).get("name") == "comment_merge_request":
            try:
                params = msg.get("params", {}).get("arguments", {})
                project_path = params["project_path"]
                mr_iid = params["mr_iid"]
                comment = params["comment"]
                result = comment_merge_request(project_path, mr_iid, comment)
                respond({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Comment posted successfully. Note ID: {result.get('id')}"
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
                        "message": f"comment_merge_request failed: {e}"
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