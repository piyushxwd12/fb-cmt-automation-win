from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import sys

SOURCE_ROOT = "."
EXCLUDE_DIRS = {
    ".git", ".github", "__pycache__",
    "build", "dist", "venv", ".venv", "tests"
}

EXCLUDE_FILES = {"setup.py"}  # files not to compile

def find_py_files(base_dir):
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                py_files.append(os.path.join(root, file))
    return py_files

extensions = []

for py_file in find_py_files(SOURCE_ROOT):
    # Convert path to module name: src/module/foo.py -> src.module.foo
    module_name = os.path.splitext(os.path.relpath(py_file, SOURCE_ROOT))[0].replace(os.sep, ".")
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
        },
        annotate=False,
    ),
    zip_safe=False,
)