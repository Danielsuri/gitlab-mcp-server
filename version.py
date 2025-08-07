#!/usr/bin/env python3
"""
Version management utility for gitlab-mcp-server
"""
import os
import re
import sys
import argparse
from typing import Tuple

def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    pyproject_path = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    return match.group(1)

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch tuple"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version}") from e

def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple into string"""
    return f"{major}.{minor}.{patch}"

def bump_version(version: str, part: str) -> str:
    """Bump version by specified part (major, minor, patch)"""
    major, minor, patch = parse_version(version)
    
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid version part: {part}. Must be 'major', 'minor', or 'patch'")
    
    return format_version(major, minor, patch)

def update_version_in_files(new_version: str) -> None:
    """Update version in all relevant files"""
    # Update pyproject.toml
    pyproject_path = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    updated_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    with open(pyproject_path, 'w') as f:
        f.write(updated_content)
    
    # Update __init__.py
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'gitlab_mcp_server', '__init__.py')
    with open(init_path, 'r') as f:
        content = f.read()
    
    updated_content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(init_path, 'w') as f:
        f.write(updated_content)

def main():
    parser = argparse.ArgumentParser(description='Manage package version')
    parser.add_argument('action', choices=['get', 'bump'], help='Action to perform')
    parser.add_argument('--part', choices=['major', 'minor', 'patch'], 
                       help='Version part to bump (required for bump action)')
    
    args = parser.parse_args()
    
    if args.action == 'get':
        current_version = get_current_version()
        print(current_version)
    
    elif args.action == 'bump':
        if not args.part:
            print("Error: --part is required for bump action", file=sys.stderr)
            sys.exit(1)
        
        current_version = get_current_version()
        new_version = bump_version(current_version, args.part)
        update_version_in_files(new_version)
        
        print(f"Version bumped from {current_version} to {new_version}")

if __name__ == '__main__':
    main()