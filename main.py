#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from scanner import file_path, imports_from_file, module_name_from_file_path
from graph_builder import build_data_structure, dependencies_digraph

def run_with_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    # run_with_gui()
    build_data_structure()



if __name__ == '__main__':
    main()