#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication

# Import MVC components
from models.repository_model import RepositoryModel
from views.main_view import MainView
from views.graph_view import GraphView
from controllers.main_controller import MainController

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create MVC components
    model = RepositoryModel()
    view = MainView()
    graph_view = GraphView()
    controller = MainController(model, view)
    
    # Set up graph view in the main view's panel
    view.graph_layout.addWidget(graph_view)
    
    # Connect the graph view to the controller
    controller.set_graph_view(graph_view)
    
    # Create repository directory if it doesn't exist
    if not os.path.exists("cur_repo"):
        os.makedirs("cur_repo")
    
    # Show the application
    view.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 