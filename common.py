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
    file_name = str(relative)
    file_name = file_name.replace("/__init__.py", "")
    file_name = file_name.replace("/", ".")
    file_name = file_name.replace(".py", "")
    #file_name = file_name.replace("./repo_for_analysis/", "")

    return file_name

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