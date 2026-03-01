"""Dark bottom status bar."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class StatusBar(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("StatusBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(24)

        self._frame_label = QLabel("Frame: --/--")
        layout.addWidget(self._frame_label)

        self._format_label = QLabel("Format: --")
        layout.addWidget(self._format_label)

        self._scale_label = QLabel("Scale: -- \u00b5m/px")
        layout.addWidget(self._scale_label)

        self._roi_label = QLabel("ROI: --")
        layout.addWidget(self._roi_label)

        layout.addStretch()

        self._mode_label = QLabel("Mode: Pre-tune")
        layout.addWidget(self._mode_label)

    def update_frame(self, current: int, total: int):
        self._frame_label.setText(f"Frame: {current}/{total}")

    def update_format(self, fmt: str):
        self._format_label.setText(f"Format: {fmt}")

    def update_scale(self, um2px: float):
        self._scale_label.setText(f"Scale: {um2px} \u00b5m/px")

    def update_roi(self, gridx: tuple[int, int], gridy: tuple[int, int]):
        self._roi_label.setText(
            f"ROI: [{gridx[0]}-{gridx[1]}, {gridy[0]}-{gridy[1]}]"
        )

    def update_mode(self, mode: str):
        self._mode_label.setText(f"Mode: {mode}")
