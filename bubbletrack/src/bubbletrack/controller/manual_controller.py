"""ManualController — manual point-and-click circle fitting."""

from __future__ import annotations

import logging

import numpy as np

from bubbletrack.controller.base import BaseController
from bubbletrack.controller.display_mixin import (
    display_frame,
    redraw_original,
    refresh_chart,
)
from bubbletrack.event_bus import EventBus
from bubbletrack.model.circle_fit import circle_fit_taubin

logger = logging.getLogger(__name__)


class ManualController(BaseController):
    """Manages manual edge-point selection and fitting."""

    def __init__(self, bus: EventBus, get_state, set_state, window,
                 get_max_radius) -> None:
        super().__init__(bus, get_state, set_state, window)
        self._manual_points: list[tuple[float, float]] = []
        self._get_max_radius = get_max_radius

    # -- public handlers -------------------------------------------------- #

    def on_manual_select(self) -> None:
        self._manual_points.clear()
        self.w.left_panel.manual_tab.set_point_count(0)
        self.w.original_panel.set_mode("point")
        self.w.header.set_status("Click on bubble edge", "#FCD34D")
        self.w.status_bar.update_mode("Manual")

    def on_point_clicked(self, x: float, y: float) -> None:
        """x = col, y = row in scene coordinates."""
        self._manual_points.append((y, x))  # store as (row, col)
        n = len(self._manual_points)
        self.w.left_panel.manual_tab.set_point_count(n)
        # Draw the point
        pt = np.array([[y, x]])
        self.w.original_panel.draw_points(pt, "#EF4444", 4.0)

    def on_manual_done(self) -> None:
        self.w.original_panel.set_mode("normal")
        if len(self._manual_points) < 3:
            self.w.header.set_status("Need at least 3 points", "#EF4444")
            return

        xy = np.array(self._manual_points)
        rc, cc, radius = circle_fit_taubin(xy)

        idx = self.state.image_no
        if np.isnan(radius):
            self.w.header.set_status("Fitting failed", "#EF4444")
        elif radius > self._get_max_radius():
            self.w.header.set_status(
                f"Radius outlier ({radius:.0f} px), skipped", "#FCD34D",
            )
        else:
            self.state.radius[idx] = radius
            self.state.circle_fit_par[idx] = [rc, cc]
            self.state.circle_xy[idx] = xy

            # Clear old overlays before drawing new results
            redraw_original(self.state, self.w)
            self.w.original_panel.draw_circle(rc, cc, radius, "#3B82F6")
            self.w.original_panel.draw_points(xy, "#EF4444", 2.0)
            refresh_chart(self.state, self.w)
            self.w.header.set_status(f"R = {radius:.1f} px", "#22C55E")

        self._manual_points.clear()
        self.w.left_panel.manual_tab.reset()

    def on_manual_clear(self) -> None:
        self._manual_points.clear()
        self.w.left_panel.manual_tab.reset()
        self.w.original_panel.set_mode("normal")

        # Clear current frame's fit results before redraw
        idx = self.state.image_no
        if self.state.radius is not None:
            self.state.radius[idx] = 0
        if self.state.circle_fit_par is not None:
            self.state.circle_fit_par[idx] = [0, 0]
        if self.state.circle_xy is not None:
            self.state.circle_xy[idx] = None

        display_frame(self.state, self.w, idx, self._set_state)

        # Refresh R-t chart
        if self.state.radius is not None:
            frames = np.arange(1, len(self.state.radius) + 1)
            self.w.radius_chart.plot_all(frames, self.state.radius)

        self.w.header.set_status("Ready", "#22C55E")

    def clear_points(self) -> None:
        """Clear the manual points list (called on tab change)."""
        self._manual_points.clear()
