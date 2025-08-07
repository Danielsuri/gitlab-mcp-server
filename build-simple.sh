#!/bin/bash

# Simple build script for creating binary-only GitLab MCP Server wheel
set -e

echo "🔧 Building binary wheel..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check environment
if [[ ! -d "venv" ]]; then
    print_error "Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# Clean previous builds
print_status "Cleaning build artifacts..."
rm -rf build/ dist/ *.egg-info/
find . -name "*.so" -delete
find . -name "*.pyd" -delete

# Build Cython extensions
print_status "Compiling Python code with Cython..."
python setup.py build_ext --inplace

# Verify compiled extensions exist
if [[ ! -f "gitlab_mcp_server/server.cpython-312-x86_64-linux-gnu.so" ]]; then
    print_error "Compilation failed - no .so files found"
    exit 1
fi

print_status "Found compiled extensions:"
ls -la gitlab_mcp_server/*.so

# Create wheel manually
print_status "Building wheel..."
python setup.py bdist_wheel

# Check wheel contents
wheel_file=$(find dist/ -name "*.whl" | head -1)
if [[ -n "$wheel_file" ]]; then
    print_status "Successfully built wheel: $(basename "$wheel_file")"
    
    echo "📦 Wheel contents:"
    python -m zipfile -l "$wheel_file" | head -20
    
    # Check for source files (should be minimal)
    py_count=$(python -m zipfile -l "$wheel_file" | grep "\.py" | wc -l || true)
    so_count=$(python -m zipfile -l "$wheel_file" | grep "\.so" | wc -l || true)
    
    print_status "Found $so_count compiled extensions and $py_count Python files"
    
    if [[ "$so_count" -gt 0 ]]; then
        print_status "Binary wheel created successfully!"
        echo ""
        echo "📋 To install:"
        echo "  pip install $wheel_file"
        echo ""
        echo "📋 To test installation:"
        echo '  echo '"'"'{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'"'"' | gitlab-mcp-server'
    else
        print_error "No compiled extensions found in wheel"
        exit 1
    fi
else
    print_error "Wheel build failed"
    exit 1
fi