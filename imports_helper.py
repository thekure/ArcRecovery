from common import get_parent_module, module_name_from_file_path
from constants import CODE_ROOT_FOLDER
import networkx as nx
import matplotlib.pyplot as plt
import re


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
    
    Returns:
    - For 'import x, y, z': returns ['x', 'y', 'z']
    - For 'from x import y, z': returns ['x'] (just the base module)
    - Returns empty list if no imports found
    """
    line = line.strip()
    result = []
    
    try:
        # Handle 'from' imports
        if line.startswith('from '):
            base_match = re.search(r'^from\s+(\.+\S*|\S+)\s+import\s+', line)
            if base_match:
                # We only care about the base module
                base_module = base_match.group(1)
                return [base_module]  # Return as a single-item list
                
        # Handle direct imports
        elif line.startswith('import '):
            # Remove the initial "import " to simplify parsing
            imports_part = re.sub(r'^import\s+', '', line)
            
            # Split by commas and process each part
            parts = imports_part.split(',')
            for part in parts:
                part = part.strip()
                if part:
                    # Extract just the module name (before any "as")
                    module_match = re.match(r'([a-zA-Z0-9_\.]+)(?:\s+as\s+[a-zA-Z0-9_]+)?', part)
                    if module_match:
                        result.append(module_match.group(1))
            
            return result
            
    except Exception as e:
        print(f"Error parsing import line: {line}")
        print(f"Error: {str(e)}")
    
    return result  # Return empty list if no matches

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
                imported_modules = import_from_line(subline if subline.strip().startswith('import') else 'import ' + subline)
                if imported_modules:
                    for module in imported_modules:
                        if module.startswith('.'):
                            resolved = resolve_relative_import(file, module)
                            all_imports.append(resolved)
                        else:
                            all_imports.append(module)
        else:
            imported_modules = import_from_line(line)
            if imported_modules:
                for module in imported_modules:
                    if module.startswith('.'):
                        resolved = resolve_relative_import(file, module)
                        all_imports.append(resolved)
                    else:
                        all_imports.append(module)
            
    return all_imports