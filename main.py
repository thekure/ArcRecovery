#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from Model.graph_builder import get_dependencies_digraph, draw_graph
from GUI.main_window import MainWindow
from Model.module import Module
from Model.common import module_name_from_file_path, file_path_from_module_name, get_parent_module
from Model.imports_helper import imports_from_file


def run_with_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    # run_with_gui()
    G = get_dependencies_digraph()
    # draw_graph(G, (10, 10))



if __name__ == '__main__':
    main()