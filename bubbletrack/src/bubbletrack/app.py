"""Application entry point — creates QApplication, loads QSS, shows window."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from bubbletrack.controller.controller import AppController
from bubbletrack.logging_config import setup_logging
from bubbletrack.model.config import save_config
from bubbletrack.ui.main_window import MainWindow


def main():
    setup_logging(log_dir=Path.home() / ".bubbletrack" / "logs")

    app = QApplication(sys.argv)

    # Resolve resources path (works both normally and when frozen by PyInstaller)
    if getattr(sys, 'frozen', False):
        res = Path(sys._MEIPASS) / "bubbletrack" / "resources"
    else:
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

    # Auto-save user parameters on application exit
    app.aboutToQuit.connect(lambda: save_config(controller._get_state()))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
