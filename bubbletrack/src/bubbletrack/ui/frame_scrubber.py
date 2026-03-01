"""Frame scrubber — horizontal slider with frame counter."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QSpinBox, QWidget


class FrameScrubber(QWidget):
    """``[< ] ====o==== [> ]  Frame: 1/100``."""

    value_changed = pyqtSignal(int)  # 0-indexed frame number

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Prev button
        self._prev = _NavButton("\u25C0")
        self._prev.clicked.connect(self._step_back)
        layout.addWidget(self._prev)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(0)
        self._slider.valueChanged.connect(self._on_slider)
        layout.addWidget(self._slider, 1)

        # Next button
        self._next = _NavButton("\u25B6")
        self._next.clicked.connect(self._step_forward)
        layout.addWidget(self._next)

        # Frame label
        self._label = QLabel("Frame: --/--")
        self._label.setFixedWidth(100)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

    def set_range(self, total: int):
        self._slider.setMaximum(max(total - 1, 0))
        self._update_label()

    def set_value(self, idx: int):
        self._slider.setValue(idx)

    def value(self) -> int:
        return self._slider.value()

    def _on_slider(self, v: int):
        self._update_label()
        self.value_changed.emit(v)

    def _step_back(self):
        self._slider.setValue(max(self._slider.value() - 1, 0))

    def _step_forward(self):
        self._slider.setValue(min(self._slider.value() + 1, self._slider.maximum()))

    def _update_label(self):
        cur = self._slider.value() + 1  # 1-indexed display
        total = self._slider.maximum() + 1
        self._label.setText(f"Frame: {cur}/{total}")


class _NavButton(QWidget):
    """Tiny navigation arrow button."""
    from PyQt6.QtWidgets import QPushButton

    def __new__(cls, text: str):
        from PyQt6.QtWidgets import QPushButton
        btn = QPushButton(text)
        btn.setFixedSize(28, 28)
        btn.setObjectName("secondaryBtn")
        return btn
