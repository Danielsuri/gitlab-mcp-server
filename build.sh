#!/bin/bash

# Build script for creating binary-only GitLab MCP Server wheel
# This script compiles Python source to binary extensions and packages them

set -e  # Exit on any error

echo "🔧 Starting binary wheel build process..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" || ! -d "gitlab_mcp_server" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Clean previous builds
print_status "Cleaning previous build artifacts..."
rm -rf build/ dist/ *.egg-info/
find . -name "*.so" -delete
find . -name "*.pyd" -delete
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install build dependencies
print_status "Installing build dependencies..."
pip install --upgrade pip
pip install build wheel Cython>=3.0 setuptools>=64

# Install runtime dependencies
print_status "Installing runtime dependencies..."
pip install -r requirements.txt

# Build the binary wheel
print_status "Building binary wheel with Cython compilation..."
python -m build --wheel

# Verify the wheel contents
print_status "Verifying wheel contents..."
wheel_file=$(find dist/ -name "*.whl" | head -1)

if [[ -n "$wheel_file" ]]; then
    print_status "Successfully built wheel: $(basename "$wheel_file")"
    
    # Show wheel contents
    echo "📦 Wheel contents:"
    python -m zipfile -l "$wheel_file" | grep -E "\.(so|pyd|py)$" || print_warning "No compiled extensions found in wheel"
    
    # Check if source files are excluded (should only see __init__.py and compiled extensions)
    py_files=$(python -m zipfile -l "$wheel_file" | grep "\.py$" | grep -v "__init__.py" | wc -l)
    if [[ $py_files -eq 0 ]]; then
        print_status "Binary-only wheel created successfully (no source .py files included)"
    else
        print_warning "Warning: Found $py_files source .py files in wheel"
    fi
    
    # Show compiled extensions
    so_files=$(python -m zipfile -l "$wheel_file" | grep -E "\.(so|pyd)$" | wc -l)
    if [[ $so_files -gt 0 ]]; then
        print_status "Found $so_files compiled extension(s)"
    else
        print_error "No compiled extensions found! Build may have failed."
        exit 1
    fi
    
else
    print_error "Wheel build failed - no wheel file found in dist/"
    exit 1
fi

# Test installation in a clean environment
print_status "Testing wheel installation..."
temp_venv=$(mktemp -d)
python3 -m venv "$temp_venv"
source "$temp_venv/bin/activate"

# Install the wheel
pip install "$wheel_file"

# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python -m gitlab_mcp_server > /tmp/test_output.json
if grep -q "hello_world" /tmp/test_output.json; then
    print_status "Wheel installation and basic functionality test passed!"
else
    print_error "Wheel functionality test failed"
    cat /tmp/test_output.json
    exit 1
fi

# Cleanup test environment
deactivate
rm -rf "$temp_venv"
rm -f /tmp/test_output.json

# Reactivate main environment
source venv/bin/activate

print_status "Build complete! Wheel is ready at: $wheel_file"
echo ""
echo "📋 Installation instructions:"
echo "  pip install $wheel_file"
echo ""
echo "🚀 To publish to GitHub Packages:"
echo "  export TWINE_USERNAME=__token__"
echo "  export TWINE_PASSWORD=<your-github-token>"
echo "  export TWINE_REPOSITORY_URL=https://upload.pypi.org/legacy/"
echo "  twine upload --repository-url https://upload.pypi.org/legacy/ $wheel_file"