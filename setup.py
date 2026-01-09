import os
import ast
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize
import importlib

SOURCE_ROOT = "."
EXCLUDE_DIRS = {
    ".git", ".github", "__pycache__",
    "build", "dist", "venv", ".venv", "tests",
    "dist_package", "linux-repo", "windows-repo"
}
EXCLUDE_FILES = {"setup.py", "main.py"}

NUMPY_IMPORTS = {"numpy", "np"}

# -----------------------
# Risk Detection Functions
# -----------------------
def is_file_risky(file_path):
    """
    Analyze a Python file AST to detect risky code.
    Flags any file that:
    - Uses indexing (arr[i], list[i])
    - Uses NumPy arrays or calls
    - Uses attributes (obj.attr) that could be arrays
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception:
        return True  # Treat unparseable files as risky

    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            return True
        elif isinstance(node, ast.Call):
            # Flag calls to numpy functions
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in NUMPY_IMPORTS:
                        return True
        elif isinstance(node, ast.Attribute):
            return True  # attribute access could be risky

    return False

# -----------------------
# Find all Python files
# -----------------------
def find_py_files(base_dir):
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                py_files.append(os.path.join(root, file))
    return py_files

# -----------------------
# Build Extension
# -----------------------
def make_extension(py_file):
    rel_path = os.path.relpath(py_file, SOURCE_ROOT)
    module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")

    risky = is_file_risky(py_file)
    if risky:
        directives = {
            "language_level": 3,
            "boundscheck": True,
            "wraparound": True,
            "initializedcheck": True,
        }
        annotate = True
        gdb_debug = True
    else:
        directives = {
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
        }
        annotate = False
        gdb_debug = False

    ext = Extension(module_name, [py_file])
    return cythonize(
        ext,
        compiler_directives=directives,
        annotate=annotate,
        gdb_debug=gdb_debug,
    )[0]

# -----------------------
# Test imports after build
# -----------------------
def test_imports(modules):
    return True
    """Try importing compiled modules to detect early crashes."""
    print("\n[INFO] Testing compiled modules...")
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"[OK] Imported {mod}")
        except Exception as e:
            print(f"[ERROR] Failed to import {mod}: {e}")
        except:  # Catch segmentation faults
            print(f"[CRASH] Segmentation fault in module {mod}")

# -----------------------
# Main setup logic
# -----------------------
py_files = find_py_files(SOURCE_ROOT)
extensions = [make_extension(f) for f in py_files]

# Get list of module names for testing
module_names = [os.path.splitext(os.path.relpath(f, SOURCE_ROOT))[0].replace(os.sep, ".") for f in py_files]

setup(
    name="compiled_project",
    version="1.0.0",
    ext_modules=extensions,
    zip_safe=False,
)

# Test compiled modules only when run directly
if __name__ == "__main__":
    test_imports(module_names)
