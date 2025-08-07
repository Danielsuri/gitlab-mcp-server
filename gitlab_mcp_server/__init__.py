"""
GitLab MCP Server Package

A Model Context Protocol (MCP) server for fetching GitLab merge request diffs
from private GitLab instances.
"""

__version__ = "0.1.0"
__author__ = "Danielsuri"
__description__ = "Private GitLab MCP Server for fetching merge request diffs"

from .server import main

def run():
    """Entry point for console script."""
    main()

__all__ = ["main", "run", "__version__"]