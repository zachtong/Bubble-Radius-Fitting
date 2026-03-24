"""Pre-tune tab: ROI, threshold, removing-factor sliders, edge checkboxes, Fit button."""

from __future__ import annotations

import json

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from bubbletrack.ui.widgets import CollapsibleSection, SliderInput, ToggleSliderInput


class PreTuneTab(QWidget):
    """Pre-tune parameter panel."""

    # Signals
    threshold_changed = pyqtSignal(float)
    removing_factor_changed = pyqtSignal(int)
    edges_changed = pyqtSignal()
    filters_changed = pyqtSignal()
    fit_clicked = pyqtSignal()
    autotune_clicked = pyqtSignal()
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
        self._frame_spin.setMinimumWidth(70)
        self._frame_spin.valueChanged.connect(
            lambda v: self.frame_selected.emit(v - 1)
        )
        frame_row.addWidget(self._frame_spin)
        self._frame_total_label = QLabel("/ —")
        frame_row.addWidget(self._frame_total_label)
        frame_row.addStretch()
        layout.addLayout(frame_row)

        # -- Threshold slider --
        self._threshold = SliderInput("Threshold", 0, 100, 50, 1, 0)
        self._threshold.setToolTip(
            "Adaptive binarization sensitivity.\n"
            "Higher = more white pixels (bubble interior brighter).\n"
            "Lower = more black pixels (stricter foreground detection)."
        )
        self._threshold.value_changed.connect(
            lambda v: self.threshold_changed.emit(v / 100.0)
        )
        layout.addWidget(self._threshold)

        # -- Removing factor slider --
        self._removing_factor = SliderInput("Remove", 0, 100, 90, 1, 0)
        self._removing_factor.setToolTip(
            "Remove small white speckles from the binary image.\n"
            "Higher = remove larger noise regions.\n"
            "Increase if small debris/beads remain after binarization."
        )
        self._removing_factor.value_changed.connect(
            lambda v: self.removing_factor_changed.emit(int(v))
        )
        layout.addWidget(self._removing_factor)

        # -- Edge checkboxes --
        edge_group = QGroupBox("Bubble crosses edge")
        edge_group.setToolTip(
            "Check the edges where the bubble extends beyond the ROI boundary.\n"
            "This helps the algorithm correctly detect partial bubbles\n"
            "by expanding the image in the opposite direction."
        )
        edge_layout = QHBoxLayout(edge_group)
        self._edge_checks: list[QCheckBox] = []
        for name in ("Top", "Right", "Down", "Left"):
            cb = QCheckBox(name)
            cb.toggled.connect(lambda _: self.edges_changed.emit())
            edge_layout.addWidget(cb)
            self._edge_checks.append(cb)
        layout.addWidget(edge_group)

        # -- Advanced Filters (collapsible) --
        filters_section = CollapsibleSection("Advanced Filters", collapsed=True)

        self._gauss_slider = ToggleSliderInput(
            "Gauss Blur", 1, 20, 3, 1, decimals=0,
        )
        self._gauss_slider.setToolTip(
            "Gaussian blur applied BEFORE binarization.\n"
            "Smooths the grayscale image to suppress small noise (e.g. tracer beads).\n"
            "Sigma controls blur strength: higher = stronger smoothing."
        )
        self._clahe_slider = ToggleSliderInput(
            "CLAHE", 1, 40, 2, 1, decimals=0,
        )
        self._clahe_slider.setToolTip(
            "Contrast Limited Adaptive Histogram Equalization.\n"
            "Applied BEFORE binarization to improve local contrast.\n"
            "Useful when lighting is uneven across the image.\n"
            "Clip limit controls enhancement strength: higher = stronger contrast."
        )
        self._close_slider = ToggleSliderInput(
            "Morph Close", 1, 30, 5, 1, decimals=0,
        )
        self._close_slider.setToolTip(
            "Morphological closing applied AFTER binarization.\n"
            "Fills small holes and gaps inside the bubble boundary.\n"
            "Radius controls the structuring element size: higher = fills larger gaps."
        )
        self._open_slider = ToggleSliderInput(
            "Morph Open", 1, 20, 3, 1, decimals=0,
        )
        self._open_slider.setToolTip(
            "Morphological opening applied AFTER binarization.\n"
            "Removes thin protrusions and spurs on the bubble edge.\n"
            "Radius controls the structuring element size: higher = removes larger spurs."
        )

        for s in (self._gauss_slider, self._clahe_slider,
                  self._close_slider, self._open_slider):
            filters_section.add_widget(s)
            s.value_changed.connect(lambda _: self.filters_changed.emit())

        # Preset buttons
        preset_row = QHBoxLayout()
        save_btn = QPushButton("Save Preset")
        save_btn.setObjectName("secondaryBtn")
        save_btn.clicked.connect(self._save_preset)
        preset_row.addWidget(save_btn)
        load_btn = QPushButton("Load Preset")
        load_btn.setObjectName("secondaryBtn")
        load_btn.clicked.connect(self._load_preset)
        preset_row.addWidget(load_btn)
        preset_container = QWidget()
        preset_container.setLayout(preset_row)
        filters_section.add_widget(preset_container)

        layout.addWidget(filters_section)

        # -- Fit button --
        self._fit_btn = QPushButton("Fit Current Frame")
        self._fit_btn.clicked.connect(self.fit_clicked)
        layout.addWidget(self._fit_btn)

        # -- Auto-Tune button --
        self._autotune_btn = QPushButton("Auto Tune")
        self._autotune_btn.setToolTip(
            "Automatically find optimal Threshold and Removing Factor\n"
            "by testing multiple combinations on the current frame."
        )
        self._autotune_btn.clicked.connect(self.autotune_clicked)
        layout.addWidget(self._autotune_btn)

        # -- Quality display --
        self._quality_label = QLabel("")
        self._quality_label.setObjectName("qualityLabel")
        self._quality_label.setWordWrap(True)
        self._quality_label.hide()
        layout.addWidget(self._quality_label)

        layout.addStretch()

    # -- Public getters --

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
        """Set threshold without emitting signals."""
        self._threshold.blockSignals(True)
        self._threshold.set_value(v * 100)
        self._threshold.blockSignals(False)

    def get_removing_factor_slider(self) -> int:
        return int(self._removing_factor.value())

    def set_removing_factor(self, v: int):
        """Set removing factor without emitting signals."""
        self._removing_factor.blockSignals(True)
        self._removing_factor.set_value(v)
        self._removing_factor.blockSignals(False)

    def get_edge_flags(self) -> list[bool]:
        return [cb.isChecked() for cb in self._edge_checks]

    def get_filter_params(self) -> dict:
        """Return advanced filter parameters (0 = disabled)."""
        return {
            "gaussian_sigma": self._gauss_slider.value(),
            "clahe_clip": self._clahe_slider.value(),
            "closing_radius": int(self._close_slider.value()),
            "opening_radius": int(self._open_slider.value()),
        }

    def _get_full_params(self) -> dict:
        """Return all pretune parameters for preset save."""
        return {
            "threshold": self.get_threshold(),
            "removing_factor": self.get_removing_factor_slider(),
            "edge_flags": self.get_edge_flags(),
            **self.get_filter_params(),
        }

    def _save_preset(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Filter Preset", "", "JSON Files (*.json)",
        )
        if not path:
            return
        with open(path, "w") as f:
            json.dump(self._get_full_params(), f, indent=2)

    def _load_preset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Filter Preset", "", "JSON Files (*.json)",
        )
        if not path:
            return
        with open(path) as f:
            p = json.load(f)

        # Apply threshold and removing factor
        if "threshold" in p:
            self.set_threshold(p["threshold"])
            self.threshold_changed.emit(p["threshold"])
        if "removing_factor" in p:
            self._removing_factor.set_value(p["removing_factor"])
            self.removing_factor_changed.emit(p["removing_factor"])

        # Apply edge flags
        if "edge_flags" in p:
            for cb, val in zip(self._edge_checks, p["edge_flags"]):
                cb.setChecked(val)

        # Apply advanced filters
        slider_map = {
            "gaussian_sigma": self._gauss_slider,
            "clahe_clip": self._clahe_slider,
            "closing_radius": self._close_slider,
            "opening_radius": self._open_slider,
        }
        for key, slider in slider_map.items():
            if key in p:
                v = p[key]
                slider.set_value(v if v > 0 else slider._default, enabled=v > 0)

        self.filters_changed.emit()

    # -- Quality display --

    def show_quality(self, n_pts: int, rms: float, score_pct: int) -> None:
        """Show fit quality metrics below the buttons."""
        if score_pct >= 70:
            color = "#10b981"
        elif score_pct >= 40:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        self._quality_label.setText(
            f'<span style="color:#a1a1aa;">Edge pts:</span> {n_pts} &nbsp; '
            f'<span style="color:#a1a1aa;">RMS:</span> {rms:.1f} px &nbsp; '
            f'<span style="color:#a1a1aa;">Confidence:</span> '
            f'<span style="color:{color};">{score_pct}%</span>'
        )
        self._quality_label.show()

    def hide_quality(self) -> None:
        self._quality_label.hide()

    def set_autotune_enabled(self, enabled: bool) -> None:
        """Enable/disable the auto-tune button (during search)."""
        self._autotune_btn.setEnabled(enabled)
        self._autotune_btn.setText("Searching..." if not enabled else "Auto Tune")
