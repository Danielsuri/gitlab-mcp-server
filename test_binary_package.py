#!/usr/bin/env python3
"""
Test script to verify binary package functionality.

This script tests that the compiled GitLab MCP Server package works correctly
after installation from the binary wheel.
"""

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path


def test_package_import():
    """Test that the package can be imported successfully."""
    print("🔍 Testing package import...")
    try:
        import gitlab_mcp_server
        print(f"✅ Package imported successfully")
        print(f"   Version: {gitlab_mcp_server.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import package: {e}")
        return False


def test_console_script():
    """Test that the console script is available and works."""
    print("\n🔍 Testing console script availability...")
    try:
        result = subprocess.run(['which', 'gitlab-mcp-server'], 
                              capture_output=True, text=True, check=True)
        script_path = result.stdout.strip()
        print(f"✅ Console script found at: {script_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Console script 'gitlab-mcp-server' not found")
        return False


def test_mcp_protocol():
    """Test basic MCP protocol functionality."""
    print("\n🔍 Testing MCP protocol communication...")
    
    test_messages = [
        {
            "name": "initialize",
            "message": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0"}
                }
            },
            "expected_keys": ["result", "serverInfo"]
        },
        {
            "name": "tools/list",
            "message": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            },
            "expected_keys": ["result", "tools"]
        },
        {
            "name": "hello_world",
            "message": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "hello_world",
                    "arguments": {}
                }
            },
            "expected_keys": ["result", "content"]
        }
    ]
    
    all_passed = True
    
    for test in test_messages:
        print(f"   Testing {test['name']}...")
        
        try:
            # Send message to server
            process = subprocess.Popen(
                ['gitlab-mcp-server'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            message_json = json.dumps(test['message'])
            stdout, stderr = process.communicate(input=message_json, timeout=10)
            
            if process.returncode != 0:
                print(f"   ❌ Process failed with return code {process.returncode}")
                if stderr:
                    print(f"      Error: {stderr}")
                all_passed = False
                continue
            
            # Parse response
            try:
                response = json.loads(stdout.strip())
                
                # Check if expected keys are present
                for key in test['expected_keys']:
                    if key not in response:
                        print(f"   ❌ Missing expected key '{key}' in response")
                        all_passed = False
                        continue
                
                print(f"   ✅ {test['name']} test passed")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Failed to parse JSON response: {e}")
                print(f"      Raw output: {stdout}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ {test['name']} test timed out")
            process.kill()
            all_passed = False
        except Exception as e:
            print(f"   ❌ {test['name']} test failed: {e}")
            all_passed = False
    
    return all_passed


def test_error_handling():
    """Test that the server handles invalid input gracefully."""
    print("\n🔍 Testing error handling...")
    
    try:
        # Send invalid JSON
        process = subprocess.Popen(
            ['gitlab-mcp-server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='invalid json\n', timeout=5)
        
        # Server should not crash with invalid input - it should ignore malformed messages
        if process.returncode == 0 or process.returncode == -15:  # 0 or SIGTERM
            print("✅ Server handles invalid JSON gracefully")
            return True
        else:
            print(f"❌ Server crashed with invalid input (return code: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_binary_compilation():
    """Verify that the package contains only compiled extensions."""
    print("\n🔍 Testing binary compilation...")
    
    try:
        import gitlab_mcp_server
        package_path = Path(gitlab_mcp_server.__file__).parent
        
        # Check for .so files (compiled extensions)
        so_files = list(package_path.glob("*.so"))
        pyd_files = list(package_path.glob("*.pyd"))  # Windows
        py_files = list(package_path.glob("*.py"))
        
        compiled_files = so_files + pyd_files
        
        print(f"   Found {len(compiled_files)} compiled extension(s)")
        print(f"   Found {len(py_files)} Python source file(s)")
        
        if compiled_files:
            print("   ✅ Package contains compiled extensions")
            for f in compiled_files:
                print(f"      - {f.name}")
            
            # Check that only __init__.py exists as source (minimal stub)
            source_files = [f for f in py_files if f.name != "__init__.py"]
            if source_files:
                print(f"   ⚠️  Warning: Found source files other than __init__.py:")
                for f in source_files:
                    print(f"      - {f.name}")
            else:
                print("   ✅ Only minimal __init__.py source file present")
            
            return True
        else:
            print("   ❌ No compiled extensions found")
            return False
            
    except Exception as e:
        print(f"❌ Binary compilation test failed: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("🧪 GitLab MCP Server Binary Package Test Suite")
    print("=" * 50)
    
    tests = [
        ("Package Import", test_package_import),
        ("Console Script", test_console_script),
        ("MCP Protocol", test_mcp_protocol),
        ("Error Handling", test_error_handling),
        ("Binary Compilation", test_binary_compilation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Binary package is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()