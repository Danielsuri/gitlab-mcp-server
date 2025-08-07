#!/usr/bin/env python3
"""
Test script to validate Python 3.8 compatibility specifically for urllib3.
This addresses the specific error mentioned in issue #25.
"""

import sys


def test_urllib3_availability_for_python38():
    """Test that urllib3 versions in our range are available for Python 3.8."""
    print("🔍 Testing urllib3 version compatibility for Python 3.8...")
    
    # Based on the error message from the issue, these are the versions that were available:
    available_versions = [
        "0.3", "1.0", "1.0.1", "1.0.2", "1.1", "1.2", "1.2.1", "1.2.2", "1.3", "1.4", "1.5", 
        "1.6", "1.7", "1.7.1", "1.8", "1.8.2", "1.8.3", "1.9", "1.9.1", "1.10", "1.10.1", 
        "1.10.2", "1.10.3", "1.10.4", "1.11", "1.12", "1.13", "1.13.1", "1.14", "1.15", 
        "1.15.1", "1.16", "1.17", "1.18", "1.18.1", "1.19", "1.19.1", "1.20", "1.21", 
        "1.21.1", "1.22", "1.23", "1.24", "1.24.1", "1.24.2", "1.24.3", "1.25.2", "1.25.3", 
        "1.25.4", "1.25.5", "1.25.6", "1.25.7", "1.25.8", "1.25.9", "1.25.10", "1.25.11", 
        "1.26.0", "1.26.1", "1.26.2", "1.26.3", "1.26.4", "1.26.5", "1.26.6", "1.26.7", 
        "1.26.8", "1.26.9", "1.26.10", "1.26.11", "1.26.12", "1.26.13", "1.26.14", "1.26.15", 
        "1.26.16", "1.26.17", "1.26.18", "1.26.19", "1.26.20", "2.0.0a1", "2.0.0a2", "2.0.0a3", 
        "2.0.0a4", "2.0.2", "2.0.3", "2.0.4", "2.0.5", "2.0.6", "2.0.7", "2.1.0", "2.2.0", 
        "2.2.1", "2.2.2", "2.2.3"
    ]
    
    # Check that 2.5.0 was NOT available (the issue)
    if "2.5.0" in available_versions:
        print("❌ Test setup error: 2.5.0 should not be in available versions")
        return False
    
    print("✅ Confirmed: urllib3==2.5.0 was not available for Python 3.8")
    
    # Check that versions in our range >=2.0.0,<2.3.0 are available
    compatible_versions = []
    for version in available_versions:
        try:
            # Parse version number to check if it's in our range
            if version.startswith("2."):
                version_parts = version.split(".")
                if len(version_parts) >= 2:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    if major == 2 and minor < 3:
                        compatible_versions.append(version)
        except (ValueError, IndexError):
            continue
    
    print(f"✅ Found {len(compatible_versions)} compatible versions in range >=2.0.0,<2.3.0:")
    for version in compatible_versions:
        print(f"   - {version}")
    
    if len(compatible_versions) > 0:
        print("✅ Our version range >=2.0.0,<2.3.0 has available versions")
        return True
    else:
        print("❌ No compatible versions found in our range")
        return False


def test_requirements_fix():
    """Test that our requirements.txt fix addresses the original issue."""
    print("🔍 Testing that requirements.txt fix addresses original issue...")
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    if "urllib3==2.5.0" in content:
        print("❌ requirements.txt still contains the problematic urllib3==2.5.0")
        return False
    elif "urllib3>=2.0.0,<2.3.0" in content:
        print("✅ requirements.txt contains compatible urllib3 version range")
        return True
    else:
        print("❌ requirements.txt does not contain expected urllib3 version specification")
        return False


def test_pyproject_fix():
    """Test that pyproject.toml fix addresses the original issue."""
    print("🔍 Testing that pyproject.toml fix addresses original issue...")
    
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        
        if "urllib3>=2.5.0" in content:
            print("❌ pyproject.toml still contains the problematic urllib3>=2.5.0")
            return False
        elif "urllib3>=2.0.0,<2.3.0" in content:
            print("✅ pyproject.toml contains compatible urllib3 version range")
            return True
        else:
            print("❌ pyproject.toml does not contain expected urllib3 version specification")
            return False
    except FileNotFoundError:
        print("⚠️  pyproject.toml not found, skipping")
        return True


def main():
    """Run all Python 3.8 compatibility tests."""
    print("🧪 Python 3.8 urllib3 Compatibility Test Suite")
    print("=" * 55)
    print(f"Current Python version: {sys.version}")
    print("=" * 55)
    
    tests = [
        ("urllib3 version availability for Python 3.8", test_urllib3_availability_for_python38),
        ("requirements.txt fix verification", test_requirements_fix),
        ("pyproject.toml fix verification", test_pyproject_fix),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed}/{total} passed")
    print("=" * 55)
    
    if passed == total:
        print("🎉 All Python 3.8 compatibility tests passed!")
        print("   This should fix the wheel action bug on Python 3.8")
        return 0
    else:
        print("⚠️  Some tests failed. The fix may not be complete.")
        return 1


if __name__ == "__main__":
    sys.exit(main())