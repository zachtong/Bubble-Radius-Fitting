"""Logarithmic mapping from slider value to minimum connected-component area."""

from __future__ import annotations


def compute_removing_factor(
    slider_value: float,
    gridx: tuple[int, int],
    gridy: tuple[int, int],
) -> int:
    """Map a 0-100 slider value to a pixel-area threshold (log scale).

    Parameters
    ----------
    slider_value : float
        Slider position in [0, 100].
    gridx : (row_start, row_end)
        ROI row bounds (1-indexed, inclusive).
    gridy : (col_start, col_end)
        ROI column bounds (1-indexed, inclusive).

    Returns
    -------
    int
        Minimum connected-component area for ``remove_small_objects``.
    """
    roi_area = (gridx[1] - gridx[0]) * (gridy[1] - gridy[0])

    min_area = 10
    max_area = max(round(roi_area * 0.5), min_area + 1)

    if slider_value <= 0:
        return min_area

    rf = round(min_area * (max_area / min_area) ** (slider_value / 100.0))
    return int(rf)
