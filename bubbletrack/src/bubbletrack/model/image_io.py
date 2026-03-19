"""Image scanning, loading, normalisation and adaptive binarisation."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import cv2
import numpy as np

from bubbletrack.model.conventions import roi_to_slice

logger = logging.getLogger(__name__)


# Supported extensions in priority order
_EXTENSIONS = (".tiff", ".tif", ".png", ".jpg", ".jpeg", ".bmp")


def _natural_sort_key(s: str):
    """Sort key that handles embedded numbers naturally."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", s)
    ]


def scan_folder(folder: str) -> list[str]:
    """Return sorted image paths from *folder*.

    Scans for the first extension group that has files, in priority order
    (tiff > tif > png > jpg > bmp).  Files are natural-sorted by name.
    """
    folder = str(folder)
    for ext in _EXTENSIONS:
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(ext)
        ]
        if files:
            files.sort(key=lambda p: _natural_sort_key(os.path.basename(p)))
            return files
    return []


def detect_bit_depth(path: str) -> int:
    """Read the first image and return its max grey value (255 or 65535)."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return 255
    if img.dtype == np.uint16:
        return 65535
    return 255


def load_and_normalize(
    image_path: str,
    sensitivity: float,
    gridx: tuple[int, int],
    gridy: tuple[int, int],
    *,
    gaussian_sigma: float = 0.0,
    clahe_clip: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load an image, normalise to [0,1], adaptive-threshold, and extract ROI.

    Parameters
    ----------
    image_path : str
        Path to the image file.
    sensitivity : float
        Adaptive threshold sensitivity in [0, 1].  Higher = more white.
    gridx : (row_start, row_end)
        1-indexed inclusive row bounds for the ROI.
    gridy : (col_start, col_end)
        1-indexed inclusive column bounds for the ROI.

    Returns
    -------
    cur_img : ndarray
        Full normalised greyscale image in [0, 1].
    cur_img_binary : ndarray
        Full binary image (bool).
    cur_img_roi : ndarray
        ROI slice of *cur_img*.
    cur_img_binary_roi : ndarray
        ROI slice of *cur_img_binary*.
    """
    logger.debug("Loading image: %s", image_path)
    raw = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if raw is None:
        logger.warning("Cannot read image: %s", image_path)
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # Convert to greyscale if needed
    if raw.ndim == 3:
        raw = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)

    # Normalise to [0, 1]
    img_f = raw.astype(np.float64)
    img_min, img_max = img_f.min(), img_f.max()
    if img_max > img_min:
        cur_img = (img_f - img_min) / (img_max - img_min)
    else:
        cur_img = np.zeros_like(img_f)

    # Adaptive binarisation
    # MATLAB imbinarize 'adaptive' uses local mean with a sensitivity param.
    # sensitivity=0.5 is default (no offset).  Higher sensitivity -> more white.
    # block_size must be odd
    h, w = raw.shape[:2]
    block_size = int(np.ceil(min(h, w) / 16)) * 2 + 1
    block_size = max(block_size, 3)

    # For adaptive thresholding we need uint8 input
    if raw.dtype == np.uint16:
        raw_8 = (raw / 256).astype(np.uint8)
    else:
        raw_8 = raw.astype(np.uint8)

    # Pre-threshold filters
    if gaussian_sigma > 0:
        ksize = int(np.ceil(gaussian_sigma * 3)) * 2 + 1
        raw_8 = cv2.GaussianBlur(raw_8, (ksize, ksize), gaussian_sigma)

    if clahe_clip > 0:
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        raw_8 = clahe.apply(raw_8)

    # MATLAB: imbinarize(img, 'adaptive', 'Sensitivity', s)
    # OpenCV adaptiveThreshold: pixel > (mean - C) => 255
    # MATLAB offset maps: C = (sensitivity - 0.5) * range_per_block
    # Approximation: C ~ (sensitivity - 0.5) * 255
    c_val = (sensitivity - 0.5) * 255.0

    binary_8 = cv2.adaptiveThreshold(
        raw_8, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_val,  # OpenCV: pixel > (mean - C) => white; higher C => more white
    )
    cur_img_binary = binary_8 > 0

    # Extract ROI (1-indexed inclusive -> 0-indexed exclusive)
    rs, cs = roi_to_slice(gridx, gridy)
    cur_img_roi = cur_img[rs, cs]
    cur_img_binary_roi = cur_img_binary[rs, cs]

    return cur_img, cur_img_binary, cur_img_roi, cur_img_binary_roi
