# ArcRecovery

ArcRecovery is a tool for analyzing Python codebases to extract module dependencies and build a dependency graph. It helps you understand the architecture and relationships between different modules in a Python project.

## Features

- Extract module dependencies from Python files
- Build a directed graph of module dependencies
- Identify internal vs external dependencies
- Analyze module relationships and architecture

## Project Structure

- `module.py`: Defines the `Module` class for representing Python modules
- `common.py`: Shared utility functions for path handling and module name extraction
- `imports_helper.py`: Functions for parsing Python imports from files
- `graph_builder.py`: Functions for building the dependency graph
- `scanner_tests.py`: Test cases for the dependency scanning functionality
- `main.py`: Entry point for running the tool

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/ArcRecovery.git
cd ArcRecovery
```

2. Create a virtual environment and install dependencies:
```
python -m venv Arch
source Arch/bin/activate  # On Windows: Arch\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the main application:
```
python main.py
```

Run the tests:
```
python scanner_tests.py
```

## How It Works

The tool scans Python files in the specified code root folder, extracts import statements, and builds a directed graph where:
- Nodes represent Python modules
- Edges represent dependencies between modules
- Each module tracks its internal dependencies

## Customization

You can customize the analysis by modifying:
- `CODE_ROOT_FOLDER` in `constants.py` to specify the root folder of the codebase to analyze
- Functions in `graph_builder.py` to change how the dependency graph is constructed 