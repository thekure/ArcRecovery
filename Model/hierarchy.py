import os
from collections import defaultdict
from .module import Module
from .common import get_parent_module

class ModuleHierarchy:
    """Organizes modules hierarchically for navigation and visualization."""
    
    def __init__(self, graph):
        """
        Initialize with a NetworkX graph of modules.
        
        Args:
            graph: NetworkX DiGraph with module nodes
        """
        self.graph = graph
        # Dictionary to store modules by depth
        self.depth_dict = {}
        self._build_hierarchy()
    
    def _build_hierarchy(self, debug=True):
        """Build the hierarchical dictionary from the graph nodes."""
        # Initialize empty dictionary for the root level
        self.depth_dict[''] = {
            'modules': set(),
            'packages': set()
        }
        
        node_count = 0

        # Process all nodes
        for node_name, node_data in self.graph.nodes(data=True):
            node_count += 1 # For debugging
            module = node_data['module']
            parts = node_name.split('.')
            
            # Handle root level modules (no dots)
            if len(parts) == 1:
                if module.is_package:
                    self.depth_dict['']['packages'].add(node_name)
                else:
                    self.depth_dict['']['modules'].add(module)
                continue

        

            # For modules with dots, add them only to their immediate parent
            parent_path = get_parent_module(node_name)
            last_part = parts[-1]  # The last part of the path
            
            # Initialize the dictionary for this level if needed
            if parent_path not in self.depth_dict:
                self.depth_dict[parent_path] = {
                    'modules': set(),
                    'packages': set()
                }
            

            # Add as a module or package to the immediate parent level
            if module.is_package:
                self.depth_dict[parent_path]['packages'].add(last_part)
            else:
                self.depth_dict[parent_path]['modules'].add(module)
            
            # Also ensure all ancestor paths are created and include this as a sub-package
            current = ''
            for i in range(len(parts) - 1):  # Skip the last part which we already handled
                
                part = parts[i]
                # Get the current path up to this part
                if current:
                    parent = current
                    current = f"{current}.{part}"
                else:
                    parent = ''
                    current = part
                # Initialize dictionary for this level if needed
                if parent not in self.depth_dict:
                    self.depth_dict[parent] = {
                        'modules': set(),
                        'packages': set()
                    }
                
                # Add as a package to its parent
                self.depth_dict[parent]['packages'].add(part)
    
    def get_level_view(self, path=''):
        """
        Get modules and packages at a specific level.
        
        Args:
            path: Package path (e.g., 'zeeguu.core')
            
        Returns:
            dict: {'modules': [...], 'packages': [...]}
        """
        if path in self.depth_dict:
            return self.depth_dict[path]
        return {'modules': set(), 'packages': set()}
    
    def get_aggregated_dependencies(self, path=''):
        """
        Calculate aggregated dependencies between modules/packages at this level.
        
        Args:
            path: Package path (e.g., 'zeeguu.core')
            
        Returns:
            dict: {(source, target): weight, ...}
        """
        dependencies = defaultdict(int)
        level_items = self.get_level_view(path)
        
        # For each module at this level
        for module in level_items['modules']:
            # For each dependency of this module
            for dep in module.dependencies:
                # Skip if dependency is not in the graph
                if dep not in self.graph.nodes:
                    continue
                    
                # If at root level
                if not path:
                    # Get top-level package of dependency
                    if '.' in dep:
                        target = dep.split('.')[0]
                        if target in level_items['packages']:
                            dependencies[(module.name, target)] += 1
                # If at deeper level
                else:
                    # Only consider dependencies within or across packages at this level
                    if dep.startswith(path + '.'):
                        rel_path = dep[len(path)+1:]  # +1 for the dot
                        if '.' in rel_path:
                            target = path + '.' + rel_path.split('.')[0]
                            dependencies[(module.name, target)] += 1
        
        # For dependencies between packages
        for package in level_items['packages']:
            full_package = f"{path}.{package}" if path else package
            
            # Get all modules in this package
            package_modules = [
                node for node in self.graph.nodes 
                if node.startswith(full_package + '.') or node == full_package
            ]
            
            # For each module in the package
            for pkg_module in package_modules:
                if pkg_module not in self.graph.nodes:
                    continue
                    
                # Get its dependencies
                for dep in self.graph.nodes[pkg_module].get('module', Module('', '', '')).dependencies:
                    # Skip if dependency is not in the graph
                    if dep not in self.graph.nodes:
                        continue
                        
                    # Only count dependencies to other packages at this level
                    if not path:
                        if '.' in dep:
                            target = dep.split('.')[0]
                            if target in level_items['packages'] and target != package:
                                dependencies[(package, target)] += 1
                    else:
                        if dep.startswith(path + '.'):
                            rel_path = dep[len(path)+1:]
                            if '.' in rel_path:
                                target_pkg = rel_path.split('.')[0]
                                target = path + '.' + target_pkg
                                if target_pkg in level_items['packages'] and target_pkg != package:
                                    dependencies[(package, target_pkg)] += 1
        
        return dict(dependencies)
    
    def get_module_info(self, module_name):
        """
        Get detailed information about a specific module.
        
        Args:
            module_name: Full module name
            
        Returns:
            dict: Module information including dependencies
        """
        if module_name in self.graph.nodes and 'module' in self.graph.nodes[module_name]:
            module = self.graph.nodes[module_name]['module']
            return {
                'name': module.name,
                'parent': module.parent_module,
                'file_path': module.file_path,
                'is_package': module.is_package,
                'depth': module.depth,
                'dependencies': list(module.dependencies),
                'dependency_count': len(module.dependencies)
            }
        return None 