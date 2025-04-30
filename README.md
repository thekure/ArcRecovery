# Module Viewer

A Python application for visualizing module dependencies in Python projects.

## Overview

Module Viewer allows you to:

- Clone a GitHub repository
- Analyze Python dependencies between modules
- Visualize the dependency graph
- Filter modules based on various criteria
- Navigate through package hierarchies
- Explore module relationships

## Application Structure

The application follows the Model-View-Controller (MVC) pattern:

```
Module Viewer/
├── models/                  # Data handling and business logic
│   ├── __init__.py
│   └── repository_model.py  # Handles repository and dependency data
├── views/                   # User interface components
│   ├── __init__.py
│   ├── main_view.py         # Main application window and controls
│   └── graph_view.py        # Graph visualization component
├── controllers/             # Application logic connecting models and views
│   ├── __init__.py
│   └── main_controller.py   # Main controller coordinating actions
├── main.py                  # Application entry point
└── README.md                # Documentation
```

## How It Works

1. **Clone Repository**: The application can clone a GitHub repository to analyze.
2. **Analyze Dependencies**: It scans the Python files and builds a dependency graph.
3. **Visualize Dependencies**: The graph view shows modules as nodes and dependencies as edges.
4. **Filter**: You can filter modules by name pattern, external dependencies, and connectivity.
5. **Navigation**: You can drill down into packages to explore their internal structure.

## Dependencies

- PyQt5: For the graphical user interface
- NetworkX: For graph data structures and algorithms

## Running the Application

```bash
python main.py
```

## Future Improvements

- Enhanced dependency detection
- Support for more repository sources
- Export functionality
- Performance improvements for large codebases 