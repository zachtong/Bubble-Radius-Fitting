"""Grid search for optimal threshold and removing factor."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def optimize_parameters(
    process_fn,
    reference_frames: dict[int, float],
    *,
    thr_range: tuple[float, float, int] = (0.1, 0.9, 9),
    rf_range: tuple[int, int, int] = (10, 100, 10),
) -> dict:
    """Find threshold & removing factor that minimize radius error on reference frames.

    Parameters
    ----------
    process_fn : callable(thr: float, rf: int, idx: int) -> float
        A callable that takes (threshold, removing_factor, frame_index) and returns
        the fitted radius for that frame.  Returns NaN on failure.
    reference_frames : dict[int, float]
        Ground truth mapping: ``{frame_idx: expected_radius}``.
    thr_range : (start, stop, num_steps)
        Threshold search range passed to ``np.linspace``.
    rf_range : (start, stop, step)
        Removing factor search range passed to ``range``.

    Returns
    -------
    dict with keys: ``"img_thr"``, ``"removing_factor"``, ``"error"``

    Raises
    ------
    ValueError
        If *reference_frames* is empty.
    """
    if not reference_frames:
        raise ValueError("No reference frames provided")

    best: dict = {"img_thr": 0.5, "removing_factor": 90, "error": float("inf")}

    thresholds = np.linspace(thr_range[0], thr_range[1], thr_range[2])
    rfs = range(rf_range[0], rf_range[1] + 1, rf_range[2])

    for thr in thresholds:
        for rf in rfs:
            total_error = 0.0
            for idx, expected_r in reference_frames.items():
                r = process_fn(thr, rf, idx)
                if np.isnan(r) or r <= 0:
                    total_error += 1000.0  # penalty for failed fit
                else:
                    total_error += (r - expected_r) ** 2
            mse = total_error / len(reference_frames)
            if mse < best["error"]:
                best = {
                    "img_thr": float(thr),
                    "removing_factor": int(rf),
                    "error": float(mse),
                }

    logger.info(
        "Auto-optimize result: thr=%.3f, rf=%d, error=%.4f",
        best["img_thr"],
        best["removing_factor"],
        best["error"],
    )
    return best
