import sys
import os
import shutil
import re
import networkx as nx
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QMessageBox, QGroupBox,
                           QCheckBox, QComboBox)

from repository_manager import RepositoryManager
from dependency_analyzer import DependencyAnalyzer
from graph_visualizer import GraphView

class ModuleViewerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Module Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize attributes
        self.repo_manager = None
        self.analyzer = None
        self.graph_view = None
        self.original_graph = None  # Store the original graph for filter reset
        self.current_package = None  # Current package being viewed
        self.navigation_history = []  # Stack to track navigation history
        self.module_hierarchy = {}  # Store the module hierarchy

        # Main layout will be horizontal split
        self.main_layout = QHBoxLayout()
        
        # Left panel for controls
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_panel.setLayout(self.control_layout)
        self.control_panel.setMaximumWidth(300)
        
        # Right panel for graph
        self.graph_panel = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_panel.setLayout(self.graph_layout)
        
        self.setup_ui()
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.graph_panel)
        self.setLayout(self.main_layout)
        self.check_directory()

    def setup_ui(self):
        # Repository controls
        repo_group = QGroupBox("Repository Controls")
        repo_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setText("https://github.com/zeeguu/api")
        repo_layout.addWidget(QLabel("GitHub Repo URL:"))
        repo_layout.addWidget(self.url_input)

        self.clone_button = QPushButton("Clone")
        self.clone_button.clicked.connect(self.clone_repo)
        repo_layout.addWidget(self.clone_button)

        self.analyse_button = QPushButton("Analyse")
        self.analyse_button.clicked.connect(self.analyse_repo)
        repo_layout.addWidget(self.analyse_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_directory)
        repo_layout.addWidget(self.clear_button)

        repo_group.setLayout(repo_layout)
        self.control_layout.addWidget(repo_group)

        # Filter controls
        filter_group = QGroupBox("Module Filters")
        filter_layout = QVBoxLayout()
        
        self.module_filter_input = QLineEdit()
        self.module_filter_input.setPlaceholderText("e.g., api.* or core.*")
        self.module_filter_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Module Name Pattern:"))
        filter_layout.addWidget(self.module_filter_input)
        
        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.clear_filter_button)

        # Add filter options with checkboxes
        filter_layout.addWidget(QLabel("Filter Options:"))
        
        self.hide_external_deps = QCheckBox("Hide External Dependencies")
        self.hide_external_deps.setToolTip("Hide all modules not defined in the repository")
        self.hide_external_deps.stateChanged.connect(self.apply_filters)
        self.hide_external_deps.setChecked(True)  # Enable by default
        filter_layout.addWidget(self.hide_external_deps)
        
        self.group_by_package = QCheckBox("Group by Package")
        self.group_by_package.setToolTip("Group nodes by their package name at each level")
        self.group_by_package.stateChanged.connect(self.apply_filters)
        self.group_by_package.setChecked(True)  # Enable by default
        filter_layout.addWidget(self.group_by_package)
        
        self.only_show_connected = QCheckBox("Only Show Connected Modules")
        self.only_show_connected.setToolTip("Hide modules with no connections")
        self.only_show_connected.stateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.only_show_connected)
        
        # Node size options
        filter_layout.addWidget(QLabel("Node Size Based On:"))
        self.node_size_metric = QComboBox()
        self.node_size_metric.addItems(["Uniform Size", "Connections Count", "Importance (PageRank)"])
        self.node_size_metric.setCurrentIndex(1)  # Set Connections Count as default
        self.node_size_metric.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.node_size_metric)

        filter_group.setLayout(filter_layout)
        self.control_layout.addWidget(filter_group)

        # Navigation controls
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout()
        
        self.current_location_label = QLabel("Current: Root level")
        nav_layout.addWidget(self.current_location_label)
        
        nav_buttons = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.navigate_back)
        self.back_button.setEnabled(False)
        nav_buttons.addWidget(self.back_button)
        
        self.root_button = QPushButton("Root")
        self.root_button.clicked.connect(self.navigate_to_root)
        self.root_button.setEnabled(False)
        nav_buttons.addWidget(self.root_button)
        
        nav_layout.addLayout(nav_buttons)
        
        nav_group.setLayout(nav_layout)
        self.control_layout.addWidget(nav_group)

        # Status label
        self.result_label = QLabel("")
        self.control_layout.addWidget(self.result_label)

    def navigate_back(self):
        """Go back to the previous view in the navigation history."""
        if self.navigation_history:
            prev_package = self.navigation_history.pop()
            self.drill_down_to_package(prev_package, update_history=False)
            
            # Enable/disable navigation buttons
            self.back_button.setEnabled(bool(self.navigation_history))
            self.update_location_label()

    def navigate_to_root(self):
        """Return to the root level view."""
        # Clear history and reset to original filtered view
        self.navigation_history = []
        self.current_package = None
        self.back_button.setEnabled(False)
        self.root_button.setEnabled(False)
        
        # Apply current filters to the original graph
        self.apply_filters()
        self.update_location_label()

    def update_location_label(self):
        """Update the label showing current navigation location."""
        if self.current_package:
            self.current_location_label.setText(f"Current: {self.current_package}")
        else:
            self.current_location_label.setText("Current: Root level")

    def clear_filter(self):
        self.module_filter_input.clear()
        self.hide_external_deps.setChecked(False)
        self.only_show_connected.setChecked(False)
        self.group_by_package.setChecked(False)
        self.node_size_metric.setCurrentIndex(0)
        if self.original_graph and self.graph_view:
            # Clear navigation history when filters are cleared
            self.navigation_history = []
            self.current_package = None
            self.back_button.setEnabled(False)
            self.root_button.setEnabled(False)
            self.update_location_label()
            
            self.update_graph_view(self.original_graph)
            self.result_label.setText(f"Showing all {len(self.original_graph.nodes())} modules")

    def update_graph_view(self, graph):
        if self.graph_view:
            # Disconnect any previous signal connections
            try:
                self.graph_view.package_clicked.disconnect()
            except:
                pass
            
            self.graph_layout.removeWidget(self.graph_view)
            self.graph_view.deleteLater()
            
        # Apply node size metric if selected
        node_size_option = self.node_size_metric.currentIndex()
        if node_size_option > 0:
            self.calculate_node_metrics(graph, node_size_option)
            
        # Create new graph view with edge_weights enabled
        self.graph_view = GraphView(graph, use_edge_weights=True)
        
        # Connect the package_clicked signal
        self.graph_view.package_clicked.connect(self.drill_down_to_package)
        
        self.graph_layout.addWidget(self.graph_view)

    def calculate_node_metrics(self, graph, option):
        # Calculate metrics for node sizing
        try:
            if option == 1:  # Connections count
                # Calculate degree (number of connections) for each node
                for node in graph.nodes():
                    graph.nodes[node]['size'] = graph.degree(node)
            elif option == 2:  # PageRank importance
                # Calculate PageRank for the graph
                pagerank = nx.pagerank(graph)
                for node, rank in pagerank.items():
                    if node in graph.nodes():
                        graph.nodes[node]['size'] = rank * 1000  # Scale up for visibility
        except Exception as e:
            print(f"Error calculating node metrics: {e}")

    def apply_filters(self):
        if not self.original_graph:
            return
            
        pattern = self.module_filter_input.text().strip()
        hide_external = self.hide_external_deps.isChecked()
        only_connected = self.only_show_connected.isChecked()
        group_by_package = self.group_by_package.isChecked()
        
        # Start with a copy of the original graph
        filtered_graph = self.original_graph.copy()
        
        # Apply text filter if provided
        if pattern:
            try:
                # Use regex pattern that matches anywhere in the string, not just at the beginning
                regex = re.compile(f".*{pattern}.*", re.IGNORECASE)
                
                # Remove nodes that don't match the pattern
                nodes_to_remove = [node for node in filtered_graph.nodes() 
                                 if not regex.match(str(node))]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            except re.error:
                self.result_label.setText("Invalid regex pattern")
                return
        
        # Hide all external dependencies if requested
        if hide_external and filtered_graph.nodes():
            try:
                # Get the repository path to identify local modules
                repo_path = ""
                if self.repo_manager:
                    repo_path = self.repo_manager.get_repo_path()
                
                if repo_path:
                    # Find all Python files in the repository to identify internal modules
                    internal_modules = self.get_internal_modules(repo_path)
                    
                    # Remove all nodes that aren't in the internal_modules set
                    nodes_to_remove = [node for node in filtered_graph.nodes() 
                                     if str(node) not in internal_modules]
                    
                    filtered_graph.remove_nodes_from(nodes_to_remove)
                    print(f"Removed {len(nodes_to_remove)} external modules")
                else:
                    # Fallback method if we don't have the repo path
                    # Try to identify main packages from file structure
                    all_nodes = list(filtered_graph.nodes())
                    
                    # Find the most common top-level packages that have submodules
                    # (likely to be internal packages)
                    potential_internal_packages = {}
                    for node in all_nodes:
                        node_str = str(node)
                        if '.' in node_str:
                            top_level = node_str.split('.')[0]
                            if top_level in potential_internal_packages:
                                potential_internal_packages[top_level] += 1
                            else:
                                potential_internal_packages[top_level] = 1
                    
                    # Keep only packages with multiple modules (likely project modules)
                    internal_packages = [pkg for pkg, count in potential_internal_packages.items() 
                                       if count >= 2]
                    
                    if internal_packages:
                        # Remove nodes that don't belong to the identified internal packages
                        nodes_to_remove = []
                        for node in filtered_graph.nodes():
                            node_str = str(node)
                            # Check if this node belongs to any internal package
                            is_internal = False
                            for pkg in internal_packages:
                                if node_str == pkg or node_str.startswith(f"{pkg}."):
                                    is_internal = True
                                    break
                            
                            if not is_internal:
                                nodes_to_remove.append(node)
                        
                        filtered_graph.remove_nodes_from(nodes_to_remove)
            except Exception as e:
                print(f"Error filtering external dependencies: {e}")
        
        # Remove disconnected nodes if requested
        if only_connected and filtered_graph.nodes():
            nodes_to_remove = [node for node, degree in filtered_graph.degree() if degree == 0]
            filtered_graph.remove_nodes_from(nodes_to_remove)
        
        # Group nodes by filesystem package structure if requested
        if group_by_package and filtered_graph.nodes() and hasattr(self, 'module_hierarchy'):
            try:
                # Determine current package context
                package_context = self.current_package if self.current_package else ""
                grouped_graph = self.group_nodes_by_filesystem(filtered_graph, package_context)
                if grouped_graph and grouped_graph.nodes():
                    filtered_graph = grouped_graph
            except Exception as e:
                print(f"Error grouping nodes by package: {e}")
        
        # Update the visualization
        if len(filtered_graph.nodes()) > 0:
            # Clear navigation when applying new filters
            if self.current_package:
                self.current_package = None
                self.navigation_history = []
                self.back_button.setEnabled(False)
                self.root_button.setEnabled(False)
                self.update_location_label()
                
            self.update_graph_view(filtered_graph)
            self.result_label.setText(f"Showing {len(filtered_graph.nodes())} modules")
        else:
            self.result_label.setText("No modules match the current filters")

    def clear_directory(self):
        dest_dir = "cur_repo"
        if os.path.exists(dest_dir):
            try:
                shutil.rmtree(dest_dir)
                os.makedirs(dest_dir)
                self.result_label.setText("Repository directory cleared successfully!")
                self.check_directory()
            except Exception as e:
                self.result_label.setText(f"Error clearing directory: {str(e)}")
        else:
            self.result_label.setText("No repository directory to clear.")

    def check_directory(self):
        dest_dir = "cur_repo"
        has_contents = os.path.exists(dest_dir) and bool(os.listdir(dest_dir))
        self.analyse_button.setEnabled(has_contents)

    def clone_repo(self):
        repo_url = self.url_input.text()
        self.repo_manager = RepositoryManager(repo_url)

        try:
            self.repo_manager.clone_repo()
            self.result_label.setText("Repository cloned successfully!")
            self.check_directory()
        except Exception as e:
            self.result_label.setText(f"Error cloning repository: {str(e)}")

    def analyse_repo(self):
        if not self.repo_manager:
            self.repo_manager = RepositoryManager(self.url_input.text())

        try:
            python_files = self.repo_manager.find_python_files()
            if not python_files:
                self.result_label.setText("No Python files found in the repository.")
                return

            self.analyzer = DependencyAnalyzer(self.repo_manager.get_repo_path())
            try:
                # Debug output
                print(f"Found {len(python_files)} Python files")
                
                # Build the dependency graph
                graph = self.analyzer.build_dependency_graph(python_files)
                print(f"Success! Built dependency graph with {len(graph.nodes)} modules")

                # Store the original graph for filtering
                self.original_graph = graph
                
                # Debug: Log all nodes in the graph
                print("Modules in graph:")
                for i, node in enumerate(sorted([str(n) for n in graph.nodes()])):
                    if i < 20 or i > len(graph.nodes()) - 5:  # Show first 20 and last 5
                        print(f"  {node}")
                    elif i == 20:
                        print(f"  ... ({len(graph.nodes()) - 25} more modules) ...")
                
                # Build module hierarchy from filesystem structure
                self.module_hierarchy = self.build_module_hierarchy(python_files)
                
                # Debug: Log the top-level packages
                print("Top-level packages in hierarchy:")
                for pkg in sorted(self.module_hierarchy.keys()):
                    if pkg != "__modules":
                        # Count modules in each package
                        module_count = self._count_modules_in_package(pkg)
                        print(f"  {pkg}: {module_count} modules")

                # Display success message
                self.result_label.setText(f"Success! {len(graph.nodes)} modules found.")

                if self.graph_view:
                    self.graph_layout.removeWidget(self.graph_view)
                    self.graph_view.deleteLater()

                # Apply default filters
                self.apply_filters()

            except ValueError as e:
                self.result_label.setText(f"Analysis error: {str(e)}")
            except Exception as e:
                self.result_label.setText(f"Unexpected error during analysis: {str(e)}")

        except Exception as e:
            self.result_label.setText(f"Error accessing repository: {str(e)}")
            
    def _count_modules_in_package(self, pkg, visited=None):
        """Helper to count all modules in a package recursively."""
        if visited is None:
            visited = set()
            
        if pkg in visited:
            return 0
            
        visited.add(pkg)
        count = 0
        
        # Get the package dict
        parts = pkg.split('.')
        current = self.module_hierarchy
        for part in parts:
            if part not in current:
                return 0
            current = current[part]
        
        # Count direct modules
        if "__modules" in current:
            count += len(current["__modules"])
        
        # Recursively count subpackages
        for key in current:
            if key != "__modules":
                sub_pkg = f"{pkg}.{key}" if pkg else key
                count += self._count_modules_in_package(sub_pkg, visited)
                
        return count

    def build_module_hierarchy(self, python_files):
        """Build a dictionary representing the module hierarchy based on filesystem structure."""
        hierarchy = {"__modules": []}  # Start with an empty root that can have modules
        repo_path = self.repo_manager.get_repo_path()
        
        # First, find all valid Python module paths
        all_modules = set()
        for file_path in python_files:
            # Skip __pycache__ 
            if "__pycache__" in file_path:
                continue
                
            # Get the relative path from the repository root
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Convert to module path notation
            module_path = rel_path.replace(os.sep, ".").rstrip(".py")
            
            # Special case for __init__.py files
            if module_path.endswith("__init__"):
                # For __init__.py files, the module name is the directory
                module_path = os.path.dirname(rel_path).replace(os.sep, ".")
                if not module_path:  # Root level __init__.py
                    continue
            
            all_modules.add(module_path)
        
        # Now construct the hierarchy
        for module_path in sorted(all_modules):  # Sort to process parents before children
            parts = module_path.split(".")
            current_dict = hierarchy
            for i, part in enumerate(parts):
                # Build the path as we go
                current_path = ".".join(parts[:i+1])
                
                # Create the nested dictionary if it doesn't exist
                if part not in current_dict:
                    current_dict[part] = {"__modules": []}
                
                # Move deeper into the hierarchy
                current_dict = current_dict[part]
                
                # If this is a full module path, add it to __modules at its level
                if current_path == module_path:
                    if "__modules" not in current_dict:
                        current_dict["__modules"] = []
                    if module_path not in current_dict["__modules"]:
                        current_dict["__modules"].append(module_path)
        
        # Debug output
        print(f"Built module hierarchy with {len(hierarchy) - 1} top-level packages")
        return hierarchy
    
    def get_package_modules(self, package_name):
        """Get all modules in a package and its subpackages recursively."""
        modules = []
        
        # Navigate to the correct place in the hierarchy
        if not package_name:
            # Root level - get all top-level packages and direct modules
            current_dict = self.module_hierarchy
            
            # Add direct modules at root level
            if "__modules" in current_dict:
                modules.extend(current_dict["__modules"])
            
            # Add top-level packages (skip the __modules key)
            for key in current_dict:
                if key != "__modules":
                    modules.append(key)
        else:
            # Split the package name into parts
            parts = package_name.split(".")
            current_dict = self.module_hierarchy
            
            # Navigate to the target package
            for part in parts:
                if part not in current_dict:
                    return modules  # Package not found
                current_dict = current_dict[part]
            
            # Add direct modules in this package
            if "__modules" in current_dict:
                modules.extend(current_dict["__modules"])
            
            # Add all subpackages
            for key in current_dict:
                if key != "__modules":
                    subpackage_name = f"{package_name}.{key}"
                    modules.append(subpackage_name)
                    # Recursively get modules from subpackages
                    submodules = self.get_package_modules(subpackage_name)
                    modules.extend(submodules)
        
        return modules

    def get_internal_modules(self, repo_path):
        """Identify all internal modules defined in the repository."""
        internal_modules = set()
        
        try:
            # Walk through the repository and find all Python files
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                # Process all Python files
                for file in files:
                    if file.endswith('.py'):
                        # Get the full path
                        file_path = os.path.join(root, file)
                        
                        # Convert file path to module path
                        rel_path = os.path.relpath(file_path, repo_path)
                        
                        # Convert file path to module notation
                        if file == '__init__.py':
                            # For __init__.py files, the module name is the directory
                            rel_dir = os.path.dirname(rel_path)
                            if rel_dir:
                                module_path = rel_dir.replace(os.sep, '.')
                                internal_modules.add(module_path)
                        else:
                            # For regular .py files, remove the .py extension
                            module_path = rel_path.replace(os.sep, '.').rsplit('.py', 1)[0]
                            internal_modules.add(module_path)
            
            # Add top-level modules (those without dots)
            top_level_modules = {m.split('.')[0] for m in internal_modules if '.' in m}
            internal_modules.update(top_level_modules)
            
            print(f"Found {len(internal_modules)} internal modules in the repository")
            
        except Exception as e:
            print(f"Error identifying internal modules: {e}")
        
        return internal_modules

    def drill_down_to_package(self, package_name, members=None, update_history=True):
        """Drill down to view the contents of a package."""
        print(f"Drilling down to package: {package_name}")
        
        # If members list wasn't provided, try to find it in the current graph
        if members is None and self.graph_view:
            for node, data in self.graph_view.graph.nodes(data=True):
                if str(node) == package_name and 'members' in data:
                    members = data['members']
                    break
        
        # Update navigation history if needed
        if update_history and self.current_package is not None:
            self.navigation_history.append(self.current_package)
            
        # Update current package
        self.current_package = package_name
        
        # Enable navigation buttons
        self.back_button.setEnabled(bool(self.navigation_history))
        self.root_button.setEnabled(True)
        
        # Update location label
        self.update_location_label()
            
        # Create a filtered graph showing only direct children of this package
        if self.original_graph:
            # Get only the direct children of this package from the module hierarchy
            direct_children = self.get_direct_children(package_name)
            
            if not direct_children:
                # Debug output to help diagnose the problem
                print(f"No direct children found for {package_name}")
                print(f"Available packages: {list(self.module_hierarchy.keys())}")
                
                self.result_label.setText(f"No direct modules found in package {package_name}")
                return
            
            print(f"Found {len(direct_children)} direct children for {package_name}: {direct_children[:5]}...")
                
            # Start with the original graph and extract the subgraph we need
            subgraph_nodes = []
            
            # First, add all direct children
            for node in self.original_graph.nodes():
                node_str = str(node)
                if node_str in direct_children or node_str == package_name:
                    subgraph_nodes.append(node)
            
            # Create a subgraph with just the nodes we want
            package_graph = self.original_graph.subgraph(subgraph_nodes).copy()
            
            # Apply current filters to the package subgraph
            hide_external = self.hide_external_deps.isChecked()
            only_connected = self.only_show_connected.isChecked()
            group_by_package = self.group_by_package.isChecked()
            
            # Remove disconnected nodes if requested
            if only_connected and package_graph.nodes():
                nodes_to_remove = [node for node, degree in package_graph.degree() if degree == 0]
                package_graph.remove_nodes_from(nodes_to_remove)
            
            # Special handling to ensure subpackages are properly identified
            for node in package_graph.nodes():
                node_str = str(node)
                if node_str != package_name:
                    # Check if this is a subpackage by looking for deeper nodes
                    for child in self.original_graph.nodes():
                        child_str = str(child)
                        if child_str.startswith(f"{node_str}."):
                            # Mark this as a package with deeper content
                            package_graph.nodes[node]['is_package'] = True
                            package_graph.nodes[node]['has_children'] = True
                            break
            
            # Apply grouping if enabled
            if group_by_package and package_graph.nodes() and hasattr(self, 'module_hierarchy'):
                try:
                    grouped_graph = self.group_nodes_by_filesystem(package_graph, package_name)
                    if grouped_graph and grouped_graph.nodes():
                        package_graph = grouped_graph
                except Exception as e:
                    print(f"Error grouping nodes in subpackage: {e}")
            
            # Update the view with this subgraph
            self.update_graph_view(package_graph)
            self.result_label.setText(f"Showing {len(package_graph.nodes())} direct submodules in {package_name}")
        else:
            self.result_label.setText("Error: No graph data available")
            
    def get_direct_children(self, package_name):
        """Get only the direct children of a package (not recursive)."""
        direct_children = []
        
        if not package_name:
            # Root level - get all top-level packages/modules
            for key in self.module_hierarchy.keys():
                if key and key != "__modules":
                    direct_children.append(key)
            # Also add top-level modules
            if "__modules" in self.module_hierarchy:
                direct_children.extend(self.module_hierarchy["__modules"])
        else:
            # Split package name into parts
            parts = package_name.split(".")
            current_dict = self.module_hierarchy
            
            # Navigate to the right package in the hierarchy
            found = True
            for i, part in enumerate(parts):
                if part not in current_dict:
                    print(f"Cannot find part '{part}' in the module hierarchy at depth {i}")
                    print(f"Available keys: {list(current_dict.keys())}")
                    found = False
                    break
                current_dict = current_dict[part]
            
            if not found:
                # Try a fallback approach
                print(f"Using fallback approach for {package_name}")
                prefix = f"{package_name}."
                for node in self.original_graph.nodes():
                    node_str = str(node)
                    if node_str.startswith(prefix):
                        # Get the next part after the prefix
                        rest = node_str[len(prefix):]
                        if "." in rest:
                            # This is a deeper submodule - extract just the next level
                            next_part = f"{prefix}{rest.split('.')[0]}"
                            if next_part not in direct_children:
                                direct_children.append(next_part)
                        else:
                            # This is a direct module
                            direct_children.append(node_str)
            else:
                # Add direct modules (files) in this package
                if "__modules" in current_dict:
                    direct_children.extend(current_dict["__modules"])
                
                # Add direct subpackages (directories)
                for key in current_dict:
                    if key != "__modules":
                        direct_children.append(f"{package_name}.{key}")
        
        return direct_children

    def group_nodes_by_filesystem(self, graph, current_package=""):
        """Group nodes based on the filesystem structure."""
        if not graph.nodes() or not hasattr(self, 'module_hierarchy'):
            return graph
            
        # Create a new graph for the grouped nodes
        grouped_graph = nx.DiGraph()
        
        # Get all visible nodes in the graph
        visible_nodes = set(str(node) for node in graph.nodes())
        
        # Filter visible nodes to only those in the current package
        if current_package:
            nodes_in_current_pkg = {node for node in visible_nodes 
                                if node == current_package or 
                                   node.startswith(f"{current_package}.")}
        else:
            nodes_in_current_pkg = visible_nodes
        
        # Find direct subpackages at the current level
        subpackages = set()
        direct_modules = set()
        
        # Identify direct subpackages at the current level
        for node in nodes_in_current_pkg:
            node_str = str(node)
            
            # Skip the current package itself
            if node_str == current_package:
                continue
                
            if current_package:
                # Inside a package - find direct children
                prefix = f"{current_package}."
                if node_str.startswith(prefix):
                    # Extract the next part
                    remaining = node_str[len(prefix):]
                    if "." in remaining:
                        # This is a deeper subpackage - extract just the next level
                        next_part = remaining.split(".", 1)[0]
                        subpackage = f"{prefix}{next_part}"
                        subpackages.add(subpackage)
                    else:
                        # This is a direct module
                        direct_modules.add(node_str)
            else:
                # At root level - find top-level packages and modules
                if "." in node_str:
                    # This belongs to a package
                    top_pkg = node_str.split(".", 1)[0]
                    subpackages.add(top_pkg)
                else:
                    # This is a top-level module
                    direct_modules.add(node_str)
        
        # Track which modules belong to which subpackage
        package_members = {pkg: [] for pkg in subpackages}
        
        # Categorize all nodes
        for node in nodes_in_current_pkg:
            node_str = str(node)
            
            # Skip nodes we've already processed or the current package
            if node_str == current_package or node_str in direct_modules:
                continue
                
            if node_str in subpackages:
                continue
                
            # Find which subpackage this node belongs to
            for pkg in subpackages:
                if node_str.startswith(f"{pkg}."):
                    package_members[pkg].append(node_str)
                    break
        
        # Count all members (including deeper ones) for each package
        package_all_members = {}
        for pkg in subpackages:
            # Find all members in the complete graph, not just the current view
            all_members = [str(node) for node in self.original_graph.nodes() 
                           if str(node).startswith(f"{pkg}.") or str(node) == pkg]
            package_all_members[pkg] = all_members
            
            # Debug info
            print(f"Package {pkg} has {len(all_members)} total submodules")
        
        # Add direct modules to the graph
        for node in direct_modules:
            grouped_graph.add_node(node)
            # Preserve node attributes from original graph
            if node in graph.nodes():
                for key, value in graph.nodes[node].items():
                    grouped_graph.nodes[node][key] = value
        
        # Add current package if it exists in the graph
        if current_package and current_package in graph.nodes():
            grouped_graph.add_node(current_package)
            for key, value in graph.nodes[current_package].items():
                grouped_graph.nodes[current_package][key] = value
        
        # Create package nodes for subpackages - these should be clickable
        for pkg, members in package_members.items():
            # Get all direct submodules (not further nested)
            direct_submodules = [m for m in members if m.count('.') == pkg.count('.') + 1]
            
            # Add the subpackage node
            grouped_graph.add_node(pkg)
            
            # Mark this as a package node
            grouped_graph.nodes[pkg]['is_package'] = True
            grouped_graph.nodes[pkg]['members'] = members + [pkg]
            grouped_graph.nodes[pkg]['is_expandable'] = True
            
            # Store the full count of all members (including deeper ones)
            all_members = package_all_members.get(pkg, [])
            grouped_graph.nodes[pkg]['total_members'] = len(all_members)
            grouped_graph.nodes[pkg]['size'] = max(len(all_members), 1)  # Size based on total
        
        # Add subpackage nodes without members but that were directly identified
        for pkg in subpackages:
            if pkg not in grouped_graph.nodes():
                grouped_graph.add_node(pkg)
                grouped_graph.nodes[pkg]['is_package'] = True
                grouped_graph.nodes[pkg]['is_expandable'] = True
                
                # Find all members in the complete graph, not just the current view
                all_members = [str(node) for node in self.original_graph.nodes() 
                               if str(node).startswith(f"{pkg}.") or str(node) == pkg]
                
                # Check if there are deeper modules in the original graph
                has_children = len(all_members) > 1  # More than just itself
                grouped_graph.nodes[pkg]['has_children'] = has_children
                grouped_graph.nodes[pkg]['total_members'] = len(all_members)
                grouped_graph.nodes[pkg]['size'] = max(len(all_members), 1)
                grouped_graph.nodes[pkg]['members'] = [pkg]
        
        # Process edges to preserve connections
        for u, v in graph.edges():
            u_str = str(u)
            v_str = str(v)
            
            # Find where these nodes should be in the grouped graph
            u_grouped = u_str
            v_grouped = v_str
            
            # Check if either node belongs to a package
            for pkg, members in package_members.items():
                if u_str in members:
                    u_grouped = pkg
                if v_str in members:
                    v_grouped = pkg
            
            # Add the edge if both nodes exist
            if u_grouped in grouped_graph.nodes() and v_grouped in grouped_graph.nodes():
                if u_grouped != v_grouped:  # Avoid self-loops
                    grouped_graph.add_edge(u_grouped, v_grouped)
        
        return grouped_graph

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ModuleViewerApp()
    viewer.show()
    sys.exit(app.exec_()) 