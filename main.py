import sys
import os
import shutil
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QMessageBox, QGroupBox)

from repository_manager import RepositoryManager
from dependency_analyzer import DependencyAnalyzer
from graph_visualizer import GraphView

class ModuleViewerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Module Viewer")
        self.setGeometry(100, 100, 1200, 800)

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

        filter_group.setLayout(filter_layout)
        self.control_layout.addWidget(filter_group)

        # Status label
        self.result_label = QLabel("")
        self.control_layout.addWidget(self.result_label)

    def apply_filters(self):
        if not self.graph_view:
            return
            
        pattern = self.module_filter_input.text()
        try:
            if pattern:
                regex = re.compile(pattern)
                filtered_graph = self.graph_view.graph.copy()
                
                # Remove nodes that don't match the pattern
                nodes_to_remove = [node for node in filtered_graph.nodes() 
                                 if not regex.match(node)]
                filtered_graph.remove_nodes_from(nodes_to_remove)
                
                # Update the visualization
                self.graph_layout.removeWidget(self.graph_view)
                self.graph_view.deleteLater()
                self.graph_view = GraphView(filtered_graph)
                self.graph_layout.addWidget(self.graph_view)
        except re.error:
            self.result_label.setText("Invalid regex pattern")

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
            self.analyzer = DependencyAnalyzer(self.repo_manager.get_repo_path())
            graph = self.analyzer.build_dependency_graph(python_files)
            self.result_label.setText(f"Success! {len(graph.nodes)} modules found.")

            if self.graph_view:
                self.graph_layout.removeWidget(self.graph_view)
                self.graph_view.deleteLater()

            self.graph_view = GraphView(graph)
            self.graph_layout.addWidget(self.graph_view)

        except Exception as e:
            self.result_label.setText(f"Error analysing repository: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ModuleViewerApp()
    viewer.show()
    sys.exit(app.exec_()) 