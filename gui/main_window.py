from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from .components.repository_panel import RepositoryPanel
from .components.filter_panel import FilterPanel
from .components.navigation_panel import NavigationPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArcRecovery")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget
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
        
        # Right panel (empty but kept for layout)
        self.graph_panel = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_panel.setLayout(self.graph_layout)
        
        # Add panels to main layout
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.graph_panel)
        
        # Add components
        self.repository_panel = RepositoryPanel()
        self.filter_panel = FilterPanel()
        self.navigation_panel = NavigationPanel()
        
        self.control_layout.addWidget(self.repository_panel)
        self.control_layout.addWidget(self.filter_panel)
        self.control_layout.addWidget(self.navigation_panel)
        
        # Status label
        self.result_label = QLabel("")
        self.control_layout.addWidget(self.result_label) 