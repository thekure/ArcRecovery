from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from .components.repository_panel import RepositoryPanel
from .components.filter_panel import FilterPanel
from .components.navigation_panel import NavigationPanel
from .components.graph_visualization_panel import GraphVisualizationPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.navigation_panel = None
        self.result_label = None
        self.graph_visualization_panel = None
        self.filter_panel = None
        self.repository_panel = None
        self.graph_layout = None
        self.graph_panel = None
        self.control_layout = None
        self.control_panel = None
        self.main_layout = None
        self.setWindowTitle("ArcRecovery")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()
        main_widget.setLayout(self.main_layout)
        
        # Left panel for controls
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_panel.setLayout(self.control_layout)
        self.control_panel.setMaximumWidth(300)
        
        # Right panel for graph visualization
        self.graph_panel = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_panel.setLayout(self.graph_layout)

        # Remove margins to maximize visualization area
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_layout.setSpacing(0)
        
        # Add panels to main layout
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.graph_panel, 1) # Give graph panel stretch priority
        
        # Add components
        self.repository_panel = RepositoryPanel()
        self.filter_panel = FilterPanel()
        self.navigation_panel = NavigationPanel()
        
        # Add graph visualization panel
        self.graph_visualization_panel = GraphVisualizationPanel()
        self.graph_layout.addWidget(self.graph_visualization_panel)
        
        # Connect repository panel's analysis completion to the visualization panel
        self.repository_panel.on_analysis_complete = self.on_analysis_complete
        
        self.control_layout.addWidget(self.repository_panel)
        self.control_layout.addWidget(self.filter_panel)
        self.control_layout.addWidget(self.navigation_panel)
        
        # Status label
        self.result_label = QLabel("")
        self.control_layout.addWidget(self.result_label)
        
    def on_analysis_complete(self, graph, hierarchy):
        """Handle the analysis completion event by updating the visualization"""
        self.graph_visualization_panel.set_graph_data(graph, hierarchy) 