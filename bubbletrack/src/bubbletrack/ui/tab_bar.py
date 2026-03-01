"""Three-tab selector: Pre-tune / Manual / Automatic."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class TabBar(QWidget):
    """Horizontal tab bar that emits the selected tab index (0, 1, 2)."""

    tab_changed = pyqtSignal(int)

    TAB_NAMES = ("Pre-tune", "Manual", "Automatic")

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("TabBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._buttons: list[QPushButton] = []
        for i, name in enumerate(self.TAB_NAMES):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._select(idx))
            layout.addWidget(btn)
            self._buttons.append(btn)

        self._select(0)

    def _select(self, idx: int):
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == idx)
            btn.setProperty("active", i == idx)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.tab_changed.emit(idx)

    def current_index(self) -> int:
        for i, btn in enumerate(self._buttons):
            if btn.isChecked():
                return i
        return 0
