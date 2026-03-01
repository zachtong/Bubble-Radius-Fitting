"""Pre-tune tab: ROI, threshold, removing-factor sliders, edge checkboxes, Fit button."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from bubbletrack.ui.widgets import SliderInput


class PreTuneTab(QWidget):
    """Pre-tune parameter panel."""

    # Signals
    threshold_changed = pyqtSignal(float)
    removing_factor_changed = pyqtSignal(int)
    edges_changed = pyqtSignal()
    fit_clicked = pyqtSignal()
    select_roi_clicked = pyqtSignal()
    frame_selected = pyqtSignal(int)  # 0-indexed frame number

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # -- Frame selector --
        frame_row = QHBoxLayout()
        frame_row.addWidget(QLabel("Frame:"))
        self._frame_spin = QSpinBox()
        self._frame_spin.setMinimum(1)
        self._frame_spin.setValue(1)
        self._frame_spin.valueChanged.connect(
            lambda v: self.frame_selected.emit(v - 1)
        )
        frame_row.addWidget(self._frame_spin)
        self._frame_total_label = QLabel("/ —")
        frame_row.addWidget(self._frame_total_label)
        frame_row.addStretch()
        layout.addLayout(frame_row)

        # -- ROI section --
        roi_group = QGroupBox("Region of Interest")
        roi_vbox = QVBoxLayout(roi_group)
        roi_vbox.setSpacing(6)

        self._select_roi_btn = QPushButton("Select ROI")
        self._select_roi_btn.setObjectName("secondaryBtn")
        self._select_roi_btn.clicked.connect(self.select_roi_clicked)
        roi_vbox.addWidget(self._select_roi_btn)

        self._roi_label = QLabel("ROI: full image")
        self._roi_label.setObjectName("dimText")
        roi_vbox.addWidget(self._roi_label)

        layout.addWidget(roi_group)

        # Internal ROI storage
        self._gridx: tuple[int, int] = (1, 99999)
        self._gridy: tuple[int, int] = (1, 99999)

        # -- Threshold slider --
        self._threshold = SliderInput("Threshold", 0, 100, 50, 1, 0)
        self._threshold.value_changed.connect(
            lambda v: self.threshold_changed.emit(v / 100.0)
        )
        layout.addWidget(self._threshold)

        # -- Removing factor slider --
        self._removing_factor = SliderInput("Remove", 0, 100, 90, 1, 0)
        self._removing_factor.value_changed.connect(
            lambda v: self.removing_factor_changed.emit(int(v))
        )
        layout.addWidget(self._removing_factor)

        # -- Edge checkboxes --
        edge_group = QGroupBox("Bubble crosses edge")
        edge_layout = QHBoxLayout(edge_group)
        self._edge_checks: list[QCheckBox] = []
        for name in ("Top", "Right", "Down", "Left"):
            cb = QCheckBox(name)
            cb.toggled.connect(lambda _: self.edges_changed.emit())
            edge_layout.addWidget(cb)
            self._edge_checks.append(cb)
        layout.addWidget(edge_group)

        # -- Fit button --
        self._fit_btn = QPushButton("Fit Current Frame")
        self._fit_btn.clicked.connect(self.fit_clicked)
        layout.addWidget(self._fit_btn)

        layout.addStretch()

    # -- Public getters --
    def get_roi(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Return (gridx, gridy) 1-indexed."""
        return self._gridx, self._gridy

    def set_roi(self, gridx: tuple[int, int], gridy: tuple[int, int]):
        self._gridx = gridx
        self._gridy = gridy
        self._roi_label.setText(
            f"X: {gridy[0]}–{gridy[1]}  Y: {gridx[0]}–{gridx[1]}"
        )

    def set_frame_range(self, total: int):
        """Set the max frame number for the frame selector."""
        self._frame_spin.setMaximum(total)
        self._frame_total_label.setText(f"/ {total}")

    def set_frame_value(self, idx: int):
        """Set frame spinbox to 1-indexed value without emitting signal."""
        self._frame_spin.blockSignals(True)
        self._frame_spin.setValue(idx + 1)
        self._frame_spin.blockSignals(False)

    def get_threshold(self) -> float:
        return self._threshold.value() / 100.0

    def set_threshold(self, v: float):
        self._threshold.set_value(v * 100)

    def get_removing_factor_slider(self) -> int:
        return int(self._removing_factor.value())

    def get_edge_flags(self) -> list[bool]:
        return [cb.isChecked() for cb in self._edge_checks]
