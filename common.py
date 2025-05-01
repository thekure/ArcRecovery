import os
from pathlib import Path
from constants import CODE_ROOT_FOLDER

# Extracts modules from file names
def module_name_from_file_path(full_path):
    """Extract module name from file path.
    
    Examples:
        zeeguu/core/model/user.py -> zeeguu.core.model.user
        zeeguu/core/model/__init__.py -> zeeguu.core.model
    """
    # Convert to Path object for safer path manipulation
    path = Path(full_path)
    root = Path(CODE_ROOT_FOLDER)
    
    # Get relative path from root
    try:
        relative = path.relative_to(root)
    except ValueError:
        # If path doesn't start with root, just use the full path
        relative = path
        
    # Convert to string and clean up
    module_name = str(relative)
    module_name = module_name.replace("/__init__.py", "")
    module_name = module_name.replace("/", ".")
    module_name = module_name.replace(".py", "")
    #file_name = file_name.replace("./repo_for_analysis/", "")

    return module_name

def file_path_from_module_name(module_name):
    """Convert a module name to a file path.
    
    Examples:
        zeeguu.core.model.user -> zeeguu/core/model/user.py
        zeeguu.core.model -> zeeguu/core/model/
    
    Args:
        module_name: Dotted module name (e.g., 'zeeguu.core.model')
        
    Returns:
        str: File path corresponding to the module name
    """
    # Convert dots to directory separators
    path_parts = module_name.split('.')
    relative_path = os.path.join(*path_parts)
    
    # Full path in the filesystem
    full_path = os.path.join(CODE_ROOT_FOLDER, relative_path)
    
    # Check if this is a package (directory)
    if os.path.isdir(full_path):
        return full_path + os.path.sep  # Return directory with trailing slash
    
    # Otherwise, it's a regular module
    return f"{full_path}.py"

def get_parent_module(module_name):
    """Extract the parent module name from a dotted module path.
    
    For example:
    - 'app.components' -> 'app'
    - 'app' -> ''  (a top-level module has no parent)
    """
    path = module_name.split('.')
    parent_depth = len(path) - 1
    parent_path = ""
    
    for i in range(parent_depth):
        if i == parent_depth - 1:
            parent_path += path[i]
        else:
            parent_path += path[i] + "."

    return parent_path

def file_path(file_name):
    """Convert a relative file path to absolute path using CODE_ROOT_FOLDER."""
    return CODE_ROOT_FOLDER + file_name