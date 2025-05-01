#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from graph_builder import build_data_structure, draw_graph
from gui.main_window import MainWindow


def run_with_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    # run_with_gui()
    G = build_data_structure()
    # draw_graph(G, (10, 10))



if __name__ == '__main__':
    main()