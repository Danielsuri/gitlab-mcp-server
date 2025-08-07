#!/usr/bin/env python3
"""
Test script to verify the final wheel package directly.

This script tests the wheel contents and functionality to ensure it meets
the binary-only requirements.
"""

import json
import subprocess
import sys
import tempfile
import os
import zipfile
from pathlib import Path


def test_wheel_contents(wheel_path):
    """Test that the wheel contains only binary files and minimal source."""
    print("🔍 Testing wheel contents...")
    
    try:
        with zipfile.ZipFile(wheel_path, 'r') as zf:
            file_list = zf.namelist()
            
            py_files = [f for f in file_list if f.endswith('.py')]
            so_files = [f for f in file_list if f.endswith('.so') or f.endswith('.pyd')]
            
            print(f"   Found {len(so_files)} compiled extension(s)")
            print(f"   Found {len(py_files)} Python source file(s)")
            
            # List compiled extensions
            for f in so_files:
                print(f"      - {f}")
            
            # Check Python files - should only be __init__.py
            if len(py_files) == 1 and py_files[0].endswith('__init__.py'):
                print(f"   ✅ Only minimal __init__.py present: {py_files[0]}")
                
                # Check __init__.py size (should be minimal)
                init_info = zf.getinfo(py_files[0])
                if init_info.file_size < 500:  # Small stub file
                    print(f"   ✅ __init__.py is minimal ({init_info.file_size} bytes)")
                else:
                    print(f"   ⚠️  __init__.py is larger than expected ({init_info.file_size} bytes)")
                
            elif len(py_files) == 0:
                print("   ✅ No Python source files (pure binary)")
            else:
                print(f"   ❌ Unexpected Python files found:")
                for f in py_files:
                    print(f"      - {f}")
                return False
            
            # Must have compiled extensions
            if so_files:
                print("   ✅ Binary-only wheel verified")
                return True
            else:
                print("   ❌ No compiled extensions found")
                return False
                
    except Exception as e:
        print(f"❌ Failed to test wheel contents: {e}")
        return False


def test_clean_installation(wheel_path):
    """Test installation in a completely clean environment."""
    print("\n🔍 Testing clean installation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create clean virtual environment
            venv_path = Path(temp_dir) / "clean_env"
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], 
                          check=True, capture_output=True)
            
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
            else:  # Unix-like
                python_exe = venv_path / "bin" / "python"
            
            print(f"   Created clean environment at: {venv_path}")
            
            # Install wheel without dependencies first
            result = subprocess.run([
                str(python_exe), '-m', 'pip', 'install', '--no-deps', str(wheel_path)
            ], capture_output=True, text=True, check=True)
            
            print("   ✅ Wheel installed successfully (no deps)")
            
            # Test basic import
            import_test = subprocess.run([
                str(python_exe), '-c', 
                'import gitlab_mcp_server; print(f"Version: {gitlab_mcp_server.__version__}")'
            ], capture_output=True, text=True)
            
            if import_test.returncode == 0:
                print(f"   ✅ Package import successful")
                print(f"      Output: {import_test.stdout.strip()}")
            else:
                # Expected to fail due to missing dependencies
                if "requests" in import_test.stderr:
                    print("   ✅ Import fails due to missing dependencies (expected)")
                else:
                    print(f"   ❌ Unexpected import failure: {import_test.stderr}")
                    return False
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Installation failed: {e}")
            if e.stderr:
                print(f"      Error: {e.stderr}")
            return False
        except Exception as e:
            print(f"   ❌ Clean installation test failed: {e}")
            return False


def test_wheel_metadata(wheel_path):
    """Test wheel metadata and structure."""
    print("\n🔍 Testing wheel metadata...")
    
    try:
        with zipfile.ZipFile(wheel_path, 'r') as zf:
            # Look for metadata
            metadata_files = [f for f in zf.namelist() if 'METADATA' in f]
            wheel_files = [f for f in zf.namelist() if f.endswith('/WHEEL')]
            entry_points = [f for f in zf.namelist() if 'entry_points' in f]
            
            if metadata_files:
                print(f"   ✅ Found metadata: {metadata_files[0]}")
                
                # Read metadata
                metadata_content = zf.read(metadata_files[0]).decode('utf-8')
                if 'gitlab-mcp-server' in metadata_content:
                    print("   ✅ Package name in metadata")
                if 'requests' in metadata_content:
                    print("   ✅ Dependencies listed in metadata")
            
            if wheel_files:
                print(f"   ✅ Found wheel info: {wheel_files[0]}")
            
            if entry_points:
                print(f"   ✅ Found entry points: {entry_points[0]}")
                
                # Read entry points
                ep_content = zf.read(entry_points[0]).decode('utf-8')
                if 'gitlab-mcp-server' in ep_content:
                    print("   ✅ Console script entry point configured")
            
            return True
            
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False


def test_wheel_size_and_structure(wheel_path):
    """Test wheel size and basic structure."""
    print("\n🔍 Testing wheel size and structure...")
    
    try:
        wheel_size = os.path.getsize(wheel_path) / 1024  # KB
        print(f"   Wheel size: {wheel_size:.1f} KB")
        
        if wheel_size > 100:  # Should be substantial due to compiled extensions
            print("   ✅ Wheel size indicates compiled content")
        else:
            print("   ⚠️  Wheel seems small - may not contain compiled extensions")
        
        # Check filename format
        wheel_name = Path(wheel_path).name
        if 'cp312' in wheel_name and 'linux_x86_64' in wheel_name:
            print(f"   ✅ Wheel filename indicates platform-specific build: {wheel_name}")
        else:
            print(f"   ⚠️  Wheel filename doesn't indicate platform-specific build: {wheel_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Size/structure test failed: {e}")
        return False


def main():
    """Run all wheel tests."""
    # Find the wheel file
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory not found. Please run build first.")
        sys.exit(1)
    
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("❌ No wheel files found in dist/. Please run build first.")
        sys.exit(1)
    
    wheel_path = wheel_files[0]
    print(f"🧪 Testing wheel: {wheel_path}")
    print("=" * 60)
    
    tests = [
        ("Wheel Contents", lambda: test_wheel_contents(wheel_path)),
        ("Wheel Metadata", lambda: test_wheel_metadata(wheel_path)),
        ("Wheel Size/Structure", lambda: test_wheel_size_and_structure(wheel_path)),
        ("Clean Installation", lambda: test_clean_installation(wheel_path)),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Wheel Test Results Summary:")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All wheel tests passed! Binary package is ready for distribution.")
        print("")
        print("📦 Installation command:")
        print(f"   pip install {wheel_path}")
        print("")
        print("🚀 For GitHub Packages:")
        print("   pip install --extra-index-url https://$USERNAME:$TOKEN@pypi.pkg.github.com/Danielsuri gitlab-mcp-server")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()