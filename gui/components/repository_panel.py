from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, 
                           QLineEdit, QLabel, QMessageBox)
import git

from graph_builder import build_graph
from ..utils.github_utils import is_valid_github_url, clone_repository, clear_repository
from constants import CODE_ROOT_FOLDER
import os

class RepositoryPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Repository Controls", parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setText("https://github.com/zeeguu/api")
        layout.addWidget(QLabel("GitHub Repo URL:"))
        layout.addWidget(self.url_input)
        
        # Repository buttons
        self.analyse_button = QPushButton("Analyse")
        self.analyse_button.clicked.connect(self.analyse_repository)
        self.check_directory()
        layout.addWidget(self.analyse_button)
        
        self.clone_button = QPushButton("Clone")
        self.clone_button.clicked.connect(self.clone_repository)
        layout.addWidget(self.clone_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_repository)
        layout.addWidget(self.clear_button)
        
        self.setLayout(layout)

    def clone_repository(self):
        url = self.url_input.text().strip()
        
        if not is_valid_github_url(url):
            QMessageBox.warning(self, "Invalid URL", 
                              "Please enter a valid GitHub repository URL.")
            return
            
        try:
            clone_repository(url, CODE_ROOT_FOLDER)
            self.check_directory()
            QMessageBox.information(self, "Success", 
                                  "Repository cloned successfully!")
        except git.exc.GitCommandError as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to clone repository: {str(e)}")
            clear_repository(CODE_ROOT_FOLDER)

    def clear_repository(self):
        clear_repository(CODE_ROOT_FOLDER)
        self.check_directory()

    def check_directory(self):
        if os.path.exists(CODE_ROOT_FOLDER):
            has_contents = any(os.scandir(CODE_ROOT_FOLDER))
            self.analyse_button.setEnabled(has_contents)
        else:
            self.analyse_button.setEnabled(False) 
    
    def analyse_repository(self):
        # This is where we should build the graph
        print("Analyzing repository...")