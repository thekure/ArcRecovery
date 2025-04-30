from constants import CODE_ROOT_FOLDER
import pathlib
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import re


def file_path(file_name):
    """Convert a relative file path to absolute path using CODE_ROOT_FOLDER."""
    return CODE_ROOT_FOLDER + file_name

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

def resolve_relative_import(importing_file, relative_import):
    """Resolve a relative import to its full module name."""
    # Get the package path of the importing file
    package_path = module_name_from_file_path(importing_file)
    package_parts = package_path.split('.')
    
    # Count leading dots to determine how many levels to go up
    dots = len(relative_import) - len(relative_import.lstrip('.'))
    
    # Remove the appropriate number of package levels
    if dots > 0:
        package_parts = package_parts[:-dots]
    
    # Add the module name (everything after the dots)
    module_name = relative_import.lstrip('.')
    if module_name:
        return '.'.join(package_parts + [module_name])
    else:
        return '.'.join(package_parts)

def import_from_line(line):
    """Extract imported module names from a line of Python code.
    
    Handles:
    - import x
    - import x as y
    - import x, y, z
    - from x import y
    - from x import y as z
    - from x import (y, z)
    - from x.y.z import a
    """
    line = line.strip()
    
    try:
        # Handle 'from' imports
        if line.startswith('from '):
            base = re.search(r'^from\s+(\.+\S*|\S+)\s+import\s+', line)
            if base:
                return base.group(1)
                
        # Handle direct imports
        elif line.startswith('import '):
            matches = re.findall(r'import\s+([a-zA-Z0-9_\.]+)(?:\s+as\s+[a-zA-Z0-9_]+)?\s*(?:,|$)', line)
            if matches:
                return matches[0]  # Return to returning just the first match

    except Exception as e:
        print(f"Error parsing import line: {line}")
        print(f"Error: {str(e)}")
    
    return None  # Return to returning None

def imports_from_file(file):
    """Extract all imported modules from a Python file.
    
    Returns a list of module names (e.g., ['os', 'datetime', 'zeeguu.core'])
    """
    all_imports = []
    
    with open(file) as f:
        lines = f.readlines()
        
    for line in lines:
        # Handle multiple imports on one line by splitting at commas
        if line.strip().startswith('import '):
            for subline in line.split(','):
                imp = import_from_line(subline if subline.strip().startswith('import') else 'import ' + subline)
                if imp:
                    if imp.startswith('.'):
                        imp = resolve_relative_import(file, imp)
                    all_imports.append(imp)
        else:
            imp = import_from_line(line)
            if imp:
                if imp.startswith('.'):
                    imp = resolve_relative_import(file, imp)
                all_imports.append(imp)
            
    return all_imports

# G = dependencies_graph(CODE_ROOT_FOLDER)
# draw_graph(G, (80,80), with_labels=False)

# However, if we think a bit more about it, we realize tat a dependency graph
# is a directed graph (e.g. module A depends on m)
# with any kinds of graph either directed (nx.DiGraph) or
# non-directed (nx.Graph)

# Looking at the directed graph
# DG = dependencies_digraph(CODE_ROOT_FOLDER)
# draw_graph(DG, (40,40), with_labels=True)