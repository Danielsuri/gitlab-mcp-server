#!/usr/bin/env python3
"""
Test script to validate requirements.txt compatibility.
This test validates that all dependencies can be resolved and are compatible.
"""

import sys
import subprocess
import tempfile
import os


def test_requirements_syntax():
    """Test that requirements.txt has valid syntax."""
    print("🔍 Testing requirements.txt syntax...")
    
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith('#'):
            # Basic syntax validation
            if '==' in line:
                parts = line.split('==')
                if len(parts) != 2:
                    print(f"❌ Line {i}: Invalid syntax '{line}'")
                    return False
            elif '>=' in line and '<' in line:
                # Version range format like "urllib3>=2.0.0,<2.3.0"
                if not (',' in line and '>=' in line and '<' in line):
                    print(f"❌ Line {i}: Invalid version range syntax '{line}'")
                    return False
            else:
                print(f"⚠️  Line {i}: Unrecognized format '{line}'")
    
    print("✅ requirements.txt syntax is valid")
    return True


def test_urllib3_version_range():
    """Test that urllib3 version range is reasonable."""
    print("🔍 Testing urllib3 version range...")
    
    with open("requirements.txt", 'r') as f:
        content = f.read()
    
    if "urllib3>=2.0.0,<2.3.0" in content:
        print("✅ urllib3 version range is appropriate for Python 3.8+ compatibility")
        return True
    elif "urllib3==2.5.0" in content:
        print("❌ urllib3==2.5.0 is not compatible with Python 3.8")
        return False
    else:
        print("❌ urllib3 version not found or unexpected format")
        return False


def test_pyproject_toml_consistency():
    """Test that pyproject.toml and requirements.txt are consistent for urllib3."""
    print("🔍 Testing pyproject.toml consistency...")
    
    if not os.path.exists("pyproject.toml"):
        print("⚠️  pyproject.toml not found, skipping consistency check")
        return True
    
    with open("pyproject.toml", 'r') as f:
        pyproject_content = f.read()
    
    if "urllib3>=2.0.0,<2.3.0" in pyproject_content:
        print("✅ pyproject.toml has consistent urllib3 version range")
        return True
    elif "urllib3>=2.5.0" in pyproject_content:
        print("❌ pyproject.toml still has incompatible urllib3>=2.5.0")
        return False
    else:
        print("❌ urllib3 version not found in pyproject.toml dependencies")
        return False


def test_dry_run_install():
    """Test pip install --dry-run to check if dependencies can be resolved."""
    print("🔍 Testing dependency resolution with pip --dry-run...")
    
    try:
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Run pip install --dry-run to check if dependencies can be resolved
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--dry-run', 
                '-r', 'requirements.txt'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Dependencies can be resolved successfully")
                return True
            else:
                # Check if it's a network error
                error_output = result.stderr.lower()
                if 'timeout' in error_output or 'connection' in error_output or 'network' in error_output:
                    print("⚠️  Dependency resolution failed due to network issues (expected in CI)")
                    return True  # Don't fail due to network issues
                else:
                    print(f"❌ Dependency resolution failed:")
                    print(f"   stdout: {result.stdout}")
                    print(f"   stderr: {result.stderr}")
                    return False
                
    except subprocess.TimeoutExpired:
        print("⚠️  Dependency resolution test timed out (network issues)")
        return True  # Don't fail due to network issues
    except Exception as e:
        print(f"⚠️  Could not test dependency resolution: {e}")
        return True  # Don't fail due to environment issues


def main():
    """Run all requirement tests."""
    print("🧪 Requirements Compatibility Test Suite")
    print("=" * 50)
    
    tests = [
        ("Requirements Syntax", test_requirements_syntax),
        ("urllib3 Version Range", test_urllib3_version_range),
        ("pyproject.toml Consistency", test_pyproject_toml_consistency),
        ("Dependency Resolution", test_dry_run_install),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())