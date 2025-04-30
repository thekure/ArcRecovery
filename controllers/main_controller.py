from PyQt5.QtWidgets import QMessageBox
import networkx as nx

class MainController:
    """
    Controller class that handles the application logic and connects model with view.
    """
    def __init__(self, model, view):
        """Initialize the controller with model and view references."""
        self.model = model
        self.view = view
        self.graph_view = None
        self.original_graph = None
        self.current_package = None
        self.navigation_history = []
        
        # Connect view signals to controller methods
        self.connect_signals()
    
    def connect_signals(self):
        """Connect view signals to controller methods."""
        self.view.clone_clicked.connect(self.clone_repository)
        self.view.analyze_clicked.connect(self.analyze_repository)
        self.view.clear_clicked.connect(self.clear_repository)
        self.view.filter_changed.connect(self.apply_filters)
        self.view.clear_filter_clicked.connect(self.clear_filters)
        self.view.back_clicked.connect(self.navigate_back)
        self.view.root_clicked.connect(self.navigate_to_root)
        
    def set_graph_view(self, graph_view):
        """Set the graph view reference and connect its signals."""
        self.graph_view = graph_view
        self.graph_view.package_clicked.connect(self.drill_down_to_package)
    
    def clone_repository(self, repo_url):
        """Clone a repository from the given URL."""
        success, message = self.model.clone_repository(repo_url)
        self.view.set_result_text(message)
        
        # Enable analyze button if clone was successful
        self.view.set_analyze_enabled(success)
    
    def analyze_repository(self):
        """Analyze the repository dependencies."""
        success, message = self.model.analyze_dependencies()
        
        if success:
            self.view.set_result_text(message)
            self.original_graph = self.model.get_dependency_graph()
            
            # Apply initial filters and update the graph view
            self.apply_filters("", True, False, True, 1)
        else:
            self.view.set_result_text(message)
            QMessageBox.warning(self.view, "Analysis Error", message)
    
    def clear_repository(self):
        """Clear the repository directory."""
        success, message = self.model.clear_repository()
        self.view.set_result_text(message)
        
        # Reset navigation
        self.current_package = None
        self.navigation_history = []
        self.view.set_navigation_state(False, True)
        self.view.set_location_label("Root level")
        
        # Reset graph view
        if self.graph_view:
            self.graph_view.set_graph(nx.DiGraph())
        
        # Disable analyze button
        self.view.set_analyze_enabled(False)
    
    def apply_filters(self, pattern, hide_external, only_connected, group_by_pkg, node_size_metric):
        """Apply filters to the dependency graph."""
        if not self.original_graph:
            return
        
        # Make a copy of the original graph for filtering
        filtered_graph = self.original_graph.copy()
        
        # Apply text pattern filter
        if pattern:
            try:
                import re
                regex = re.compile(f".*{pattern}.*", re.IGNORECASE)
                
                # Filter nodes that match the pattern
                nodes_to_keep = [node for node in filtered_graph.nodes() 
                              if regex.match(str(node))]
                filtered_graph = filtered_graph.subgraph(nodes_to_keep).copy()
            except:
                self.view.set_result_text("Invalid regex pattern")
                return
        
        # Hide external dependencies
        if hide_external and self.current_package is None:
            # This would be more complex in a real implementation
            # Here we just keep nodes that start with "app"
            nodes_to_keep = [node for node in filtered_graph.nodes() 
                           if str(node).startswith("app")]
            filtered_graph = filtered_graph.subgraph(nodes_to_keep).copy()
        
        # Remove disconnected nodes
        if only_connected:
            nodes_to_keep = [node for node, degree in filtered_graph.degree() 
                           if degree > 0]
            filtered_graph = filtered_graph.subgraph(nodes_to_keep).copy()
        
        # Group by package
        if group_by_pkg:
            # Add package information to nodes
            for node in filtered_graph.nodes():
                node_str = str(node)
                if "." in node_str:
                    parent_pkg = node_str.rsplit(".", 1)[0]
                    filtered_graph.nodes[node]["parent_package"] = parent_pkg
                    filtered_graph.nodes[node]["is_submodule"] = True
        
        # Set node size based on metric
        if node_size_metric > 0:
            for node in filtered_graph.nodes():
                if node_size_metric == 1:  # Connections count
                    filtered_graph.nodes[node]["size"] = filtered_graph.degree(node)
                elif node_size_metric == 2:  # PageRank
                    # This would be calculated in a real implementation
                    filtered_graph.nodes[node]["size"] = 1
        
        # Update the graph view
        if self.graph_view:
            self.graph_view.set_graph(filtered_graph)
            
            # Update result text
            self.view.set_result_text(f"Showing {len(filtered_graph.nodes())} modules")
    
    def clear_filters(self):
        """Clear all filters and reset to the original graph."""
        # Reset current package and navigation history
        self.current_package = None
        self.navigation_history = []
        self.view.set_navigation_state(False, True)
        self.view.set_location_label("Root level")
        
        # Apply minimal filtering with default settings
        self.apply_filters("", False, False, False, 0)
    
    def navigate_back(self):
        """Navigate back to the previous package."""
        if self.navigation_history:
            # Pop the last package from history
            prev_package = self.navigation_history.pop()
            
            # Update current package
            self.current_package = prev_package
            
            # Update navigation buttons
            self.view.set_navigation_state(bool(self.navigation_history), False)
            
            # Update location label
            self.view.set_location_label(prev_package if prev_package else "Root level")
            
            # Apply filters in the context of this package
            self.drill_down_to_package(prev_package, update_history=False)
    
    def navigate_to_root(self):
        """Navigate to the root level view."""
        # Reset current package and history
        self.current_package = None
        self.navigation_history = []
        
        # Update navigation buttons
        self.view.set_navigation_state(False, True)
        
        # Update location label
        self.view.set_location_label("Root level")
        
        # Apply filters to show the root level
        self.apply_filters("", True, False, True, 1)
    
    def drill_down_to_package(self, package_name, members=None, update_history=True):
        """Drill down to view the contents of a package."""
        # Add current package to history if needed
        if update_history and self.current_package is not None:
            self.navigation_history.append(self.current_package)
        
        # Update current package
        self.current_package = package_name
        
        # Update navigation buttons
        self.view.set_navigation_state(bool(self.navigation_history), False)
        
        # Update location label
        self.view.set_location_label(package_name if package_name else "Root level")
        
        # Get package modules from the model
        modules = self.model.get_package_modules(package_name)
        
        if modules:
            # Filter the original graph to only show package modules
            subgraph_nodes = modules + [package_name] if package_name else modules
            package_graph = self.original_graph.subgraph(subgraph_nodes).copy()
            
            # Mark package nodes
            for node in package_graph.nodes():
                node_str = str(node)
                if node_str == package_name:
                    # Mark this as the current package
                    package_graph.nodes[node]["is_current_package"] = True
                elif "." in node_str and len(node_str.split(".")) > len(package_name.split(".")) + 1:
                    # Mark as deeper nested modules (could be grouped)
                    package_graph.nodes[node]["is_nested"] = True
                    parent_parts = node_str.split(".")
                    # Get the immediate parent package
                    parent_pkg = ".".join(parent_parts[:-1])
                    package_graph.nodes[node]["parent_package"] = parent_pkg
            
            # Update the graph view
            if self.graph_view:
                self.graph_view.set_graph(package_graph)
                self.view.set_result_text(f"Showing {len(package_graph.nodes())} modules in {package_name}")
        else:
            self.view.set_result_text(f"No modules found in package {package_name}") 