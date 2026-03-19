"""Export radius data to .mat files."""

from __future__ import annotations

import numpy as np
from scipy.io import savemat


def export_r_data(
    save_path: str,
    radius: np.ndarray,
    centers: np.ndarray,
    edge_pts: list,
) -> None:
    """Save raw fitting results to a ``.mat`` file.

    Parameters
    ----------
    save_path : str
        Full file path for the output ``.mat`` file.
    radius : (N,) array
        Fitted radii in pixels (-1 for unprocessed frames).
    centers : (N, 2) array
        Circle centres ``[row, col]``.
    edge_pts : list of (M, 2) arrays or None
        Edge coordinates per frame.
    """
    # Replace None entries with empty arrays for savemat compatibility
    cleaned_edges = [
        (e if e is not None else np.empty((0, 2))) for e in edge_pts
    ]

    savemat(save_path, {
        "Radius": radius.reshape(1, -1),
        "CircleFitPar": centers,
        "CircleXY": np.array(cleaned_edges, dtype=object),
    })


def export_rof_t_data(
    save_path: str,
    radius: np.ndarray,
    um2px: float,
    fps: float,
    rmax_fit_length: int,
) -> tuple[bool, str]:
    """Convert pixel radii to physical units and save to a ``.mat`` file.

    Parameters
    ----------
    save_path : str
        Full file path for the output ``.mat`` file.
    radius : (N,) array
        Fitted radii in pixels.
    um2px : float
        Micrometres per pixel.
    fps : float
        Frames per second.
    rmax_fit_length : int
        Window length for quadratic Rmax fitting (must be odd).

    Returns
    -------
    (success, message) : (bool, str)
    """
    deltax = um2px
    deltat = 1.0 / fps
    half = int(round((rmax_fit_length - 1) / 2))

    R = radius.copy().ravel().astype(np.float64)
    t = np.arange(1, len(R) + 1, dtype=np.float64)

    # Filter out invalid frames (radius <= 0 or NaN) before Rmax fitting
    valid_mask = (R > 0) & ~np.isnan(R)
    n_valid = int(valid_mask.sum())
    if n_valid < 3:
        return False, f"Not enough valid frames (need >= 3, got {n_valid})"

    # Find Rmax among valid frames only
    valid_R = R[valid_mask]
    valid_indices = np.where(valid_mask)[0]  # 0-indexed
    rmax_valid_pos = int(valid_R.argmax())
    rmax_val = valid_R[rmax_valid_pos]
    rmax_loc = int(valid_indices[rmax_valid_pos]) + 1  # 1-indexed

    # Boundary checks
    if rmax_loc - half < 1:
        return False, "Rmax_Fit_Length exceeds data range (left boundary)!"
    if rmax_loc + half > len(R):
        return False, "Rmax_Fit_Length exceeds data range (right boundary)!"

    # Build fit window, using only valid (radius > 0, non-NaN) frames
    window_indices_1based = np.arange(rmax_loc - half, rmax_loc + half + 1)
    window_mask = valid_mask[window_indices_1based - 1]
    fit_indices = window_indices_1based[window_mask]
    fit_vals = R[fit_indices - 1]  # back to 0-indexed for array access

    if len(fit_indices) < 3:
        return False, "Not enough valid frames in Rmax fit window (need >= 3)"

    # Quadratic fit
    try:
        p = np.polyfit(fit_indices, fit_vals, 2)
        if p[0] >= 0:
            # Not concave — use discrete max
            rmax_all = rmax_val
        else:
            fit_time_loc = -p[1] / (2.0 * p[0])
            fit_rmax = (4 * p[0] * p[2] - p[1] ** 2) / (4 * p[0])
            if fit_time_loc < 1 or fit_time_loc > len(R):
                rmax_all = rmax_val
            else:
                rmax_loc = fit_time_loc
                rmax_all = fit_rmax
    except Exception:
        rmax_all = rmax_val

    # Build output arrays — insert Rmax at the peak and shift time
    mask_before = t < rmax_loc
    mask_after = t > rmax_loc

    R_out = np.concatenate([R[mask_before], [rmax_all], R[mask_after]]) * deltax
    t_out = np.concatenate([
        t[mask_before] - rmax_loc,
        [0.0],
        t[mask_after] - rmax_loc,
    ]) * deltat
    rmax_all_phys = rmax_all * deltax
    rmax_time_loc_phys = rmax_loc * deltat

    savemat(save_path, {
        "t": t_out.reshape(-1, 1),
        "R": R_out.reshape(-1, 1),
        "RmaxAll": float(rmax_all_phys),
        "RmaxTimeLoc": float(rmax_time_loc_phys),
    })

    return True, ""
