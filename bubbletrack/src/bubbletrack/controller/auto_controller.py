"""AutoController — batch automatic fitting across frame ranges."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QTimer

from bubbletrack.controller.base import BaseController
from bubbletrack.controller.display_mixin import display_frame, refresh_chart
from bubbletrack.controller.worker import BatchWorker
from bubbletrack.event_bus import EventBus
from bubbletrack.model.cache import ImageCache
from bubbletrack.model.anomaly import detect_anomalies
from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.constants import AUTO_DISPLAY_THROTTLE_MS
from bubbletrack.model.conventions import frame_to_display
from bubbletrack.model.export import export_r_data
from bubbletrack.model.image_io import load_and_normalize
from bubbletrack.model.state import update_state

logger = logging.getLogger(__name__)

AUTOSAVE_INTERVAL = 50  # frames between incremental auto-saves


class AutoController(BaseController):
    """Manages automatic batch fitting with a background worker thread."""

    def __init__(self, bus: EventBus, get_state, set_state, window,
                 get_max_radius, cache: ImageCache | None = None) -> None:
        super().__init__(bus, get_state, set_state, window)
        self._worker: BatchWorker | None = None
        self._auto_last_display: float = 0.0
        self._auto_start_time: float = 0.0
        self._get_max_radius = get_max_radius
        self._cache = cache

    # -- public handlers -------------------------------------------------- #

    def on_auto_fit(self) -> None:
        if not self.state.images:
            return

        from bubbletrack.model.conventions import display_to_frame

        start, end = self.w.left_panel.automatic_tab.get_range()
        start_idx = display_to_frame(start)
        end_idx = display_to_frame(end)

        self._worker = BatchWorker(
            images=self.state.images,
            start=start_idx,
            end=end_idx,
            sensitivity=self.state.img_thr,
            gridx=self.state.gridx,
            gridy=self.state.gridy,
            removing_factor_slider=self.state.removing_factor,
            bubble_cross_edges=self.state.bubble_cross_edges,
            removing_obj_radius=self.state.removing_obj_radius,
            gaussian_sigma=self.state.gaussian_sigma,
            clahe_clip=self.state.clahe_clip,
            closing_radius=self.state.closing_radius,
            opening_radius=self.state.opening_radius,
            max_radius=self._get_max_radius(),
        )
        self._worker.progress.connect(self._on_auto_progress)
        self._worker.frame_done.connect(self._on_auto_frame_done)
        self._worker.finished.connect(self._on_auto_finished)
        self._worker.error.connect(
            lambda msg: self.w.header.set_status(msg, "#FCD34D"),
        )

        self.w.left_panel.automatic_tab.set_running(True)
        self.w.header.set_status("Processing...", "#FCD34D")
        self.w.status_bar.update_mode("Automatic")
        self._auto_last_display = 0.0  # force first frame to display
        self._auto_start_time = time.monotonic()
        self._worker.start()

    def on_auto_stop(self) -> None:
        if self._worker:
            self._worker.request_stop()
            self.w.header.set_status("Stopping...", "#FCD34D")

    def on_auto_clear(self) -> None:
        if self.state.images:
            self.state = self.state.with_results_initialized(len(self.state.images))
        self.w.left_panel.automatic_tab.reset_progress()
        self.w.radius_chart.clear()
        display_frame(
            self.state, self.w, self.state.image_no, self._set_state,
            self._cache,
        )
        self.w.header.set_status("Cleared", "#22C55E")

    # -- internal signal handlers ----------------------------------------- #
    # Thread safety: BatchWorker runs on a QThread and communicates results
    # via frame_done signal. State mutations happen here on the main thread
    # (guaranteed by Qt's queued signal/slot connection for cross-thread signals).

    def _on_auto_progress(self, current: int, total: int) -> None:
        # Calculate ETA based on elapsed time
        if current > 0:
            elapsed = time.monotonic() - self._auto_start_time
            eta_sec = elapsed / current * (total - current)
            minutes, secs = divmod(int(eta_sec), 60)
            eta_text = f"{minutes}m {secs}s remaining"
        else:
            eta_text = "Calculating..."
        self.w.left_panel.automatic_tab.set_progress(current, total, eta_text)

    def _on_auto_frame_done(self, idx: int, radius: float, edge_xy, binary_roi) -> None:
        # Always update state (fast, no UI)
        self.state.radius[idx] = radius
        if edge_xy is not None and edge_xy.shape[0] > 0:
            rc, cc, _ = circle_fit_taubin(edge_xy)
            self.state.circle_fit_par[idx] = [rc, cc]
            self.state.circle_xy[idx] = edge_xy

        # Incremental auto-save every AUTOSAVE_INTERVAL frames
        if (idx + 1) % AUTOSAVE_INTERVAL == 0 and self.state.folder_path:
            autosave_path = Path(self.state.folder_path) / ".bubbletrack_autosave.mat"
            try:
                export_r_data(
                    str(autosave_path),
                    self.state.radius,
                    self.state.circle_fit_par,
                    self.state.circle_xy,
                )
                logger.info("Auto-saved at frame %d to %s", idx, autosave_path)
            except Exception as exc:
                logger.warning("Auto-save failed at frame %d: %s", idx, exc)

        # Throttle display updates so the UI thread can process user events
        now = time.monotonic()
        if now - self._auto_last_display < AUTO_DISPLAY_THROTTLE_MS / 1000.0:
            return
        self._auto_last_display = now

        # Update frame scrubber WITHOUT triggering on_frame_changed
        self.w.frame_scrubber.blockSignals(True)
        self.w.frame_scrubber.set_value(idx)
        self.w.frame_scrubber.blockSignals(False)
        self._update(image_no=idx)

        self.w.status_bar.update_frame(
            frame_to_display(idx), self.state.total_frames,
        )

        # Load and display original image for current frame
        try:
            cur_img, _, _, _ = load_and_normalize(
                self.state.images[idx], self.state.img_thr,
                self.state.gridx, self.state.gridy,
                gaussian_sigma=self.state.gaussian_sigma,
                clahe_clip=self.state.clahe_clip,
            )
            self.w.original_panel.set_image(cur_img)
            self.w.original_panel.draw_roi_rect(
                self.state.gridx, self.state.gridy,
            )
            # Draw fitted circle and edge points on original image
            if radius > 0 and edge_xy is not None and edge_xy.shape[0] > 0:
                rc, cc, _ = circle_fit_taubin(edge_xy)
                self.w.original_panel.draw_circle(rc, cc, radius, "#3B82F6")
                self.w.original_panel.draw_points(edge_xy, "#EF4444", 2.0)
        except Exception:
            pass

        # Show binary result from worker (no disk I/O needed)
        if binary_roi is not None:
            self.w.binary_panel.set_image(binary_roi)

        # Update chart periodically
        if radius > 0:
            refresh_chart(self.state, self.w)

    def _on_auto_finished(self) -> None:
        self.w.left_panel.automatic_tab.set_running(False)
        self.w.header.set_status("Done", "#22C55E")
        # Final full display update
        display_frame(
            self.state, self.w, self.state.image_no, self._set_state,
            self._cache,
        )
        # Refresh chart with all data and run anomaly detection
        if self.state.radius is not None:
            frames = np.arange(1, len(self.state.radius) + 1)
            self.w.radius_chart.plot_all(frames, self.state.radius)

            anomaly_mask = detect_anomalies(self.state.radius)
            self.w.radius_chart.mark_anomalies(frames, self.state.radius, anomaly_mask)
            anomaly_count = int(anomaly_mask.sum())
            if anomaly_count > 0:
                self.w.header.set_status(
                    f"Done — {anomaly_count} anomalies detected", "#FCD34D",
                )
            logger.info("Anomaly detection: %d / %d frames flagged",
                        anomaly_count, len(self.state.radius))
