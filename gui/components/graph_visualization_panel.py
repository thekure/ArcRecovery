from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
from pyvis.network import Network
from collections import defaultdict

from Model.graph_builder import get_dependencies_digraph
from Model.hierarchy import ModuleHierarchy
from constants import HTML_OUTPUT_FOLDER, ASSETS_FOLDER
from ..utils.pyvis_assets import ensure_pyvis_assets_available, fix_html_asset_references

class GraphVisualizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.graph = None
        self.hierarchy = None
        self.parent = parent
        self.ensure_folders_exist()
        
        # Remove border around the group box
        self.setStyleSheet("QGroupBox { border: none; }")
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create a web view for the pyvis visualization
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)
        
        # Fill the entire space with the web view
        layout.addWidget(self.web_view)
        
        # Set layout margins to zero to maximize visualization area
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
    def ensure_folders_exist(self):
        """Make sure the output and assets folders exist"""
        os.makedirs(HTML_OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(ASSETS_FOLDER, exist_ok=True)
        # Ensure we have the necessary pyvis assets
        ensure_pyvis_assets_available()
    
    def visualize_root_level(self):
        """Visualize the root level of the repository graph"""
        if not self.graph or not self.hierarchy:
            # If no graph data, show an empty visualization
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
        
        # Get root level view
        root_view = self.hierarchy.get_level_view('')
        
        # Add package nodes (orange boxes)
        packages = list(root_view['packages'])
        for package in packages:
            net.add_node(package, label=package, title=package, 
                        color="#ff9900", shape="box", 
                        size=25)
        
        # Add module nodes (blue circles) 
        modules = []
        for module in root_view['modules']:
            module_name = module.name
            modules.append(module_name)
            net.add_node(module_name, label=module_name, title=module_name, 
                        color="#66ccff", shape="dot",
                        size=15)
        
        # Use the existing aggregated dependencies method
        dependencies = self.hierarchy.get_aggregated_dependencies('')
        
        # Process and add edges
        for (source, target), weight in dependencies.items():
            # Skip nodes that don't exist (they may be filtered out)
            if not net.get_node(source) or not net.get_node(target):
                continue
                
            # Style differently based on node types
            if source in packages and target in packages:
                # Package to package (orange edges)
                net.add_edge(source, target, 
                            label=str(weight),  # Display the dependency count
                            title=f"{source} → {target}: {weight} dependencies",
                            color="#e08214",
                            arrows={'to': True},
                            width=2)  # Fixed width for all edges
            else:
                # Module to package (blue edges)
                net.add_edge(source, target, 
                            label=str(weight),  # Display the dependency count
                            title=f"{source} → {target}: {weight} dependencies",
                            color="#3182bd",
                            arrows={'to': True},
                            width=1.5)  # Fixed width for all edges
        
        try:
            # Save to the HTML output folder
            html_file = os.path.join(HTML_OUTPUT_FOLDER, "root_level_graph.html")
            net.save_graph(html_file)
            
            # Fix HTML to use local assets instead of CDN
            fix_html_asset_references(html_file)
            
            # Load the HTML file in the web view
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath(html_file)))
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Visualization Error", f"Error generating visualization: {str(e)}")
    
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