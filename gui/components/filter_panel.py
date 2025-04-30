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
        
        # Filter options
        layout.addWidget(QLabel("Filter Options:"))
        
        self.hide_external_deps = QCheckBox("Hide External Dependencies")
        self.hide_external_deps.setToolTip("Hide all modules not defined in the repository")
        self.hide_external_deps.setChecked(True)
        self.hide_external_deps.stateChanged.connect(self.on_hide_external_changed)
        layout.addWidget(self.hide_external_deps)
        
        self.group_by_package = QCheckBox("Group by Package")
        self.group_by_package.setToolTip("Group nodes by their package name at each level")
        self.group_by_package.setChecked(True)
        layout.addWidget(self.group_by_package)
        
        self.only_show_connected = QCheckBox("Only Show Connected Modules")
        self.only_show_connected.setToolTip("Hide modules with no connections")
        layout.addWidget(self.only_show_connected)
        
        self.setLayout(layout) 


    # This is where I control checkbox state changes
    def on_hide_external_changed(self, state):
        """Handle state changes for hide external dependencies checkbox.
        Args:
            state: Qt.Checked or Qt.Unchecked
        """
        print(f"Hide external dependencies checkbox state changed: {state}")
        # Your code here to handle the checkbox state change
        pass 