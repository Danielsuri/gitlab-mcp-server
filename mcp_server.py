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

    msg_type = msg.get("type")

    if msg_type == "initialize":
        respond({
            "type": "initialize_result",
            "protocol_version": "0.1",
            "server_info": {"name": "Private GitLab MCP", "version": "0.1"}
        })

    elif msg_type == "tools/list":
        respond({
            "type": "tools/list_result",
            "tools": [
                {
                    "name": "hello_world",
                    "description": "Returns a friendly hello message",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "fetch_merge_request_diff",
                    "description": "Fetches the diff of a given merge request for a GitLab project",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string"},
                            "mr_iid": {"type": "integer"}
                        },
                        "required": ["project_path", "mr_iid"]
                    }
                }
            ]
        })

    elif msg_type == "tools/call":
        if msg.get("name") == "hello_world":
            respond({
                "type": "tools/call_result",
                "result": "Hello from your Private GitLab MCP!"
            })
        elif msg.get("name") == "fetch_merge_request_diff":
            try:
                params = msg.get("params", {})
                project_path = params.get("project_path") or "portialinuxdevelopers/sources/apps/core"
                mr_iid = params["mr_iid"]
                result = fetch_mr_diff(project_path, mr_iid)
                respond({
                    "type": "tools/call_result",
                    "result": result
                })
            except Exception as e:
                respond({
                    "type": "error",
                    "message": f"fetch_merge_request_diff failed: {e}"
                })

    else:
        respond({"type": "error", "message": f"Unknown message type: {msg_type}"})