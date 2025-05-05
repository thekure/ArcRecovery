from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, 
                           QLineEdit, QLabel, QCheckBox)

class FilterPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Module Filters", parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Module filter input
        self.module_filter_input = QLineEdit()
        self.module_filter_input.setPlaceholderText("e.g., api.* or core.*")
        layout.addWidget(QLabel("Module Name Pattern:"))
        layout.addWidget(self.module_filter_input)
        
        # Clear filter button
        self.clear_filter_button = QPushButton("Clear Filter")
        layout.addWidget(self.clear_filter_button)
    
        
        
        self.setLayout(layout) 