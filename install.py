#!/usr/bin/env python3
"""
GitLab MCP Server Installation Script

This script helps set up the GitLab MCP server with the necessary configuration
for MCP clients like Claude Desktop or VS Code.
"""

import json
import os
import sys
import urllib.parse
from pathlib import Path


def create_mcp_config(gitlab_url=None, gitlab_token=None, gitlab_project_path=None, install_path=None):
    """Create MCP configuration for clients"""
    
    if not install_path:
        install_path = os.getcwd()
    
    config = {
        "mcpServers": {
            "gitlab-mcp-server": {
                "command": "python3",
                "args": ["mcp_server.py"],
                "cwd": install_path,
                "env": {
                    "GITLAB_URL": gitlab_url or "https://gitlab.solaredge.com",
                    "GITLAB_TOKEN": gitlab_token or "YOUR_GITLAB_TOKEN_HERE",
                    "GITLAB_PROJECT_PATH": gitlab_project_path or "portialinuxdevelopers/sources/apps/core"
                }
            }
        }
    }
    
    return config


def generate_install_urls(config):
    """Generate VS Code and other MCP client install URLs"""
    
    # Simplified config for VS Code MCP extension
    vscode_config = {
        "name": "gitlab-mcp-server",
        "displayName": "GitLab MCP Server",
        "repository": "https://github.com/Danielsuri/gitlab-mcp-server",
        "command": config["mcpServers"]["gitlab-mcp-server"]["command"],
        "args": config["mcpServers"]["gitlab-mcp-server"]["args"],
        "env": config["mcpServers"]["gitlab-mcp-server"]["env"]
    }
    
    # URL encode the config
    encoded_config = urllib.parse.quote(json.dumps(vscode_config))
    vscode_url = f"vscode:mcp/install?{encoded_config}"
    
    return {
        "vscode": vscode_url,
        "config": vscode_config
    }


def print_installation_info(config, urls):
    """Print installation instructions"""
    
    print("=" * 60)
    print("GitLab MCP Server Installation Configuration")
    print("=" * 60)
    print()
    
    print("📋 MCP Client Configuration:")
    print("Copy this configuration to your MCP client:")
    print()
    print(json.dumps(config, indent=2))
    print()
    
    print("🔗 One-Click Install URLs:")
    print()
    print("VS Code MCP Extension:")
    print(f"  {urls['vscode']}")
    print()
    
    print("💡 Manual Installation Steps:")
    print("1. Clone this repository")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Set your GitLab token: export GITLAB_TOKEN='your_token_here'")
    print("4. Add the above configuration to your MCP client")
    print()
    
    print("📝 Configuration Files:")
    print("- MCP client config: mcp.json")
    print("- Server manifest: mcp-manifest.json")
    print()


def main():
    """Main installation function"""
    
    print("GitLab MCP Server Installation Helper")
    print("====================================")
    print()
    
    # Get configuration from user or environment
    gitlab_url = os.environ.get("GITLAB_URL") or input("GitLab URL (press Enter for default): ").strip()
    gitlab_token = os.environ.get("GITLAB_TOKEN") or input("GitLab Token (press Enter to use placeholder): ").strip()
    gitlab_project_path = os.environ.get("GITLAB_PROJECT_PATH") or input("Default Project Path (press Enter for default): ").strip()
    
    # Create configuration
    config = create_mcp_config(
        gitlab_url=gitlab_url or None,
        gitlab_token=gitlab_token or None, 
        gitlab_project_path=gitlab_project_path or None,
        install_path=os.getcwd()
    )
    
    # Generate install URLs
    urls = generate_install_urls(config)
    
    # Save configuration files
    with open("mcp.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Print installation info
    print_installation_info(config, urls)
    
    print("✅ Configuration files created successfully!")
    print("   - mcp.json (MCP client configuration)")
    print("   - Use the one-click install URL above for easy installation")


if __name__ == "__main__":
    main()