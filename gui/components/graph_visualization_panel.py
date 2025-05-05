from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
from pyvis.network import Network

from Model.graph_builder import get_dependencies_digraph
from Model.hierarchy import ModuleHierarchy
from constants import HTML_OUTPUT_FOLDER, ASSETS_FOLDER
from ..utils.pyvis_assets import ensure_pyvis_assets_available, fix_html_asset_references

class GraphVisualizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Graph Visualization", parent)
        self.setup_ui()
        self.graph = None
        self.hierarchy = None
        self.parent = parent
        self.ensure_folders_exist()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create a web view for the pyvis visualization
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)
        
        # Initial message
        self.message_label = QLabel("No repository loaded. Please analyze a repository first.")
        layout.addWidget(self.message_label)
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        
    def ensure_folders_exist(self):
        """Make sure the output and assets folders exist"""
        os.makedirs(HTML_OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(ASSETS_FOLDER, exist_ok=True)
        # Ensure we have the necessary pyvis assets
        if not ensure_pyvis_assets_available():
            self.message_label.setText("Warning: Could not prepare visualization assets. Visualizations may not display correctly.")
    
    def visualize_root_level(self):
        """Visualize the root level of the repository graph"""
        if not self.graph or not self.hierarchy:
            self.message_label.setText("No graph data available. Please analyze a repository first.")
            return
        
        # Check if we have required assets
        if not os.path.exists(os.path.join(ASSETS_FOLDER, "vis-network.min.js")):
            if self.parent:
                QMessageBox.warning(self.parent, "Missing Assets", 
                                   "Visualization assets are missing. Install the 'requests' library and try again.")
            self.message_label.setText("Error: Missing required visualization assets.")
            return
            
        # Create a pyvis network
        net = Network(height="500px", width="100%", notebook=False, directed=True)
        
        # Configure network to use local assets
        net.set_options("""
        var options = {
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 0,
                    "springLength": 100,
                    "nodeDistance": 120
                },
                "solver": "hierarchicalRepulsion"
            }
        }
        """)
        
        # Get root level view
        root_view = self.hierarchy.get_level_view('')
        
        # Add package nodes
        for package in root_view['packages']:
            net.add_node(package, label=package, title=package, color="#ff9900", shape="box")
        
        # Add module nodes
        for module in root_view['modules']:
            module_name = module.name
            net.add_node(module_name, label=module_name, title=module_name, color="#66ccff")
        
        # Add dependency edges
        dependencies = self.hierarchy.get_aggregated_dependencies('')
        for (source, target), weight in dependencies.items():
            net.add_edge(source, target, width=weight, title=f"Weight: {weight}")
        
        try:
            # Save to the HTML output folder
            html_file = os.path.join(HTML_OUTPUT_FOLDER, "root_level_graph.html")
            net.save_graph(html_file)
            
            # Fix HTML to use local assets instead of CDN
            fix_html_asset_references(html_file)
            
            # Load the HTML file in the web view
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath(html_file)))
            self.message_label.setText("Graph visualization ready.")
        except Exception as e:
            error_msg = f"Error generating visualization: {str(e)}"
            self.message_label.setText(error_msg)
            if self.parent:
                QMessageBox.critical(self.parent, "Visualization Error", error_msg)
    
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