#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from GUI.main_window import MainWindow
from constants import CODE_ROOT_FOLDER, HTML_OUTPUT_FOLDER, ASSETS_FOLDER
from GUI.utils.pyvis_assets import ensure_pyvis_assets_available


def ensure_folders_exist():
    """Make sure all required folders exist"""
    os.makedirs(CODE_ROOT_FOLDER, exist_ok=True)
    os.makedirs(HTML_OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(ASSETS_FOLDER, exist_ok=True)
    ensure_pyvis_assets_available()


def run_with_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    ensure_folders_exist()
    run_with_gui()

if __name__ == '__main__':
    main()