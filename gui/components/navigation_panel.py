from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class NavigationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Navigation", parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Current location label
        self.current_location_label = QLabel("Current: Root level")
        layout.addWidget(self.current_location_label)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.setEnabled(False)
        nav_buttons.addWidget(self.back_button)
        
        self.root_button = QPushButton("Root")
        self.root_button.setEnabled(False)
        nav_buttons.addWidget(self.root_button)
        
        layout.addLayout(nav_buttons)
        self.setLayout(layout) 