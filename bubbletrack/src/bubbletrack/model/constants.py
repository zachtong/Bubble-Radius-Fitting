"""Centralised constants for the BubbleTrack model layer.

Every magic number used in the detection, fitting, and export pipelines
lives here so that values are documented, discoverable, and easy to tune.
"""

from __future__ import annotations

# ------------------------------------------------------------------ #
#  Detection pipeline
# ------------------------------------------------------------------ #

MAX_AXIS_RATIO: float = 2.2
"""Reject blobs whose major axis exceeds this multiple of the image short side."""

MAX_ECCENTRICITY: float = 1.6
"""Reject blobs whose major/minor axis ratio exceeds this value."""

MIN_HOLE_AREA: int = 40
"""Minimum hole area (px) inside the bubble blob to keep (smaller holes are filled)."""

# ------------------------------------------------------------------ #
#  Removing factor (slider -> area mapping)
# ------------------------------------------------------------------ #

RF_MIN_AREA: int = 10
"""Minimum connected-component area at the low end of the slider."""

RF_MAX_AREA_FRACTION: float = 0.5
"""Fraction of ROI area used as upper bound for the removing-factor slider."""

# ------------------------------------------------------------------ #
#  Circle fitting (Taubin algorithm)
# ------------------------------------------------------------------ #

TAUBIN_EPSILON: float = 1e-12
"""Convergence tolerance for Newton's method in the Taubin fitter."""

TAUBIN_MAX_ITER: int = 20
"""Maximum Newton iterations for the Taubin fitter."""

TAUBIN_MIN_POINTS: int = 3
"""Minimum number of boundary points required for circle fitting."""

MIN_POINT_DISTANCE_PX: float = 5.0
"""Minimum Euclidean distance (px) between manual edge points.

Points closer than this threshold are rejected to prevent near-duplicate
entries that destabilize the Taubin circle fitter."""

# ------------------------------------------------------------------ #
#  Export defaults
# ------------------------------------------------------------------ #

DEFAULT_FPS: float = 1_000_000.0
"""Default frames-per-second for high-speed camera recordings."""

DEFAULT_UM2PX: float = 3.2
"""Default micrometres-per-pixel scale factor."""

DEFAULT_RMAX_FIT_LENGTH: int = 11
"""Default window length for quadratic Rmax fitting (must be odd)."""

# ------------------------------------------------------------------ #
#  State defaults
# ------------------------------------------------------------------ #

DEFAULT_REMOVING_FACTOR: int = 90
"""Default removing-factor slider position (0-100)."""

# ------------------------------------------------------------------ #
#  UI debounce / throttle
# ------------------------------------------------------------------ #

DISPLAY_DEBOUNCE_MS: int = 50
"""Debounce interval (ms) for the frame-display timer."""

PREVIEW_DEBOUNCE_MS: int = 50
"""Debounce interval (ms) for the detection-preview timer."""

AUTO_DISPLAY_THROTTLE_MS: int = 150
"""Minimum interval (ms) between display refreshes during automatic fitting."""
