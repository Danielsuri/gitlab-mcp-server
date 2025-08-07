#!/bin/bash

# Build GitLab MCP Server for Ubuntu 20.04 using Docker

set -e

echo "Building GitLab MCP Server for Ubuntu 20.04..."

# Build the Docker image
docker build -t gitlab-mcp-builder .

# Create a container and copy the binary out
echo "Extracting binary..."
docker create --name temp-container gitlab-mcp-builder
docker cp temp-container:/app/dist/gitlab-mcp-server ./gitlab-mcp-server-ubuntu
docker rm temp-container

echo "Build complete! Binary available as: gitlab-mcp-server-ubuntu"
echo "You can test it with:"
echo "  ./gitlab-mcp-server-ubuntu"
echo ""
echo "Or copy to Ubuntu 20.04 system and run with environment variables:"
echo "  GITLAB_URL=https://your-gitlab.com GITLAB_TOKEN=your-token GITLAB_PROJECT_PATH=your/project ./gitlab-mcp-server-ubuntu"
