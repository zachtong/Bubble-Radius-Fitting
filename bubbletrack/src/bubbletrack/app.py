"""Application entry point — creates QApplication, loads QSS, shows window."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from bubbletrack.ui.main_window import MainWindow
from bubbletrack.controller.controller import AppController


def main():
    app = QApplication(sys.argv)

    # Load QSS stylesheet
    qss_path = Path(__file__).parent / "resources" / "style.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    window = MainWindow()
    controller = AppController(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
