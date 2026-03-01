"""Bubble detection pipeline: expand, filter, label, crop, edge-detect."""

from __future__ import annotations

import numpy as np
from scipy import ndimage
from skimage import measure, morphology


# --- Constants matching MATLAB implementation ---
MAX_AXIS_RATIO = 2.2
MAX_ECCENTRICITY = 1.6
MIN_HOLE_AREA = 40


def expand_binary_image(
    bw: np.ndarray,
    bubble_cross_edges: list[bool],
) -> np.ndarray:
    """Double the image in the first non-crossing direction, filled with True.

    Parameters
    ----------
    bw : 2-D bool array
        Binary ROI image.
    bubble_cross_edges : list of 4 bool
        ``[Top, Right, Down, Left]`` — True if the bubble crosses that edge.
    """
    h, w = bw.shape
    non_cross = [not e for e in bubble_cross_edges]
    # Find first non-crossing direction (1-indexed: 1=Top, 2=Right, 3=Down, 4=Left)
    direction = None
    for i, nc in enumerate(non_cross):
        if nc:
            direction = i + 1
            break
    if direction is None:
        direction = 1  # fallback: expand top

    if direction == 1:  # Top: original goes to bottom half
        expanded = np.ones((h * 2, w), dtype=bool)
        expanded[h:2 * h, :w] = bw
    elif direction == 2:  # Right: original goes to left half
        expanded = np.ones((h, w * 2), dtype=bool)
        expanded[:h, :w] = bw
    elif direction == 3:  # Down: original goes to top half
        expanded = np.ones((h * 2, w), dtype=bool)
        expanded[:h, :w] = bw
    elif direction == 4:  # Left: original goes to right half
        expanded = np.ones((h, w * 2), dtype=bool)
        expanded[:h, w:2 * w] = bw

    return expanded


def crop_expanded_image(
    expanded: np.ndarray,
    orig_rows: int,
    orig_cols: int,
    bubble_cross_edges: list[bool],
) -> np.ndarray:
    """Reverse :func:`expand_binary_image` — crop back to original size."""
    non_cross = [not e for e in bubble_cross_edges]
    direction = None
    for i, nc in enumerate(non_cross):
        if nc:
            direction = i + 1
            break
    if direction is None:
        direction = 1

    if direction == 1:
        return expanded[orig_rows:2 * orig_rows, :orig_cols]
    elif direction == 2:
        return expanded[:orig_rows, :orig_cols]
    elif direction == 3:
        return expanded[:orig_rows, :orig_cols]
    elif direction == 4:
        return expanded[:orig_rows, orig_cols:2 * orig_cols]


def detect_bubble(
    binary_roi: np.ndarray,
    bubble_cross_edges: list[bool],
    removing_factor: int,
    gridx: tuple[int, int],
    gridy: tuple[int, int],
    removing_obj_radius: int = 0,
    *,
    opening_radius: int = 0,
    closing_radius: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Detect a bubble boundary in *binary_roi*.

    Parameters
    ----------
    binary_roi : 2-D bool array
        Binary image of the ROI (True = foreground/white).
    bubble_cross_edges : list of 4 bool
        ``[Top, Right, Down, Left]``.
    removing_factor : int
        Min connected-component area to keep.
    gridx, gridy : (start, end)
        1-indexed ROI bounds for coordinate conversion.
    removing_obj_radius : int
        Disk radius for morphological closing (0 = skip).

    Returns
    -------
    processed : 2-D bool array
        Processed binary mask (original ROI size) of the detected bubble.
    edge_xy : ndarray of shape (N, 2)
        ``[row, col]`` edge coordinates in **full-image** space (1-indexed).
    """
    bw = binary_roi.astype(bool)
    orig_h, orig_w = bw.shape

    # Expand for edge-crossing bubbles
    expanded = expand_binary_image(bw, bubble_cross_edges)

    # Remove small connected white areas
    expanded = morphology.remove_small_objects(expanded, min_size=removing_factor)

    # Optional morphological opening (remove bead spurs on edges)
    if opening_radius > 0:
        selem = morphology.disk(opening_radius)
        expanded = morphology.opening(expanded, selem)

    # Optional morphological closing (fill small holes, smooth boundary)
    effective_closing = closing_radius if closing_radius > 0 else removing_obj_radius
    if effective_closing > 1:
        selem = morphology.disk(effective_closing)
        expanded = morphology.closing(expanded, selem)
        expanded = ndimage.binary_fill_holes(expanded)

    # Invert: bubble interior (dark in original) becomes foreground
    inverted = ~expanded
    labels = measure.label(inverted)
    props = measure.regionprops(labels)

    if not props:
        # No regions found — return empty
        processed = np.zeros((orig_h, orig_w), dtype=bool)
        return processed, np.empty((0, 2), dtype=np.float64)

    # Filter by shape: reject elongated / eccentric blobs
    short_side = min(inverted.shape)
    valid_props = []
    for p in props:
        if p.axis_major_length > MAX_AXIS_RATIO * short_side:
            continue
        if p.axis_minor_length > 0 and (
            p.axis_major_length > MAX_ECCENTRICITY * p.axis_minor_length
        ):
            continue
        valid_props.append(p)

    if not valid_props:
        # Fallback: use the largest region without filtering
        valid_props = props

    # Keep the largest blob
    largest = max(valid_props, key=lambda p: p.area)
    blob_mask = labels == largest.label

    # Remove small holes inside the blob
    holes = ~blob_mask
    holes_cleaned = morphology.remove_small_objects(holes, min_size=MIN_HOLE_AREA)
    blob_mask = ~holes_cleaned

    # Crop back to original ROI size
    processed = crop_expanded_image(blob_mask, orig_h, orig_w, bubble_cross_edges)
    processed = processed.astype(bool)

    # Edge detection via morphological gradient (dilation XOR original)
    selem_3x3 = np.ones((3, 3), dtype=bool)
    dilated = morphology.dilation(processed, selem_3x3)
    edge_mask = dilated ^ processed
    rows, cols = np.where(edge_mask)

    # Convert to full-image 1-indexed coordinates
    edge_xy = np.column_stack([
        rows + gridx[0],
        cols + gridy[0],
    ]).astype(np.float64)

    return processed, edge_xy
