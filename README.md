# ArcRecovery

A tool for visualizing and analyzing dependencies in Python codebases.

## Features

- Clone GitHub repositories
- Analyze code structure and dependencies
- Visualize package/module dependencies using interactive graphs
- Filter and navigate through complex codebases

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application with:

```bash
python main.py
```

### Basic workflow:

1. Enter a GitHub repository URL in the Repository Controls panel
2. Click "Clone" to clone the repository
3. Click "Analyze" to build the dependency graph
4. The graph visualization will display the root-level modules and packages with their dependencies

## Dependencies

- PyQt5: GUI framework
- PyQtWebEngine: Web view for interactive visualizations
- pyvis: Network visualization library
- NetworkX: Graph manipulation and analysis
- GitPython: Git repository handling 