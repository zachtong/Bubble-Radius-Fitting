"""Application entry point — creates QApplication, loads QSS, shows window."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication

from bubbletrack.controller.controller import AppController
from bubbletrack.logging_config import setup_logging
from bubbletrack.model.config import is_onboarding_done, save_config, set_onboarding_done
from bubbletrack.ui.main_window import MainWindow
from bubbletrack.ui.welcome_dialog import WelcomeDialog


def main():
    # Required for PyInstaller + multiprocessing on Windows.
    # Without this, child processes re-execute main() and open duplicate GUIs.
    from multiprocessing import freeze_support
    freeze_support()

    setup_logging(log_dir=Path.home() / ".bubbletrack" / "logs")

    app = QApplication(sys.argv)

    # Force Fusion style for consistent dark-theme rendering across platforms
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0f1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e4e4e7"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1a1b23"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#13141b"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e4e4e7"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1a1b23"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#a1a1aa"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#6366f1"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#e4e4e7"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1a1b23"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e4e4e7"))
    app.setPalette(palette)

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

    # Show onboarding dialog on first launch
    if not is_onboarding_done():
        dlg = WelcomeDialog(window)
        dlg.exec()
        if dlg.dont_show_again:
            set_onboarding_done()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
