"""AppController — wires UI signals to model logic and updates views."""

from __future__ import annotations

import logging
import os
import time

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.constants import (
    AUTO_DISPLAY_THROTTLE_MS,
    DISPLAY_DEBOUNCE_MS,
    PREVIEW_DEBOUNCE_MS,
)
from bubbletrack.model.conventions import display_to_frame, frame_to_display
from bubbletrack.model.detection import detect_bubble
from bubbletrack.model.export import export_r_data, export_rof_t_data
from bubbletrack.model.image_io import (
    detect_bit_depth,
    load_and_normalize,
    scan_folder,
)
from bubbletrack.model.removing_factor import compute_removing_factor
from bubbletrack.model.state import AppState
from bubbletrack.controller.worker import BatchWorker

logger = logging.getLogger(__name__)


class AppController:
    """Connects the MainWindow UI to the model layer.

    Signal flow: View -> Controller -> Model -> View (one-way).
    """

    def __init__(self, window):
        self.w = window
        self.state = AppState()
        self._worker: BatchWorker | None = None
        self._manual_points: list[tuple[float, float]] = []
        self._max_radius: float = float("inf")  # image long side; set on folder load

        # Debounce timers for slider-driven updates
        self._display_timer = QTimer()
        self._display_timer.setSingleShot(True)
        self._display_timer.setInterval(DISPLAY_DEBOUNCE_MS)
        self._display_timer.timeout.connect(
            lambda: self._display_frame(self.state.image_no)
        )

        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)
        self._preview_timer.timeout.connect(self._preview_detection)

        self._connect_signals()

    # ------------------------------------------------------------------ #
    #  Signal wiring
    # ------------------------------------------------------------------ #

    def _connect_signals(self):
        lp = self.w.left_panel

        # Image source
        lp.image_source.folder_selected.connect(self._on_folder_selected)

        # Frame scrubber
        self.w.frame_scrubber.value_changed.connect(self._on_frame_changed)

        # Pre-tune
        pt = lp.pretune_tab
        pt.threshold_changed.connect(self._on_threshold_changed)
        pt.removing_factor_changed.connect(self._on_removing_factor_changed)
        pt.edges_changed.connect(self._on_edges_changed)
        pt.fit_clicked.connect(self._on_pretune_fit)
        pt.select_roi_clicked.connect(self._on_select_roi)
        pt.frame_selected.connect(self._on_tab_frame_selected)
        pt.filters_changed.connect(self._on_filters_changed)

        # Manual
        mt = lp.manual_tab
        mt.select_clicked.connect(self._on_manual_select)
        mt.done_clicked.connect(self._on_manual_done)
        mt.clear_clicked.connect(self._on_manual_clear)
        mt.frame_selected.connect(self._on_tab_frame_selected)
        self.w.original_panel.point_clicked.connect(self._on_point_clicked)

        # Tab switching
        lp.tab_bar.tab_changed.connect(self._on_tab_changed)

        # Automatic
        at = lp.automatic_tab
        at.fit_clicked.connect(self._on_auto_fit)
        at.stop_clicked.connect(self._on_auto_stop)
        at.clear_clicked.connect(self._on_auto_clear)

        # Post processing
        pp = lp.post_processing
        pp.export_r_data_clicked.connect(self._on_export_r_data)
        pp.export_rof_t_clicked.connect(self._on_export_rof_t)

        # ROI selection from image panel
        self.w.original_panel.roi_selected.connect(self._on_roi_selected)

    # ------------------------------------------------------------------ #
    #  Folder / frame
    # ------------------------------------------------------------------ #

    def _on_folder_selected(self, folder: str):
        images = scan_folder(folder)
        if not images:
            self.w.header.set_status("No images found", "#EF4444")
            return

        logger.info("Loaded %d images from %s", len(images), folder)

        self.state.folder_path = folder
        self.state.images = images
        self.state.image_no = 0
        self.state.img_grayscale_max = detect_bit_depth(images[0])
        self.state.init_results(len(images))

        # Set default ROI to full image
        first_img, _, _, _ = load_and_normalize(images[0], 0.5, (1, 99999), (1, 99999))
        h, w = first_img.shape
        self.state.gridx = (1, h)
        self.state.gridy = (1, w)
        self._max_radius = float(max(h, w))

        # Update UI
        lp = self.w.left_panel
        lp.image_source.set_info(f"{len(images)} images  |  {os.path.basename(images[0])}")
        lp.pretune_tab.set_roi(self.state.gridx, self.state.gridy)
        lp.pretune_tab.set_frame_range(len(images))
        lp.manual_tab.set_frame_range(len(images))
        lp.automatic_tab.set_range(len(images))
        self.w.frame_scrubber.set_range(len(images))
        self.w.radius_chart.set_total_frames(len(images))
        self.w.status_bar.update_frame(frame_to_display(0), len(images))
        self.w.status_bar.update_format(os.path.splitext(images[0])[1])
        self.w.header.set_status("Ready", "#22C55E")

        self._display_frame(0)

    def _on_frame_changed(self, idx: int):
        self.state.image_no = idx
        self._display_frame(idx)
        # Sync tab frame spinboxes
        self.w.left_panel.pretune_tab.set_frame_value(idx)
        self.w.left_panel.manual_tab.set_frame_value(idx)

    def _on_tab_frame_selected(self, idx: int):
        """Frame selected from a tab's frame spinbox."""
        if not self.state.images or idx < 0 or idx >= len(self.state.images):
            return
        self.state.image_no = idx
        self.w.frame_scrubber.set_value(idx)
        self.w.left_panel.pretune_tab.set_frame_value(idx)
        self.w.left_panel.manual_tab.set_frame_value(idx)
        self._display_frame(idx)

    def _on_tab_changed(self, idx: int):
        """Tab bar switched — exit interactive modes, update status."""
        self.w.original_panel.set_mode("normal")
        self._manual_points.clear()
        self.w.left_panel.manual_tab.reset()
        tab_names = ("Pre-tune", "Manual", "Automatic")
        self.w.status_bar.update_mode(tab_names[idx] if idx < len(tab_names) else "")

    def _display_frame(self, idx: int):
        if not self.state.images:
            return
        try:
            cur_img, _, _, binary_roi = load_and_normalize(
                self.state.images[idx],
                self.state.img_thr,
                self.state.gridx,
                self.state.gridy,
                gaussian_sigma=self.state.gaussian_sigma,
                clahe_clip=self.state.clahe_clip,
            )
            self.state.cur_img = cur_img
            self.state.cur_img_binary_roi = binary_roi

            self.w.original_panel.set_image(cur_img)

            # For fitted frames, show the actual detection result;
            # for unfitted frames, show the raw threshold.
            if (self.state.radius is not None and self.state.radius[idx] > 0):
                rf = compute_removing_factor(
                    self.state.removing_factor,
                    self.state.gridx, self.state.gridy,
                )
                processed, _ = detect_bubble(
                    binary_roi, self.state.bubble_cross_edges, rf,
                    self.state.gridx, self.state.gridy,
                    self.state.removing_obj_radius,
                    opening_radius=self.state.opening_radius,
                    closing_radius=self.state.closing_radius,
                )
                self.w.binary_panel.set_image(processed)
            else:
                self.w.binary_panel.set_image(~binary_roi)

            # Draw ROI rectangle on original
            self.w.original_panel.draw_roi_rect(self.state.gridx, self.state.gridy)

            # Draw existing circle fit if available
            if (self.state.radius is not None
                    and self.state.radius[idx] > 0
                    and self.state.circle_fit_par is not None):
                rc = self.state.circle_fit_par[idx, 0]
                cc = self.state.circle_fit_par[idx, 1]
                r = self.state.radius[idx]
                self.w.original_panel.draw_circle(rc, cc, r, "#3B82F6")
                if self.state.circle_xy and self.state.circle_xy[idx] is not None:
                    self.w.original_panel.draw_points(
                        self.state.circle_xy[idx], "#EF4444", 2.0,
                    )

            self.w.status_bar.update_frame(
                frame_to_display(idx), self.state.total_frames,
            )
            self.w.status_bar.update_roi(self.state.gridx, self.state.gridy)
        except Exception as exc:
            self.w.header.set_status(f"Error: {exc}", "#EF4444")

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _refresh_chart(self):
        """Redraw R-t chart from state data (prevents duplicate markers)."""
        if self.state.radius is not None:
            frames = np.arange(1, len(self.state.radius) + 1)
            self.w.radius_chart.plot_all(frames, self.state.radius)

    def _redraw_original(self):
        """Clear overlays on original panel and re-draw ROI rect."""
        self.w.original_panel.clear_overlays()
        self.w.original_panel.draw_roi_rect(self.state.gridx, self.state.gridy)

    # ------------------------------------------------------------------ #
    #  Pre-tune
    # ------------------------------------------------------------------ #

    def _on_threshold_changed(self, v: float):
        self.state.img_thr = v
        self._display_timer.start()  # debounced

    def _on_removing_factor_changed(self, v: int):
        self.state.removing_factor = v
        self._preview_timer.start()  # debounced

    def _on_filters_changed(self):
        p = self.w.left_panel.pretune_tab.get_filter_params()
        self.state.gaussian_sigma = p["gaussian_sigma"]
        self.state.clahe_clip = p["clahe_clip"]
        self.state.closing_radius = p["closing_radius"]
        self.state.opening_radius = p["opening_radius"]
        self._preview_timer.start()  # debounced

    def _on_edges_changed(self):
        self.state.bubble_cross_edges = self.w.left_panel.pretune_tab.get_edge_flags()
        self._preview_detection()

    def _preview_detection(self):
        """Run full detect_bubble pipeline for preview (matches MATLAB behavior).

        MATLAB's realtimeDisplay_connectedArea calls detectBubble with
        removeobjradius=0 to skip morphological closing for speed.
        """
        if not self.state.images:
            return
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

    def _on_select_roi(self):
        self.w.original_panel.set_mode("roi")
        self.w.header.set_status("Drag on image to select ROI", "#FCD34D")

    def _on_roi_selected(self, r0: int, r1: int, c0: int, c1: int):
        # Clamp to actual image dimensions
        if self.state.cur_img is not None:
            h, w = self.state.cur_img.shape[:2]
            r0 = max(1, min(r0, h))
            r1 = max(1, min(r1, h))
            c0 = max(1, min(c0, w))
            c1 = max(1, min(c1, w))
        self.state.gridx = (r0, r1)
        self.state.gridy = (c0, c1)
        self.w.left_panel.pretune_tab.set_roi((r0, r1), (c0, c1))
        self.w.header.set_status("ROI selected", "#22C55E")
        self._display_frame(self.state.image_no)

    def _on_pretune_fit(self):
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
                if np.isnan(radius) or radius > self._max_radius:
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
                    self._redraw_original()
                    self.w.original_panel.draw_circle(rc, cc, radius, "#3B82F6")
                    self.w.original_panel.draw_points(edge_xy, "#EF4444", 2.0)
                    self._refresh_chart()
                    self.w.header.set_status(
                        f"R = {radius:.1f} px", "#22C55E",
                    )
            else:
                self.w.header.set_status("Too few edge points", "#EF4444")
        except Exception as exc:
            self.w.header.set_status(f"Error: {exc}", "#EF4444")

    # ------------------------------------------------------------------ #
    #  Manual mode
    # ------------------------------------------------------------------ #

    def _on_manual_select(self):
        self._manual_points.clear()
        self.w.left_panel.manual_tab.set_point_count(0)
        self.w.original_panel.set_mode("point")
        self.w.header.set_status("Click on bubble edge", "#FCD34D")
        self.w.status_bar.update_mode("Manual")

    def _on_point_clicked(self, x: float, y: float):
        """x = col, y = row in scene coordinates."""
        self._manual_points.append((y, x))  # store as (row, col)
        n = len(self._manual_points)
        self.w.left_panel.manual_tab.set_point_count(n)
        # Draw the point
        pt = np.array([[y, x]])
        self.w.original_panel.draw_points(pt, "#EF4444", 4.0)

    def _on_manual_done(self):
        self.w.original_panel.set_mode("normal")
        if len(self._manual_points) < 3:
            self.w.header.set_status("Need at least 3 points", "#EF4444")
            return

        xy = np.array(self._manual_points)
        rc, cc, radius = circle_fit_taubin(xy)

        idx = self.state.image_no
        if np.isnan(radius):
            self.w.header.set_status("Fitting failed", "#EF4444")
        elif radius > self._max_radius:
            self.w.header.set_status(
                f"Radius outlier ({radius:.0f} px), skipped", "#FCD34D",
            )
        else:
            self.state.radius[idx] = radius
            self.state.circle_fit_par[idx] = [rc, cc]
            self.state.circle_xy[idx] = xy

            # Clear old overlays before drawing new results
            self._redraw_original()
            self.w.original_panel.draw_circle(rc, cc, radius, "#3B82F6")
            self.w.original_panel.draw_points(xy, "#EF4444", 2.0)
            self._refresh_chart()
            self.w.header.set_status(f"R = {radius:.1f} px", "#22C55E")

        self._manual_points.clear()
        self.w.left_panel.manual_tab.reset()

    def _on_manual_clear(self):
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

        self._display_frame(idx)

        # Refresh R-t chart
        if self.state.radius is not None:
            frames = np.arange(1, len(self.state.radius) + 1)
            self.w.radius_chart.plot_all(frames, self.state.radius)

        self.w.header.set_status("Ready", "#22C55E")

    # ------------------------------------------------------------------ #
    #  Automatic mode
    # ------------------------------------------------------------------ #

    def _on_auto_fit(self):
        if not self.state.images:
            return

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
            max_radius=self._max_radius,
        )
        self._worker.progress.connect(self._on_auto_progress)
        self._worker.frame_done.connect(self._on_auto_frame_done)
        self._worker.finished.connect(self._on_auto_finished)
        self._worker.error.connect(lambda msg: self.w.header.set_status(msg, "#FCD34D"))

        self.w.left_panel.automatic_tab.set_running(True)
        self.w.header.set_status("Processing...", "#FCD34D")
        self.w.status_bar.update_mode("Automatic")
        self._auto_last_display = 0.0  # force first frame to display
        self._worker.start()

    def _on_auto_progress(self, current: int, total: int):
        self.w.left_panel.automatic_tab.set_progress(current, total)

    def _on_auto_frame_done(self, idx: int, radius: float, edge_xy, binary_roi):
        # Always update state (fast, no UI)
        self.state.radius[idx] = radius
        if edge_xy is not None and edge_xy.shape[0] > 0:
            rc, cc, _ = circle_fit_taubin(edge_xy)
            self.state.circle_fit_par[idx] = [rc, cc]
            self.state.circle_xy[idx] = edge_xy

        # Throttle display updates so the UI thread can process user events
        # (e.g. stop button clicks)
        now = time.monotonic()
        if now - self._auto_last_display < AUTO_DISPLAY_THROTTLE_MS / 1000.0:
            return
        self._auto_last_display = now

        # Update frame scrubber WITHOUT triggering _on_frame_changed
        self.w.frame_scrubber.blockSignals(True)
        self.w.frame_scrubber.set_value(idx)
        self.w.frame_scrubber.blockSignals(False)
        self.state.image_no = idx

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
            self._refresh_chart()

    def _on_auto_finished(self):
        self.w.left_panel.automatic_tab.set_running(False)
        self.w.header.set_status("Done", "#22C55E")
        # Final full display update
        self._display_frame(self.state.image_no)
        # Refresh chart with all data
        if self.state.radius is not None:
            frames = np.arange(1, len(self.state.radius) + 1)
            self.w.radius_chart.plot_all(frames, self.state.radius)

    def _on_auto_stop(self):
        if self._worker:
            self._worker.request_stop()
            self.w.header.set_status("Stopping...", "#FCD34D")

    def _on_auto_clear(self):
        if self.state.images:
            self.state.init_results(len(self.state.images))
        self.w.left_panel.automatic_tab.reset_progress()
        self.w.radius_chart.clear()
        self._display_frame(self.state.image_no)
        self.w.header.set_status("Cleared", "#22C55E")

    # ------------------------------------------------------------------ #
    #  Export
    # ------------------------------------------------------------------ #

    def _default_export_dir(self) -> str:
        """Return the image folder as default export directory, or home."""
        return self.state.folder_path or os.path.expanduser("~")

    def _on_export_r_data(self):
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        default = os.path.join(self._default_export_dir(), "radius_pixel.mat")
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Pixel Data", default,
            "MAT Files (*.mat);;All Files (*)",
        )
        if not path:
            return  # user cancelled

        try:
            export_r_data(
                path,
                self.state.radius,
                self.state.circle_fit_par,
                self.state.circle_xy,
            )
            logger.info("Export: %s", path)
            pp.set_status(f"Exported: {os.path.basename(path)}", True)
        except Exception as exc:
            pp.set_status(f"Error: {exc}", False)

    def _on_export_rof_t(self):
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        default = os.path.join(
            self._default_export_dir(), "radius_time_physical.mat",
        )
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Physical Data", default,
            "MAT Files (*.mat);;All Files (*)",
        )
        if not path:
            return  # user cancelled

        try:
            ok, msg = export_rof_t_data(
                path,
                self.state.radius,
                pp.get_scale(),
                pp.get_fps(),
                pp.get_fit_length(),
            )
            if ok:
                logger.info("Export: %s", path)
                pp.set_status(f"Exported: {os.path.basename(path)}", True)
                self.w.status_bar.update_scale(pp.get_scale())
            else:
                pp.set_status(msg, False)
        except Exception as exc:
            pp.set_status(f"Error: {exc}", False)
