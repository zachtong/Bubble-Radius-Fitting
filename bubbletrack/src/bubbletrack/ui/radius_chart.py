"""Matplotlib-embedded R(t) scatter chart."""

from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy


class RadiusChart(QWidget):
    """Red ``+`` scatter chart of radius vs frame number."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(350)
        self.setMaximumHeight(500)

        self._fig = Figure(figsize=(6, 5), dpi=100)
        self._fig.patch.set_facecolor("#F8FAFC")
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self._total_frames: int = 0
        self._setup_axes()

    def _setup_axes(self):
        ax = self._ax
        ax.set_facecolor("#F8FAFC")
        ax.set_xlabel("Frame", fontsize=10, color="#64748B")
        ax.set_ylabel("Radius (px)", fontsize=10, color="#64748B")
        ax.tick_params(colors="#94A3B8", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#E2E8F0")
        if self._total_frames > 0:
            ax.set_xlim(0.5, self._total_frames + 0.5)
        self._fig.tight_layout(pad=1.5)

    def set_total_frames(self, n: int):
        """Fix the x-axis range to [1, n]."""
        self._total_frames = n
        if n > 0:
            self._ax.set_xlim(0.5, n + 0.5)
            self._canvas.draw_idle()

    def plot_all(self, frames: np.ndarray, radii: np.ndarray):
        """Clear and replot all valid data points."""
        self._ax.clear()
        self._setup_axes()
        mask = radii > 0
        if mask.any():
            self._ax.plot(
                frames[mask], radii[mask], "+",
                color="#EF4444", markersize=8, markeredgewidth=1.5,
            )
        self._canvas.draw_idle()

    def clear(self):
        self._ax.clear()
        self._setup_axes()
        self._canvas.draw_idle()
