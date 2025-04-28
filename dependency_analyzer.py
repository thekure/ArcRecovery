import os
import ast
import networkx as nx

class DependencyAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            raise ValueError(f"Base directory {base_dir} does not exist")

    def parse_imports(self, file_path):
        imports = []
        module_name = ""
        
        try:
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} does not exist")
                return "", []

            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=file_path)
                except SyntaxError as e:
                    print(f"Syntax error in {file_path}: {e}")
                    return "", []
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception as e:
            print(f"Failed to parse {file_path}: {e}")
            return "", []
        
        # Map imports to local modules if possible
        try:
            rel_path = os.path.relpath(file_path, self.base_dir)
            module_name = rel_path.replace(os.sep, ".").rstrip(".py")
            if module_name.endswith("."):
                module_name = module_name[:-1]
        except Exception as e:
            print(f"Failed to process module name for {file_path}: {e}")
            return "", []

        return module_name, imports

    def build_dependency_graph(self, python_files):
        if not python_files:
            raise ValueError("No Python files provided for analysis")

        graph = nx.DiGraph()
        print(f"Found {len(python_files)} Python files.\n")

        for file_path in python_files:
            module, imports = self.parse_imports(file_path)
            if module:  # Only add nodes for successfully parsed modules
                graph.add_node(module)
                for imp in imports:
                    if imp:  # Only add edges for valid imports
                        graph.add_edge(module, imp)

        if len(graph.nodes) == 0:
            raise ValueError("No valid modules found in the provided files")

        return graph 