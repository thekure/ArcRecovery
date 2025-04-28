import os
import ast
import networkx as nx

class DependencyAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def parse_imports(self, file_path):
        imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception as e:
            print(f"Failed to parse {file_path}: {e}")
        
        # Map imports to local modules if possible
        rel_path = os.path.relpath(file_path, self.base_dir)
        module_name = rel_path.replace(os.sep, ".").rstrip(".py")
        if module_name.endswith("."):
            module_name = module_name[:-1]
        return module_name, imports

    def build_dependency_graph(self, python_files):
        graph = nx.DiGraph()
        print(f"Found {len(python_files)} Python files.\n")

        for file_path in python_files:
            module, imports = self.parse_imports(file_path)
            graph.add_node(module)
            for imp in imports:
                graph.add_edge(module, imp)

        return graph 