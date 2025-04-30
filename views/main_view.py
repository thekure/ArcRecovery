from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLineEdit, QLabel, QGroupBox, QCheckBox, QComboBox)
from PyQt5.QtCore import pyqtSignal

class MainView(QWidget):
    """
    Main view for the application that handles the UI layout and interactions.
    """
    # Signals to notify controller of UI events
    clone_clicked = pyqtSignal(str)
    analyze_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()
    filter_changed = pyqtSignal(str, bool, bool, bool, int)  # pattern, hide_external, only_connected, group_by_pkg, node_size
    clear_filter_clicked = pyqtSignal()
    back_clicked = pyqtSignal()
    root_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set up the window
        self.setWindowTitle("Module Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout (horizontal split)
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
        
        # Add panels to main layout
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.graph_panel)
        self.setLayout(self.main_layout)
        
        # Set up control components
        self.setup_repository_controls()
        self.setup_filter_controls()
        self.setup_navigation_controls()
        
        # Status label
        self.result_label = QLabel("")
        self.control_layout.addWidget(self.result_label)
        
    def setup_repository_controls(self):
        """Set up repository control components."""
        repo_group = QGroupBox("Repository Controls")
        repo_layout = QVBoxLayout()
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setText("https://github.com/zeeguu/api")
        repo_layout.addWidget(QLabel("GitHub Repo URL:"))
        repo_layout.addWidget(self.url_input)
        
        # Repository buttons
        self.clone_button = QPushButton("Clone")
        self.clone_button.clicked.connect(self.on_clone_clicked)
        repo_layout.addWidget(self.clone_button)
        
        self.analyse_button = QPushButton("Analyse")
        self.analyse_button.clicked.connect(self.on_analyze_clicked)
        repo_layout.addWidget(self.analyse_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        repo_layout.addWidget(self.clear_button)
        
        repo_group.setLayout(repo_layout)
        self.control_layout.addWidget(repo_group)
        
    def setup_filter_controls(self):
        """Set up filter control components."""
        filter_group = QGroupBox("Module Filters")
        filter_layout = QVBoxLayout()
        
        # Module filter input
        self.module_filter_input = QLineEdit()
        self.module_filter_input.setPlaceholderText("e.g., api.* or core.*")
        self.module_filter_input.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(QLabel("Module Name Pattern:"))
        filter_layout.addWidget(self.module_filter_input)
        
        # Clear filter button
        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.clicked.connect(self.on_clear_filter_clicked)
        filter_layout.addWidget(self.clear_filter_button)
        
        # Filter options
        filter_layout.addWidget(QLabel("Filter Options:"))
        
        self.hide_external_deps = QCheckBox("Hide External Dependencies")
        self.hide_external_deps.setToolTip("Hide all modules not defined in the repository")
        self.hide_external_deps.stateChanged.connect(self.on_filter_changed)
        self.hide_external_deps.setChecked(True)
        filter_layout.addWidget(self.hide_external_deps)
        
        self.group_by_package = QCheckBox("Group by Package")
        self.group_by_package.setToolTip("Group nodes by their package name at each level")
        self.group_by_package.stateChanged.connect(self.on_filter_changed)
        self.group_by_package.setChecked(True)
        filter_layout.addWidget(self.group_by_package)
        
        self.only_show_connected = QCheckBox("Only Show Connected Modules")
        self.only_show_connected.setToolTip("Hide modules with no connections")
        self.only_show_connected.stateChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.only_show_connected)
        
        # Node size options
        filter_layout.addWidget(QLabel("Node Size Based On:"))
        self.node_size_metric = QComboBox()
        self.node_size_metric.addItems(["Uniform Size", "Connections Count", "Importance (PageRank)"])
        self.node_size_metric.setCurrentIndex(1)
        self.node_size_metric.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.node_size_metric)
        
        filter_group.setLayout(filter_layout)
        self.control_layout.addWidget(filter_group)
        
    def setup_navigation_controls(self):
        """Set up navigation control components."""
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout()
        
        # Current location label
        self.current_location_label = QLabel("Current: Root level")
        nav_layout.addWidget(self.current_location_label)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setEnabled(False)
        nav_buttons.addWidget(self.back_button)
        
        self.root_button = QPushButton("Root")
        self.root_button.clicked.connect(self.on_root_clicked)
        self.root_button.setEnabled(False)
        nav_buttons.addWidget(self.root_button)
        
        nav_layout.addLayout(nav_buttons)
        nav_group.setLayout(nav_layout)
        self.control_layout.addWidget(nav_group)
    
    # UI update methods
    def set_analyze_enabled(self, enabled):
        """Enable or disable the analyze button."""
        self.analyse_button.setEnabled(enabled)
    
    def set_navigation_state(self, has_history, at_root):
        """Update navigation button states."""
        self.back_button.setEnabled(has_history)
        self.root_button.setEnabled(not at_root)
    
    def set_location_label(self, location):
        """Update the location label text."""
        self.current_location_label.setText(f"Current: {location}")
    
    def set_result_text(self, text):
        """Update the result label text."""
        self.result_label.setText(text)
    
    # Signal handlers
    def on_clone_clicked(self):
        """Handle clone button clicked."""
        self.clone_clicked.emit(self.url_input.text())
    
    def on_analyze_clicked(self):
        """Handle analyze button clicked."""
        self.analyze_clicked.emit()
    
    def on_clear_clicked(self):
        """Handle clear button clicked."""
        self.clear_clicked.emit()
    
    def on_filter_changed(self):
        """Handle filter settings changed."""
        self.filter_changed.emit(
            self.module_filter_input.text(),
            self.hide_external_deps.isChecked(),
            self.only_show_connected.isChecked(),
            self.group_by_package.isChecked(),
            self.node_size_metric.currentIndex()
        )
    
    def on_clear_filter_clicked(self):
        """Handle clear filter button clicked."""
        self.module_filter_input.clear()
        self.hide_external_deps.setChecked(False)
        self.only_show_connected.setChecked(False)
        self.group_by_package.setChecked(False)
        self.node_size_metric.setCurrentIndex(0)
        self.clear_filter_clicked.emit()
    
    def on_back_clicked(self):
        """Handle back button clicked."""
        self.back_clicked.emit()
    
    def on_root_clicked(self):
        """Handle root button clicked."""
        self.root_clicked.emit() 