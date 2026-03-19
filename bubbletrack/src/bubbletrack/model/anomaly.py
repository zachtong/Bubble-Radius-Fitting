"""Anomaly detection for bubble radius time series.

Identifies three types of anomalous frames:
1. Fit failures (NaN or non-positive radius)
2. Statistical outliers (z-score via MAD)
3. Large frame-to-frame jumps
"""

from __future__ import annotations

import numpy as np

# MAD-to-std conversion factor for normally distributed data
_MAD_SCALE = 1.4826


def detect_anomalies(
    radius: np.ndarray,
    *,
    nan_is_anomaly: bool = True,
    zscore_threshold: float = 3.0,
    jump_threshold_pct: float = 50.0,
) -> np.ndarray:
    """Return boolean mask of anomalous frames.

    Parameters
    ----------
    radius : np.ndarray
        1-D array of fitted radii (NaN or <= 0 for failed fits).
    nan_is_anomaly : bool
        If True, mark NaN / non-positive entries as anomalies.
    zscore_threshold : float
        Modified z-score threshold (based on MAD) for outlier detection.
    jump_threshold_pct : float
        Maximum allowed frame-to-frame change as a percentage of the
        median radius.  Frames exceeding this are flagged.

    Returns
    -------
    np.ndarray
        Boolean array of same length as *radius*; True = anomalous.
    """
    radius = np.asarray(radius, dtype=float)
    n = len(radius)
    flags = np.zeros(n, dtype=bool)

    valid = np.isfinite(radius) & (radius > 0)

    # Type 1: fit failures
    if nan_is_anomaly:
        flags[~valid] = True

    # Need a minimum sample to compute statistics
    if valid.sum() < 5:
        return flags

    r_valid = radius[valid]
    median_r = np.median(r_valid)

    # Type 2: z-score outliers (MAD-based)
    mad = np.median(np.abs(r_valid - median_r))
    if mad > 0:
        z = np.abs(radius - median_r) / (mad * _MAD_SCALE)
        flags[valid & (z > zscore_threshold)] = True

    # Type 3: frame-to-frame jumps (vectorized)
    if median_r > 0:
        jump_limit = median_r * jump_threshold_pct / 100.0
        diffs = np.abs(np.diff(radius))
        both_valid = valid[:-1] & valid[1:]
        jump_mask = both_valid & (diffs > jump_limit)
        # Flag the *destination* frame of the jump (index i+1)
        flags[1:] |= jump_mask

    return flags
