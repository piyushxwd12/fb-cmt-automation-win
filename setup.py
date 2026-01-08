from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import sys
import shutil

SOURCE_ROOT = "."
EXCLUDE_DIRS = {
    ".git", ".github", "__pycache__",
    "build", "dist", "venv", ".venv", "tests",
    "dist_package", "linux-repo", "windows-repo"
}

EXCLUDE_FILES = {"setup.py", "main.py"}  # Keep main.py as source

def find_py_files(base_dir):
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                full_path = os.path.join(root, file)
                py_files.append(full_path)
    return py_files

extensions = []

for py_file in find_py_files(SOURCE_ROOT):
    # Convert path to module name: core/bot.py -> core.bot
    rel_path = os.path.relpath(py_file, SOURCE_ROOT)
    module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")
    extensions.append(Extension(module_name, [py_file]))

setup(
    name="compiled_project",
    version="1.0.0",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "optimize.use_switch": True,
        },
        annotate=False,
    ),
    zip_safe=False,
)