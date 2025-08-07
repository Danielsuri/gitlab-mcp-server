#!/bin/bash
# Docker-based build script for Ubuntu 20.04 compatibility
# Usage: ./build-ubuntu20.04-docker.sh

set -e

echo "Building GitLab MCP Server for Ubuntu 20.04 using Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not accessible"
    echo "Please start Docker and try again"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.ubuntu20.04 -t gitlab-mcp-builder-ubuntu20.04 .

# Create output directory
mkdir -p dist-ubuntu20.04

# Run the container and extract the binary
echo "Extracting compiled binary..."
docker run --rm -v "$(pwd)/dist-ubuntu20.04:/output" gitlab-mcp-builder-ubuntu20.04

# Verify the binary was created
if [ -f "dist-ubuntu20.04/gitlab-mcp-server-ubuntu20.04" ]; then
    echo "✅ Build successful!"
    echo "Binary location: $(pwd)/dist-ubuntu20.04/gitlab-mcp-server-ubuntu20.04"
    echo "File info:"
    file dist-ubuntu20.04/gitlab-mcp-server-ubuntu20.04
    ls -lh dist-ubuntu20.04/gitlab-mcp-server-ubuntu20.04
else
    echo "❌ Build failed - binary not found"
    exit 1
fi

echo ""
echo "To test the binary on Ubuntu 20.04:"
echo "  ./dist-ubuntu20.04/gitlab-mcp-server-ubuntu20.04"
