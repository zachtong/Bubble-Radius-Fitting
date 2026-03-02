"""Application entry point — creates QApplication, loads QSS, shows window."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from bubbletrack.ui.main_window import MainWindow
from bubbletrack.controller.controller import AppController


def main():
    app = QApplication(sys.argv)

    # Load QSS stylesheet
    res = Path(__file__).parent / "resources"
    qss_path = res / "style.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # Application icon
    icon_path = res / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    controller = AppController(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
