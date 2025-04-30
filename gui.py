from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QGroupBox, QCheckBox, 
                           QComboBox, QFileDialog)
from PyQt5.QtCore import Qt
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArcRecovery")
        self.setGeometry(100, 100, 1200, 800)
        
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
        
        # Destination directory
        dest_layout = QHBoxLayout()
        dest_label = QLabel("Destination directory:")
        self.dest_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        dest_layout.addWidget(dest_label)
        dest_layout.addWidget(self.dest_input)
        dest_layout.addWidget(browse_button)
        repo_layout.addLayout(dest_layout)
        
        # Repository buttons
        self.analyse_button = QPushButton("Analyse")
        self.analyse_button.setEnabled(False)
        repo_layout.addWidget(self.analyse_button)
        
        self.scan_button = QPushButton("Scan")
        repo_layout.addWidget(self.scan_button)
        
        self.clear_button = QPushButton("Clear")
        repo_layout.addWidget(self.clear_button)
        
        repo_group.setLayout(repo_layout)
        self.control_layout.addWidget(repo_group)
        
    def setup_filter_controls(self):
        """Set up filter control components (visual only)."""
        filter_group = QGroupBox("Module Filters")
        filter_layout = QVBoxLayout()
        
        # Module filter input
        self.module_filter_input = QLineEdit()
        self.module_filter_input.setPlaceholderText("e.g., api.* or core.*")
        filter_layout.addWidget(QLabel("Module Name Pattern:"))
        filter_layout.addWidget(self.module_filter_input)
        
        # Clear filter button
        self.clear_filter_button = QPushButton("Clear Filter")
        filter_layout.addWidget(self.clear_filter_button)
        
        # Filter options
        filter_layout.addWidget(QLabel("Filter Options:"))
        
        self.hide_external_deps = QCheckBox("Hide External Dependencies")
        self.hide_external_deps.setToolTip("Hide all modules not defined in the repository")
        self.hide_external_deps.setChecked(True)
        filter_layout.addWidget(self.hide_external_deps)
        
        self.group_by_package = QCheckBox("Group by Package")
        self.group_by_package.setToolTip("Group nodes by their package name at each level")
        self.group_by_package.setChecked(True)
        filter_layout.addWidget(self.group_by_package)
        
        self.only_show_connected = QCheckBox("Only Show Connected Modules")
        self.only_show_connected.setToolTip("Hide modules with no connections")
        filter_layout.addWidget(self.only_show_connected)
        
        # Node size options
        filter_layout.addWidget(QLabel("Node Size Based On:"))
        self.node_size_metric = QComboBox()
        self.node_size_metric.addItems(["Uniform Size", "Connections Count", "Importance (PageRank)"])
        self.node_size_metric.setCurrentIndex(1)
        filter_layout.addWidget(self.node_size_metric)
        
        filter_group.setLayout(filter_layout)
        self.control_layout.addWidget(filter_group)
        
    def setup_navigation_controls(self):
        """Set up navigation control components (visual only)."""
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout()
        
        # Current location label
        self.current_location_label = QLabel("Current: Root level")
        nav_layout.addWidget(self.current_location_label)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.setEnabled(False)
        nav_buttons.addWidget(self.back_button)
        
        self.root_button = QPushButton("Root")
        self.root_button.setEnabled(False)
        nav_buttons.addWidget(self.root_button)
        
        nav_layout.addLayout(nav_buttons)
        nav_group.setLayout(nav_layout)
        self.control_layout.addWidget(nav_group)

    def browse_directory(self):
        """Handle browse button clicked."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dest_input.setText(directory)
            self.check_directory()

    def check_directory(self):
        """Check if selected directory has contents."""
        path = self.dest_input.text()
        if os.path.exists(path):
            has_contents = any(os.scandir(path))
            self.analyse_button.setEnabled(has_contents)
        else:
            self.analyse_button.setEnabled(False) 