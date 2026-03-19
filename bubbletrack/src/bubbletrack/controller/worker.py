"""Background worker thread for batch bubble detection + fitting."""

from __future__ import annotations

import logging

import numpy as np

from PyQt6.QtCore import QThread, pyqtSignal

from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.conventions import frame_to_display
from bubbletrack.model.detection import detect_bubble
from bubbletrack.model.image_io import load_and_normalize
from bubbletrack.model.removing_factor import compute_removing_factor

logger = logging.getLogger(__name__)


class BatchWorker(QThread):
    """Process a range of frames in the background.

    Signals
    -------
    progress(current, total)
    frame_done(frame_idx, radius, edge_xy, binary_roi)
    finished()
    error(str)
    """

    progress = pyqtSignal(int, int)
    frame_done = pyqtSignal(int, float, object, object)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        images: list[str],
        start: int,
        end: int,
        sensitivity: float,
        gridx: tuple[int, int],
        gridy: tuple[int, int],
        removing_factor_slider: int,
        bubble_cross_edges: list[bool],
        removing_obj_radius: int = 0,
        gaussian_sigma: float = 0.0,
        clahe_clip: float = 0.0,
        closing_radius: int = 0,
        opening_radius: int = 0,
        max_radius: float = float("inf"),
    ):
        super().__init__()
        self._images = images
        self._start = start        # 0-indexed
        self._end = end            # 0-indexed inclusive
        self._sensitivity = sensitivity
        self._gridx = gridx
        self._gridy = gridy
        self._rf_slider = removing_factor_slider
        self._edges = bubble_cross_edges
        self._obj_radius = removing_obj_radius
        self._gaussian_sigma = gaussian_sigma
        self._clahe_clip = clahe_clip
        self._closing_radius = closing_radius
        self._opening_radius = opening_radius
        self._max_radius = max_radius
        self._stop = False

    def request_stop(self):
        self._stop = True

    def run(self):
        total = self._end - self._start + 1
        rf = compute_removing_factor(self._rf_slider, self._gridx, self._gridy)
        logger.info("Batch processing frames %d-%d", self._start, self._end)

        for count, i in enumerate(range(self._start, self._end + 1)):
            if self._stop:
                logger.warning("Batch stopped by user at frame %d", i)
                break
            try:
                _, _, _, binary_roi = load_and_normalize(
                    self._images[i], self._sensitivity,
                    self._gridx, self._gridy,
                    gaussian_sigma=self._gaussian_sigma,
                    clahe_clip=self._clahe_clip,
                )
                processed, edge_xy = detect_bubble(
                    binary_roi, self._edges, rf,
                    self._gridx, self._gridy,
                    self._obj_radius,
                    opening_radius=self._opening_radius,
                    closing_radius=self._closing_radius,
                )
                if edge_xy.shape[0] >= 3:
                    rc, cc, radius = circle_fit_taubin(edge_xy)
                    if np.isnan(radius) or radius > self._max_radius:
                        radius = -1.0
                        edge_xy = np.empty((0, 2))
                else:
                    radius = -1.0
                    edge_xy = np.empty((0, 2))

                self.frame_done.emit(i, float(radius), edge_xy, processed)
            except Exception as exc:
                logger.error("Batch error: %s", exc)
                self.error.emit(f"Frame {frame_to_display(i)}: {exc}")
                self.frame_done.emit(i, -1.0, np.empty((0, 2)), None)

            self.progress.emit(count + 1, total)

        self.finished.emit()
