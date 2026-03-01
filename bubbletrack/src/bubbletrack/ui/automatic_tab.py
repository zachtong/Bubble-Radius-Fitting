"""Automatic mode tab: frame range, progress, Fit / Stop / Clear buttons."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QProgressBar, QPushButton, QSpinBox,
    QVBoxLayout, QWidget,
)


class AutomaticTab(QWidget):
    """Automatic batch-processing panel."""

    fit_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Frame range
        range_lbl = QLabel("Frame Range")
        range_lbl.setObjectName("sectionTitle")
        layout.addWidget(range_lbl)

        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("From:"))
        self._start_spin = QSpinBox()
        self._start_spin.setMinimum(1)
        self._start_spin.setValue(1)
        self._start_spin.setMinimumWidth(70)
        range_row.addWidget(self._start_spin)

        range_row.addStretch()

        range_row.addWidget(QLabel("To:"))
        self._end_spin = QSpinBox()
        self._end_spin.setMinimum(1)
        self._end_spin.setValue(1)
        self._end_spin.setMinimumWidth(70)
        range_row.addWidget(self._end_spin)
        layout.addLayout(range_row)

        # Progress
        self._progress_label = QLabel("Ready")
        self._progress_label.setObjectName("dimText")
        layout.addWidget(self._progress_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        layout.addWidget(self._progress)

        # Buttons
        btn_row = QHBoxLayout()
        self._fit_btn = QPushButton("Fit All")
        self._fit_btn.clicked.connect(self.fit_clicked)
        btn_row.addWidget(self._fit_btn)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("dangerBtn")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_clicked)
        btn_row.addWidget(self._stop_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("secondaryBtn")
        self._clear_btn.clicked.connect(self.clear_clicked)
        btn_row.addWidget(self._clear_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

    # -- Public API --
    def set_range(self, total: int):
        self._start_spin.setMaximum(total)
        self._end_spin.setMaximum(total)
        self._end_spin.setValue(total)

    def get_range(self) -> tuple[int, int]:
        """Return 1-indexed (start, end)."""
        return self._start_spin.value(), self._end_spin.value()

    def set_progress(self, current: int, total: int):
        pct = int(current / max(total, 1) * 100)
        self._progress.setValue(pct)
        self._progress_label.setText(f"Processing: {current}/{total} ({pct}%)")

    def set_running(self, running: bool):
        self._fit_btn.setEnabled(not running)
        self._stop_btn.setEnabled(running)
        if not running:
            self._progress_label.setText("Done" if self._progress.value() > 0 else "Ready")

    def reset_progress(self):
        self._progress.setValue(0)
        self._progress_label.setText("Ready")
