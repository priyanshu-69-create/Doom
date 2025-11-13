# utils/resource_path.py
import os

def project_root():
    # go up one level from utils/ to the main project directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_path(*parts):
    """Return absolute path to a resource relative to project root."""
    return os.path.normpath(os.path.join(project_root(), *parts))
