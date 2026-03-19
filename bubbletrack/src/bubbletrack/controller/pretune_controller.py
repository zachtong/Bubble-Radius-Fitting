"""PretuneController — threshold, ROI, edge flags, single-frame fitting."""

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
from bubbletrack.model.cache import ImageCache
from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.conventions import clamp_roi
from bubbletrack.model.detection import detect_bubble
from bubbletrack.model.image_io import load_and_normalize
from bubbletrack.model.removing_factor import compute_removing_factor
from bubbletrack.model.state import update_state

logger = logging.getLogger(__name__)


class PretuneController(BaseController):
    """Manages pre-tune parameters and single-frame fitting."""

    def __init__(self, bus: EventBus, get_state, set_state, window,
                 display_timer, preview_timer, get_max_radius,
                 cache: ImageCache | None = None) -> None:
        super().__init__(bus, get_state, set_state, window)
        self._display_timer = display_timer
        self._preview_timer = preview_timer
        self._get_max_radius = get_max_radius
        self._cache = cache

        # Preview detection cache: skip load_and_normalize when only RF changes
        self._last_binary_roi = None
        self._last_binary_params: tuple | None = None

    # -- public handlers -------------------------------------------------- #

    def on_threshold_changed(self, v: float) -> None:
        self._update(img_thr=v)
        self._invalidate_binary_cache()
        if self._cache is not None:
            self._cache.invalidate()
        self._display_timer.start()  # debounced

    def on_removing_factor_changed(self, v: int) -> None:
        self._update(removing_factor=v)
        self._preview_timer.start()  # debounced

    def on_filters_changed(self) -> None:
        p = self.w.left_panel.pretune_tab.get_filter_params()
        self._update(
            gaussian_sigma=p["gaussian_sigma"],
            clahe_clip=p["clahe_clip"],
            closing_radius=p["closing_radius"],
            opening_radius=p["opening_radius"],
        )
        self._invalidate_binary_cache()
        if self._cache is not None:
            self._cache.invalidate()
        self._preview_timer.start()  # debounced

    def _invalidate_binary_cache(self) -> None:
        """Clear the preview binary ROI cache."""
        self._last_binary_roi = None
        self._last_binary_params = None

    def on_edges_changed(self) -> None:
        self._update(
            bubble_cross_edges=tuple(self.w.left_panel.pretune_tab.get_edge_flags()),
        )
        self.preview_detection()

    def preview_detection(self) -> None:
        """Run full detect_bubble pipeline for preview.

        MATLAB's realtimeDisplay_connectedArea calls detectBubble with
        removeobjradius=0 to skip morphological closing for speed.

        When only removing_factor changes, the cached binary_roi is reused
        to skip the expensive load_and_normalize step.
        """
        if not self.state.images:
            return
        idx = self.state.image_no
        rf = compute_removing_factor(
            self.state.removing_factor, self.state.gridx, self.state.gridy,
        )
        try:
            # Check if binary ROI can be reused (only RF or edges changed)
            current_params = (
                self.state.images[idx],
                self.state.img_thr,
                self.state.gridx,
                self.state.gridy,
                self.state.gaussian_sigma,
                self.state.clahe_clip,
            )
            if (current_params == self._last_binary_params
                    and self._last_binary_roi is not None):
                binary_roi = self._last_binary_roi
            else:
                _, _, _, binary_roi = load_and_normalize(
                    self.state.images[idx], self.state.img_thr,
                    self.state.gridx, self.state.gridy,
                    gaussian_sigma=self.state.gaussian_sigma,
                    clahe_clip=self.state.clahe_clip,
                )
                self._last_binary_roi = binary_roi
                self._last_binary_params = current_params

            processed, _ = detect_bubble(
                binary_roi, self.state.bubble_cross_edges, rf,
                self.state.gridx, self.state.gridy,
                0,  # skip legacy morphological closing for preview speed
                opening_radius=self.state.opening_radius,
                closing_radius=self.state.closing_radius,
            )
            self.w.binary_panel.set_image(processed)
        except Exception:
            pass

    def on_select_roi(self) -> None:
        self.w.original_panel.set_mode("roi")
        self.w.header.set_status("Drag on image to select ROI", "#FCD34D")

    def on_roi_selected(self, r0: int, r1: int, c0: int, c1: int) -> None:
        # Clamp to actual image dimensions
        if self.state.cur_img is not None:
            h, w = self.state.cur_img.shape[:2]
            (r0, r1), (c0, c1) = clamp_roi((r0, r1), (c0, c1), h, w)
        self._update(gridx=(r0, r1), gridy=(c0, c1))
        self._invalidate_binary_cache()
        if self._cache is not None:
            self._cache.invalidate()
        self.w.left_panel.pretune_tab.set_roi((r0, r1), (c0, c1))
        self.w.header.set_status("ROI selected", "#22C55E")
        display_frame(
            self.state, self.w, self.state.image_no, self._set_state,
            self._cache,
        )

    def on_pretune_fit(self) -> None:
        """Detect + fit circle for the current single frame."""
        if not self.state.images:
            return

        self.w.header.set_status("Fitting...", "#FCD34D")
        idx = self.state.image_no
        rf = compute_removing_factor(
            self.state.removing_factor, self.state.gridx, self.state.gridy,
        )

        try:
            _, _, _, binary_roi = load_and_normalize(
                self.state.images[idx], self.state.img_thr,
                self.state.gridx, self.state.gridy,
                gaussian_sigma=self.state.gaussian_sigma,
                clahe_clip=self.state.clahe_clip,
            )
            processed, edge_xy = detect_bubble(
                binary_roi, self.state.bubble_cross_edges, rf,
                self.state.gridx, self.state.gridy,
                self.state.removing_obj_radius,
                opening_radius=self.state.opening_radius,
                closing_radius=self.state.closing_radius,
            )

            self.w.binary_panel.set_image(processed)

            if edge_xy.shape[0] >= 3:
                rc, cc, radius = circle_fit_taubin(edge_xy)
                if np.isnan(radius) or radius > self._get_max_radius():
                    logger.error("Fit failed for frame %d", idx)
                    self.w.header.set_status(
                        f"Radius outlier ({radius:.0f} px), skipped", "#FCD34D",
                    )
                else:
                    logger.info("Fit frame %d: radius=%.2f", idx, radius)
                    self.state.radius[idx] = radius
                    self.state.circle_fit_par[idx] = [rc, cc]
                    self.state.circle_xy[idx] = edge_xy

                    # Clear old overlays before drawing new results
                    redraw_original(self.state, self.w)
                    self.w.original_panel.draw_circle(rc, cc, radius, "#3B82F6")
                    self.w.original_panel.draw_points(edge_xy, "#EF4444", 2.0)
                    refresh_chart(self.state, self.w)
                    self.w.header.set_status(
                        f"R = {radius:.1f} px", "#22C55E",
                    )
            else:
                self.w.header.set_status("Too few edge points", "#EF4444")
        except Exception as exc:
            self.w.header.set_status(f"Error: {exc}", "#EF4444")
