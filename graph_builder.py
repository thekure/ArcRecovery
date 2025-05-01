from module import Module
from matplotlib import pyplot as plt
import networkx as nx
from pathlib import Path

from common import get_parent_module, module_name_from_file_path
from constants import CODE_ROOT_FOLDER
from imports_helper import imports_from_file

def build_data_structure():
    top_level_packages = get_top_level_packages()
    return dependencies_digraph()


def dependency_is_internal(dependency):
    for dir in get_top_level_packages():
        if dependency.startswith(dir):
            return True
    return False



def get_top_level_packages():
    dirs = Path(CODE_ROOT_FOLDER).glob("[!.]*/")  # Exclude directories starting with '.'
    dirs = [dir.name for dir in dirs]
    return dirs


def dependencies_digraph():
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    G = nx.DiGraph()
    

    for file in files:
        file_path = str(file)
        source_module_name = module_name_from_file_path(file_path)
        # Creates a module object with module name, parent module, file path, and dependencies
        source_module = Module(source_module_name, get_parent_module(source_module_name), file_path)

        if source_module_name not in G.nodes:
            G.add_node(source_module_name, module=source_module)

        for dependency in imports_from_file(file_path):
            if dependency_is_internal(dependency):
                if dependency not in G.nodes:
                    G.add_node(dependency, module=Module(dependency, get_parent_module(dependency), file_path))
                G.add_edge(source_module_name, dependency)
                G.nodes[source_module_name]['module'].dependencies.add(dependency)

    return G



def draw_graph(G, size, **args):
    """Draw a graph using matplotlib."""
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()