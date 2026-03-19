"""Application state data class."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import numpy as np

from bubbletrack.model.constants import (
    DEFAULT_FPS,
    DEFAULT_REMOVING_FACTOR,
    DEFAULT_RMAX_FIT_LENGTH,
    DEFAULT_UM2PX,
)


@dataclass
class AppState:
    """Mutable application state shared between controller and views."""

    # Image file list
    images: list[str] = field(default_factory=list)
    folder_path: str = ""
    image_no: int = 0  # 0-indexed (UI displays +1)

    # Threshold / binarisation
    img_thr: float = 0.5  # adaptive sensitivity [0, 1]

    # ROI bounds (1-indexed inclusive, matching MATLAB convention)
    gridx: tuple[int, int] = (1, 1)
    gridy: tuple[int, int] = (1, 1)

    # Removing factor slider 0-100
    removing_factor: int = DEFAULT_REMOVING_FACTOR

    # Bubble-crosses-edge flags [Top, Right, Down, Left]
    bubble_cross_edges: list[bool] = field(default_factory=lambda: [False] * 4)

    # Morphological closing radius (0 = skip)
    removing_obj_radius: int = 0

    # Advanced filters (0 = disabled)
    gaussian_sigma: float = 0.0
    clahe_clip: float = 0.0
    closing_radius: int = 0
    opening_radius: int = 0

    # Results arrays — allocated after folder is loaded
    radius: np.ndarray | None = None          # (N,) float, -1 = unprocessed
    circle_fit_par: np.ndarray | None = None   # (N, 2) [row_c, col_c]
    circle_xy: list | None = None              # list of (M, 2) arrays

    # Display parameters
    img_grayscale_max: int = 65535
    um2px: float = DEFAULT_UM2PX
    fps: float = DEFAULT_FPS
    rmax_fit_length: int = DEFAULT_RMAX_FIT_LENGTH

    # Export
    save_path: str = ""

    # Runtime state
    realtime_play: bool = False
    cur_img: np.ndarray | None = None
    cur_img_binary_roi: np.ndarray | None = None

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @property
    def total_frames(self) -> int:
        return len(self.images)

    def init_results(self, n: int) -> None:
        """Allocate result arrays for *n* frames, filled with -1 / NaN."""
        self.radius = np.full(n, -1.0)
        self.circle_fit_par = np.full((n, 2), np.nan)
        self.circle_xy = [None] * n
