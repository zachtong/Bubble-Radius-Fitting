"""Interactive R-t scatter chart using pyqtgraph."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class RadiusChart(QWidget):
    """Scatter plot of bubble radius vs frame number.

    Uses pyqtgraph for 10-100x faster updates compared to Matplotlib.
    Supports click-to-jump, zoom, and pan interactivity.

    Signals:
        point_clicked(int): Emitted when user clicks a data point,
                           with the 0-based frame index.
    """

    point_clicked = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(350)
        self.setMaximumHeight(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configure pyqtgraph plot widget
        self._plot = pg.PlotWidget()
        self._plot.setBackground("#F8FAFC")
        self._plot.setLabel("left", "Radius (px)")
        self._plot.setLabel("bottom", "Frame")
        self._plot.showGrid(x=True, y=True, alpha=0.3)

        # Style axes to match the app theme
        for axis_name in ("left", "bottom"):
            axis = self._plot.getAxis(axis_name)
            axis.setPen(pg.mkPen("#E2E8F0"))
            axis.setTextPen(pg.mkPen("#64748B"))

        # Scatter plot item — red "+" markers
        self._scatter = pg.ScatterPlotItem(
            pen=pg.mkPen("#EF4444", width=1.5),
            brush=pg.mkBrush("#EF4444"),
            symbol="+",
            size=10,
        )
        self._plot.addItem(self._scatter)
        self._scatter.sigClicked.connect(self._on_scatter_clicked)

        layout.addWidget(self._plot)

        self._total_frames: int = 0
        self._frames: np.ndarray = np.array([])
        self._radii: np.ndarray = np.array([])

    def plot_all(self, frames: np.ndarray, radii: np.ndarray) -> None:
        """Clear and replot all valid data points (radius > 0)."""
        mask = radii > 0
        if not np.any(mask):
            self._scatter.setData([], [])
            self._frames = np.array([])
            self._radii = np.array([])
            return
        self._frames = frames[mask]
        self._radii = radii[mask]
        self._scatter.setData(self._frames, self._radii)

    def set_total_frames(self, n: int) -> None:
        """Fix the x-axis range to [1, n]."""
        self._total_frames = n
        if n > 0:
            self._plot.setXRange(0.5, n + 0.5, padding=0)

    def clear(self) -> None:
        """Remove all data points from the chart."""
        self._scatter.setData([], [])
        self._frames = np.array([])
        self._radii = np.array([])

    def _on_scatter_clicked(self, plot, points, ev=None) -> None:
        """Handle click on scatter point — emit 0-based frame index.

        The sigClicked signature is ``(plot, points)`` in pyqtgraph 0.13+.
        We accept an optional third ``ev`` arg for forward-compatibility.
        """
        if points:
            frame_num = int(points[0].pos().x())  # 1-based frame number
            self.point_clicked.emit(frame_num - 1)  # emit 0-based index
