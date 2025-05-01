import os
from module import Module
from matplotlib import pyplot as plt
import networkx as nx
from pathlib import Path

from common import file_path_from_module_name, get_parent_module, module_name_from_file_path
from constants import CODE_ROOT_FOLDER
from imports_helper import imports_from_file

def build_data_structure():
    G = dependencies_digraph()
    G = set_package_flags(G)
    G = set_depth(G)
    return G


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


def dependencies_digraph():
    print(f"Building dependencies digraph...")
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    G = nx.DiGraph()
    
    top_level_packages = get_top_level_packages()

    for file in files:
        file_path = str(file)
        source_module_name = module_name_from_file_path(file_path)
        parent_module = get_parent_module(source_module_name)

        # Creates a module object with module name, parent module, file path, and dependencies
        source_module = Module(source_module_name, parent_module, file_path)

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

def draw_graph(G, size, **args):
    """Draw a graph using matplotlib."""
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()