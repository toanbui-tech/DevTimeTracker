#!/usr/bin/env python3
"""
main.py — TimeTracker v2 entry point
Run with: python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from tracker import TimeTracker
from main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("TimeTracker")
    app.setOrganizationName("TimeTracker")

    tracker = TimeTracker()
    window = MainWindow(tracker)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()