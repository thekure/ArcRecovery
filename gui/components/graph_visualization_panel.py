from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QMessageBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import pyqtSlot
import os
import json
from pyvis.network import Network
from collections import defaultdict

from Model.graph_builder import get_dependencies_digraph
from Model.hierarchy import ModuleHierarchy
from constants import HTML_OUTPUT_FOLDER, ASSETS_FOLDER
from ..utils.pyvis_assets import ensure_pyvis_assets_available, fix_html_asset_references

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None, panel=None):
        super().__init__(parent)
        self.visualization_panel = panel
        
    def javaScriptConsoleMessage(self, level, message, line, source):
        # We use this to catch console messages from the HTML page
        # This is useful for debugging JavaScript issues
        if 'click event' in message and self.visualization_panel:
            self.visualization_panel.handle_click_event(message)

class GraphVisualizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.graph = None
        self.hierarchy = None
        self.parent = parent
        self.current_path = ''  # Start at root level
        self.navigation_history = []  # To keep track of navigation
        self.ensure_folders_exist()
        
        # Remove border around the group box
        self.setStyleSheet("QGroupBox { border: none; }")
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Add navigation bar with back button
        nav_layout = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setEnabled(False)  # Disabled initially
        self.back_button.clicked.connect(self.navigate_back)
        
        # Path label
        self.path_label = QLabel("Root")
        self.path_label.setStyleSheet("font-weight: bold;")
        
        # Home button
        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self.navigate_home)
        self.home_button.setEnabled(False)  # Disabled initially
        
        # Add to navigation layout
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.path_label)
        nav_layout.addStretch(1)  # Push home button to the right
        nav_layout.addWidget(self.home_button)
        
        # Add navigation layout to main layout
        main_layout.addLayout(nav_layout)
        
        # Create a web view for the pyvis visualization
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)
        
        # Set up a custom page to handle JavaScript events
        # Pass this panel as the visualization_panel so the page can call back
        self.custom_page = CustomWebEnginePage(self.web_view, panel=self)
        self.web_view.setPage(self.custom_page)
        
        # Fill the entire space with the web view
        main_layout.addWidget(self.web_view)
        
        # Set layout margins to zero to maximize visualization area
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(main_layout)
        
    def ensure_folders_exist(self):
        """Make sure the output and assets folders exist"""
        os.makedirs(HTML_OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(ASSETS_FOLDER, exist_ok=True)
        # Ensure we have the necessary pyvis assets
        ensure_pyvis_assets_available()
    
    def handle_click_event(self, message):
        """Handle click events from the graph visualization"""
        try:
            # Extract the clicked node from the message
            # The message format is expected to be: "click event: {node_data_json}"
            start_idx = message.find('{')
            if start_idx > 0:
                node_data = json.loads(message[start_idx:])
                node_id = node_data.get('id')
                
                # Add some protection for null/empty node ids
                if not node_id:
                    return
                    
                print(f"Click on node: {node_id}")
                
                # Check if the clicked node is a package
                if self.is_package(node_id):
                    print(f"Navigating to package: {node_id}")
                    self.navigate_to_package(node_id)
        except Exception as e:
            print(f"Error handling click event: {str(e)}")
    
    def is_package(self, node_id):
        """Check if the given node is a package"""
        # If we're at root level
        if not self.current_path:
            # Check if the node is in the root packages
            root_view = self.hierarchy.get_level_view('')
            return node_id in root_view['packages']
        else:
            # For non-root levels, construct the full package path
            full_path = f"{self.current_path}.{node_id}" if self.current_path else node_id
            
            # Check if this node exists in the graph and is a package
            if full_path in self.graph.nodes and 'module' in self.graph.nodes[full_path]:
                return self.graph.nodes[full_path]['module'].is_package
                
        return False
    
    def navigate_to_package(self, package_name):
        """Navigate to the specified package"""
        # Save current path in history
        self.navigation_history.append(self.current_path)
        
        # Update current path
        if self.current_path:
            self.current_path = f"{self.current_path}.{package_name}"
        else:
            self.current_path = package_name
            
        # Update UI
        self.path_label.setText(self.current_path if self.current_path else "Root")
        self.back_button.setEnabled(True)
        self.home_button.setEnabled(True)
        
        # Visualize the new level
        self.visualize_current_level()
    
    def navigate_back(self):
        """Navigate back to the previous level"""
        if self.navigation_history:
            self.current_path = self.navigation_history.pop()
            self.path_label.setText(self.current_path if self.current_path else "Root")
            
            # Disable back button if we're at root
            if not self.navigation_history:
                self.back_button.setEnabled(False)
                
            # Disable home button if we're at root
            if not self.current_path:
                self.home_button.setEnabled(False)
                
            # Visualize the new level
            self.visualize_current_level()
    
    def navigate_home(self):
        """Navigate back to the root level"""
        self.navigation_history = []
        self.current_path = ''
        self.path_label.setText("Root")
        self.back_button.setEnabled(False)
        self.home_button.setEnabled(False)
        
        # Visualize the root level
        self.visualize_current_level()
    
    def visualize_current_level(self):
        """Visualize the current level based on the current_path"""
        if not self.graph or not self.hierarchy:
            return
            
        # Check if we have required assets
        if not os.path.exists(os.path.join(ASSETS_FOLDER, "vis-network.min.js")):
            if self.parent:
                QMessageBox.warning(self.parent, "Missing Assets", 
                                   "Visualization assets are missing. Install the 'requests' library and try again.")
            return
            
        # Create a pyvis network
        net = Network(height="100%", width="100%", notebook=False, directed=True, bgcolor="#ffffff")
        
        # Configure network options for better visualization
        net.set_options("""
        var options = {
            "nodes": {
                "font": {
                    "size": 14,
                    "face": "Tahoma"
                }
            },
            "edges": {
                "color": {
                    "inherit": false
                },
                "smooth": {
                    "enabled": true,
                    "type": "dynamic"
                },
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.5
                    }
                },
                "font": {
                    "size": 12,
                    "color": "#000000",
                    "align": "middle",
                    "background": "rgba(255, 255, 255, 0.7)",
                    "strokeWidth": 0,
                    "strokeColor": "#ffffff"
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 150,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "enabled": true,
                    "iterations": 1000,
                    "updateInterval": 25
                }
            },
            "interaction": {
                "navigationButtons": true,
                "keyboard": true,
                "hover": true
            }
        }
        """)
        
        # Get current level view
        level_view = self.hierarchy.get_level_view(self.current_path)
        
        # Add package nodes (orange boxes)
        packages = list(level_view['packages'])
        for package in packages:
            # For non-root levels, we need to ensure the correct node ID is used
            node_id = package  # Just the package name, not the full path
            full_path = f"{self.current_path}.{package}" if self.current_path else package
            
            net.add_node(node_id, label=node_id, title=full_path, 
                        color="#ff9900", shape="box", 
                        size=25)
        
        # Add module nodes (blue circles) 
        modules = []
        for module in level_view['modules']:
            module_name = module.name
            # Strip the prefix to get just the module name for this level
            if self.current_path and module_name.startswith(self.current_path + '.'):
                display_name = module_name[len(self.current_path) + 1:]  # +1 for the dot
            else:
                display_name = module_name
                
            modules.append(display_name)
            net.add_node(display_name, label=display_name, title=module_name, 
                        color="#66ccff", shape="dot",
                        size=15)
        
        # Use the existing aggregated dependencies method
        dependencies = self.hierarchy.get_aggregated_dependencies(self.current_path)
        
        # Process and add edges
        for (source, target), weight in dependencies.items():
            # For non-root levels, we need to adjust the source and target to just the final name part
            source_display = source
            target_display = target
            
            if self.current_path:
                # Handle package->package dependencies
                if source.startswith(self.current_path + '.') and target.startswith(self.current_path + '.'):
                    source_display = source.split('.')[-1]
                    target_display = target.split('.')[-1]
                # Handle module->package dependencies    
                elif source.startswith(self.current_path + '.'):
                    # Module within the current package
                    source_display = source[len(self.current_path) + 1:]
                    if target.startswith(self.current_path + '.'):
                        target_display = target.split('.')[-1]
            
            # Skip nodes that don't exist (they may be filtered out)
            if not net.get_node(source_display) or not net.get_node(target_display):
                continue
                
            # Style differently based on node types
            if (self.current_path and source.startswith(self.current_path + '.') and 
                target.startswith(self.current_path + '.') and 
                source != target):
                # Package to package (orange edges)
                net.add_edge(source_display, target_display, 
                            label=str(weight),  # Display the dependency count
                            title=f"{source} → {target}: {weight} dependencies",
                            color="#e08214",
                            arrows={'to': True},
                            width=2)  # Fixed width for all edges
            else:
                # Module to package (blue edges)
                net.add_edge(source_display, target_display, 
                            label=str(weight),  # Display the dependency count
                            title=f"{source} → {target}: {weight} dependencies",
                            color="#3182bd",
                            arrows={'to': True},
                            width=1.5)  # Fixed width for all edges
        
        try:
            # Save to the HTML output folder
            html_file = os.path.join(HTML_OUTPUT_FOLDER, "current_level_graph.html")
            
            # Generate the graph HTML
            net.save_graph(html_file)
            
            # Add JavaScript to handle clicks and send them to Python
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add click handler before the closing body tag
            click_handler = """
            <script type="text/javascript">
            network.on("click", function(params) {
                if (params.nodes.length > 0) {
                    var node = params.nodes[0];
                    var nodeData = network.body.data.nodes.get(node);
                    console.log("click event: " + JSON.stringify(nodeData));
                }
            });
            </script>
            """
            content = content.replace('</body>', click_handler + '</body>')
            
            # Write back the modified content
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Fix HTML to use local assets instead of CDN
            fix_html_asset_references(html_file)
            
            # Load the HTML file in the web view
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath(html_file)))
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Visualization Error", f"Error generating visualization: {str(e)}")
    
    def visualize_root_level(self):
        """Visualize the root level of the repository graph"""
        self.current_path = ''
        self.navigation_history = []
        self.path_label.setText("Root")
        self.back_button.setEnabled(False)
        self.home_button.setEnabled(False)
        self.visualize_current_level()
    
    def set_graph_data(self, graph=None, hierarchy=None):
        """Set the graph data and trigger visualization"""
        if graph:
            self.graph = graph
        else:
            self.graph = get_dependencies_digraph()
            
        if hierarchy:
            self.hierarchy = hierarchy
        else:
            self.hierarchy = ModuleHierarchy(self.graph)
            
        self.visualize_root_level() 