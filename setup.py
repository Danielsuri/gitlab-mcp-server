#!/usr/bin/env python3
"""
Setup script for gitlab-mcp-server with Cython compilation
"""
import os
from setuptools import setup, Extension
from setuptools.command.build_py import build_py
from Cython.Build import cythonize

class BuildPyBinaryOnly(build_py):
    """Custom build_py command to exclude Python source files from binary distribution"""
    
    def run(self):
        # Only run the normal build_py for .py files that don't have corresponding extensions
        super().run()
        
        # Remove the source .py files and .c files that have been compiled to extensions
        build_dir = self.build_lib
        for ext_name in ['mcp_server', 'test_mcp_server']:
            py_file = os.path.join(build_dir, 'gitlab_mcp_server', f'{ext_name}.py')
            c_file = os.path.join(build_dir, 'gitlab_mcp_server', f'{ext_name}.c')
            if os.path.exists(py_file):
                os.remove(py_file)
                print(f"Removed source file: {py_file}")
            if os.path.exists(c_file):
                os.remove(c_file)
                print(f"Removed C file: {c_file}")

# Define extensions for Cython compilation
extensions = [
    Extension(
        "gitlab_mcp_server.mcp_server",
        ["src/gitlab_mcp_server/mcp_server.py"],
        include_dirs=[],
        language="c"
    ),
    Extension(
        "gitlab_mcp_server.test_mcp_server", 
        ["src/gitlab_mcp_server/test_mcp_server.py"],
        include_dirs=[],
        language="c"
    )
]

# Cythonize the extensions
cythonized_extensions = cythonize(
    extensions,
    compiler_directives={
        "embedsignature": True,
        "language_level": "3"
    }
)

if __name__ == "__main__":
    setup(
        ext_modules=cythonized_extensions,
        cmdclass={'build_py': BuildPyBinaryOnly},
        zip_safe=False,
    )