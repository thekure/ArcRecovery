from matplotlib import pyplot as plt
import networkx as nx
from pathlib import Path
from scanner import imports_from_file, module_name_from_file_path
from scanner import CODE_ROOT_FOLDER
from collections import defaultdict

def dependency_is_internal(dependency):
    for dir in get_top_level_packages():
        if dependency.startswith(dir):
            return True
    return False

def build_data_structure():
    top_level_packages = get_top_level_packages()

def get_top_level_packages():
    dirs = Path(CODE_ROOT_FOLDER).glob("[!.]*/")  # Exclude directories starting with '.'
    
    for dir in dirs:
        print(dir.name)

def dependencies_digraph():
    files = Path(CODE_ROOT_FOLDER).rglob("*.py")
    G = nx.DiGraph()
    
    # Track modules per package
    package_contents = defaultdict(int)
    package_dependencies = defaultdict(set)

    for file in files:
        file_path = str(file)
        source_module = module_name_from_file_path(file_path)

        if source_module not in G.nodes:
            G.add_node(source_module, outgoing_count=0, module_count=1)  # Initial attributes

        for target_module in imports_from_file(file_path):
            G.add_edge(source_module, target_module)
            G.nodes[source_module]['outgoing_count'] += 1  # Increment counter

    return G

def draw_graph(G, size, **args):
    """Draw a graph using matplotlib."""
    plt.figure(figsize=size)
    nx.draw(G, **args)
    plt.show()