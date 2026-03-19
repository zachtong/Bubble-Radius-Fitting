"""Interactive R-t scatter chart using pyqtgraph."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget


class RadiusChart(QWidget):
    """Scatter plot of bubble radius vs frame number.

    Uses pyqtgraph for 10-100x faster updates compared to Matplotlib.
    Supports click-to-jump, zoom, pan, and right-click context menu.

    Signals:
        point_clicked(int): Emitted when user clicks a data point,
                           with the 0-based frame index.
        delete_requested(int): Emitted when user requests deletion of a point,
                              with the 0-based frame index.
        refit_requested(int): Emitted when user requests refitting a frame,
                             with the 0-based frame index.
    """

    point_clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    refit_requested = pyqtSignal(int)

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

        # Anomaly overlay — yellow triangle markers
        self._anomaly_scatter = pg.ScatterPlotItem(
            pen=pg.mkPen("#FCD34D", width=1.5),
            brush=pg.mkBrush("#FCD34D"),
            symbol="t",
            size=12,
        )
        self._plot.addItem(self._anomaly_scatter)

        layout.addWidget(self._plot)

        self._total_frames: int = 0
        self._frames: np.ndarray = np.array([])
        self._radii: np.ndarray = np.array([])

        # Right-click context menu on scatter plot
        self._setup_context_menu()

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

    def mark_anomalies(
        self, frames: np.ndarray, radii: np.ndarray, mask: np.ndarray,
    ) -> None:
        """Overlay yellow triangle markers on anomalous data points.

        Parameters
        ----------
        frames : np.ndarray
            1-based frame numbers for every data point.
        radii : np.ndarray
            Radius values (may include NaN / non-positive).
        mask : np.ndarray
            Boolean array; True = anomalous.  Same length as *frames*.
        """
        # Only show anomaly markers for points that are valid AND anomalous
        valid = np.isfinite(radii) & (radii > 0)
        show = mask & valid
        if not np.any(show):
            self._anomaly_scatter.setData([], [])
            return
        self._anomaly_scatter.setData(frames[show], radii[show])

    def set_total_frames(self, n: int) -> None:
        """Fix the x-axis range to [1, n]."""
        self._total_frames = n
        if n > 0:
            self._plot.setXRange(0.5, n + 0.5, padding=0)

    def clear(self) -> None:
        """Remove all data points from the chart."""
        self._scatter.setData([], [])
        self._anomaly_scatter.setData([], [])
        self._frames = np.array([])
        self._radii = np.array([])

    def _setup_context_menu(self) -> None:
        """Connect right-click detection on the scatter plot scene."""
        self._plot.scene().sigMouseClicked.connect(self._on_mouse_clicked)

    def _find_nearest_point(self, x: float, y: float) -> int | None:
        """Find nearest data point to (x, y) in view coords. Return 0-based idx or None."""
        if len(self._frames) == 0:
            return None

        vb = self._plot.plotItem.vb
        view_range = vb.viewRange()
        x_range = view_range[0][1] - view_range[0][0]
        y_range = view_range[1][1] - view_range[1][0]

        if x_range <= 0 or y_range <= 0:
            return None

        # Normalize distances by axis range for uniform click tolerance
        dx = (self._frames - x) / x_range
        dy = (self._radii - y) / y_range
        dists = dx ** 2 + dy ** 2

        nearest_idx = int(np.argmin(dists))
        # Threshold: 1% of the plot area (in normalized coords)
        if dists[nearest_idx] > 0.01 ** 2 + 0.01 ** 2:
            return None

        # Convert from filtered index to 0-based frame index
        frame_num = int(self._frames[nearest_idx])  # 1-based
        return frame_num - 1  # 0-based

    def _on_mouse_clicked(self, event) -> None:
        """Handle mouse click on the plot scene — show context menu on right-click."""
        if event.button() != Qt.MouseButton.RightButton:
            return

        pos = self._plot.plotItem.vb.mapSceneToView(event.scenePos())
        frame_idx = self._find_nearest_point(pos.x(), pos.y())
        if frame_idx is None:
            return

        # Build context menu
        menu = QMenu(self)
        frame_label = frame_idx + 1  # display as 1-based

        delete_action = QAction(f"Delete point (Frame {frame_label})", self)
        delete_action.triggered.connect(
            lambda _checked=False, i=frame_idx: self.delete_requested.emit(i),
        )

        refit_action = QAction(f"Refit frame {frame_label}", self)
        refit_action.triggered.connect(
            lambda _checked=False, i=frame_idx: self.refit_requested.emit(i),
        )

        menu.addAction(delete_action)
        menu.addAction(refit_action)

        # Show at cursor position
        menu.exec(event.screenPos().toPoint())

    def _on_scatter_clicked(self, plot, points, ev=None) -> None:
        """Handle click on scatter point — emit 0-based frame index.

        The sigClicked signature is ``(plot, points)`` in pyqtgraph 0.13+.
        We accept an optional third ``ev`` arg for forward-compatibility.
        """
        if points:
            frame_num = int(points[0].pos().x())  # 1-based frame number
            self.point_clicked.emit(frame_num - 1)  # emit 0-based index
