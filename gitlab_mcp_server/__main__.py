#!/usr/bin/env python3
"""
Entry point for running the GitLab MCP server as a module.
"""

def main():
    """Entry point function for the package."""
    from .server import main as server_main
    server_main()

if __name__ == "__main__":
    main()