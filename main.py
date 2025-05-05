#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from Model.graph_builder import get_dependencies_digraph, draw_graph, print_module_tree
from GUI.main_window import MainWindow
from Model.hierarchy import ModuleHierarchy


def run_with_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    G = get_dependencies_digraph()
    H = ModuleHierarchy(G)

    # draw_graph(G, (10, 10))

if __name__ == '__main__':
    main()