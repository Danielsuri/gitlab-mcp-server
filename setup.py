#!/usr/bin/env python3
"""
Setup script for building binary-only GitLab MCP Server wheel.

This setup.py is specifically designed to create a wheel that contains
only compiled .so/.pyd files, hiding the source code from users.
"""

import os
import sys
from pathlib import Path
import setuptools
import setuptools.command.build_py
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


class CustomBuildExt(build_ext):
    """Custom build extension to ensure binary-only distribution."""
    
    def run(self):
        # Build the Cython extensions
        super().run()


class CustomBuildPy(setuptools.command.build_py.build_py):
    """Custom build_py to exclude source .py files from binary-only wheel."""
    
    def run(self):
        # Create minimal __init__.py only
        self.build_packages()
    
    def build_packages(self):
        # Create minimal __init__.py
        package_dir = os.path.join(self.build_lib, "gitlab_mcp_server")
        os.makedirs(package_dir, exist_ok=True)
        
        init_file = os.path.join(package_dir, "__init__.py")
        with open(init_file, 'w') as f:
            f.write('"""GitLab MCP Server Package"""\n')
            f.write('__version__ = "0.1.0"\n')
            f.write('from . import server\n')
            f.write('def run():\n')
            f.write('    """Entry point for console script."""\n')
            f.write('    server.main()\n')


def get_extensions():
    """Get list of Cython extensions to compile."""
    extensions = []
    
    # Find all .py files in the package directory (except __init__.py)
    package_dir = Path("gitlab_mcp_server")
    for py_file in package_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            # Convert to module path
            module_name = f"gitlab_mcp_server.{py_file.stem}"
            extensions.append(
                Extension(
                    module_name,
                    [str(py_file)],
                    language_level="3"
                )
            )
    
    return extensions


if __name__ == "__main__":
    # Check if Cython is available
    try:
        from Cython.Build import cythonize
    except ImportError:
        print("Error: Cython is required for building this package.")
        print("Please install it with: pip install Cython")
        sys.exit(1)
    
    extensions = get_extensions()
    
    if not extensions:
        print("Warning: No Python files found to compile.")
        
    setup(
        cmdclass={
            'build_ext': CustomBuildExt,
            'build_py': CustomBuildPy,
        },
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                'language_level': "3",
                'embedsignature': True,
                'boundscheck': False,
                'wraparound': False,
            },
            build_dir="build/cython"
        ),
        zip_safe=False,  # Required for binary extensions
        include_package_data=True,
    )