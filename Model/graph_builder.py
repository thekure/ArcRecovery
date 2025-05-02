import os
from .module import Module
from matplotlib import pyplot as plt
import networkx as nx
from pathlib import Path

from .common import file_path_from_module_name, get_parent_module, module_name_from_file_path
from constants import CODE_ROOT_FOLDER
from .imports_helper import imports_from_file
from .hierarchy import ModuleHierarchy

def get_dependencies_digraph():
    G = build_graph()
    G = set_package_flags(G)
    G = set_depth(G)
    return G

def get_module_hierarchy():
    """Get a hierarchical organization of modules."""
    G = get_dependencies_digraph()
    return ModuleHierarchy(G)

def dependency_is_internal(dependency, top_level_packages):
    for dir in top_level_packages:
        if dependency.startswith(dir):
            return True
    return False


def get_top_level_packages():
    print(f"Identifying top level packages...\n")
    dirs = Path(CODE_ROOT_FOLDER).glob("[!.]*/")  # Exclude directories starting with '.'
    dirs = [dir.name for dir in dirs]
    return dirs


def set_ancestor_paths(G, source_module_name):
    parts = source_module_name.split('.')
    current = ''
    for _, part in enumerate(parts[:-1]):  # Skip the last part (actual module)
        parent = current
        current = f"{current}.{part}" if current else part
        if current not in G.nodes:
            G.add_node(current, module=Module(current, parent, file_path_from_module_name(current)))
    return G


def build_graph():
    print(f"Building dependencies digraph...")
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    G = nx.DiGraph()
    
    top_level_packages = get_top_level_packages()

    for file in files:
        file_path = str(file)

        source_module_name = module_name_from_file_path(file_path)
        parent_module_name = get_parent_module(source_module_name)

        G = set_ancestor_paths(G, source_module_name)

        if "__init__" in file_path:
            source_module = Module(source_module_name, parent_module_name, file_path)
            source_module.is_package = True
        else:
            # Creates a module object with module name, parent module, file path, and dependencies
            source_module = Module(source_module_name, parent_module_name, file_path)

        if source_module_name not in G.nodes:
            G.add_node(source_module_name, module=source_module)

        for dependency in imports_from_file(file_path):
            if dependency_is_internal(dependency, top_level_packages):
                if dependency not in G.nodes:
                    G.add_node(dependency, module=Module(dependency, get_parent_module(dependency), file_path))
                    G.add_edge(source_module_name, dependency)
                    G.nodes[source_module_name]['module'].dependencies.add(dependency)

    print(f"Nodes created: {len(G.nodes)}\n")
    return G

def set_package_flags(G):
    print("Setting package flags...")
    packages_found = 0
    
    for node_name, node_data in G.nodes(data=True):
        if 'module' in node_data:
            path = file_path_from_module_name(node_data['module'].name)
            is_dir = os.path.isdir(path)
            
            # Debug output
            if is_dir:
                packages_found += 1
                node_data['module'].is_package = True
                
    print(f"Total packages identified: {packages_found}\n")
    return G

def set_depth(G):
    print("Setting depth...")
    max_depth = 0
    
    for node_name, node_data in G.nodes(data=True):
        if 'module' in node_data:
                        # Calculate depth based on number of dots in module name
            depth = node_name.count('.')
            node_data['module'].depth = depth
            
            # Track maximum depth for reporting
            if depth > max_depth:
                max_depth = depth
                
    print(f"Max depth: {max_depth}")
    return G

def print_module_tree(G):
    """Print the file/module hierarchy as a tree structure."""
    from collections import defaultdict

    # Build a tree of parent → children
    tree = defaultdict(list)
    roots = []

    for node_name, node_data in G.nodes(data=True):
        module = node_data['module']
        parent = module.parent_module
        if parent and parent in G.nodes:
            tree[parent].append(node_name)
        else:
            roots.append(node_name)

    def print_subtree(node, prefix=""):
        module = G.nodes[node]['module']
        label = node.split('.')[-1]
        is_pkg = module.is_package
        suffix = "/" if is_pkg else ".py"
        print(f"{prefix}├── {label}{suffix}")
        children = sorted(tree.get(node, []))
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_subtree(child, next_prefix)

    # Start from top-level roots
    for root in sorted(roots):
        print_subtree(root)


def draw_graph(G, size, **args):
    """Draw a graph using matplotlib."""
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()