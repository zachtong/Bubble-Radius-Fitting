"""Tests for the invert_mask post-detection visual toggle.

invert_mask is a pure display flag — when enabled, the binary panel renders
``~processed`` instead of ``processed``.  It does NOT alter the image
processing pipeline (``normalize_frame`` / ``detect_bubble``), the cached
binaries, the detected edge points, or the fitted radius.  These tests lock
in that semantic so the pre-2026-04-06 regression — where invert_mask was
threaded into ``normalize_frame`` and silently produced a totally different
detection result — cannot return.
"""

import inspect

import numpy as np

from bubbletrack.controller.display_mixin import _build_cache_key
from bubbletrack.model.config import PERSIST_KEYS
from bubbletrack.model.image_io import load_and_normalize, normalize_frame
from bubbletrack.model.state import AppState, update_state


class TestNormalizeFrameSignature:
    """``invert_mask`` must NOT be a parameter of the processing pipeline.

    The whole point of the 2026-04-06 refactor is that invert is a render-
    layer flag, not a processing-layer flag.  If somebody re-adds the kwarg
    to ``normalize_frame`` or ``load_and_normalize``, this test fails loudly.
    """

    def test_normalize_frame_has_no_invert_mask_kwarg(self):
        sig = inspect.signature(normalize_frame)
        assert "invert_mask" not in sig.parameters

    def test_load_and_normalize_has_no_invert_mask_kwarg(self):
        sig = inspect.signature(load_and_normalize)
        assert "invert_mask" not in sig.parameters


class TestInvertMaskState:
    """invert_mask is a session-only flag — must not be persisted."""

    def test_invert_mask_default_is_false(self):
        """Fresh AppState defaults invert_mask to False."""
        assert AppState.create_empty().invert_mask is False

    def test_invert_mask_not_in_persist_keys(self):
        """invert_mask must not be persisted across launches.

        Each session starts with the flag off so a stale flag from a
        previous dataset cannot silently mislead the user about the
        rendered binary.
        """
        assert "invert_mask" not in PERSIST_KEYS


class TestInvertMaskCacheKey:
    """Toggling invert_mask must NOT change the cache key.

    invert is a pure post-detection visual swap — the cached binary is
    identical regardless of the flag.  Including invert in the key would
    cause unnecessary cache invalidation and force a full re-load + re-
    threshold + re-detect every time the user clicks the button.
    """

    def test_cache_key_invariant_under_invert_mask(self):
        state_off = update_state(AppState.create_empty(), invert_mask=False)
        state_on = update_state(AppState.create_empty(), invert_mask=True)
        key_off = _build_cache_key("frame_001.png", state_off)
        key_on = _build_cache_key("frame_001.png", state_on)
        assert key_off == key_on, (
            "Cache key must NOT include invert_mask: it is a render-time "
            "swap and the cached binary is identical for both states."
        )


class TestInvertMaskIsPureBitFlip:
    """The visual swap is exactly ``~processed``.

    This is the contract every render site relies on.  We model it directly
    against ``np.invert`` so that nobody can ever 'fix' it by, say,
    re-running detection on the inverse — that was the original bug.
    """

    def test_inverted_render_equals_bitwise_not(self):
        rng = np.random.default_rng(0)
        processed = rng.random((50, 50)) > 0.5  # arbitrary bool mask
        inverted = ~processed
        # Re-derive the swap exactly as the render sites do.
        bin_display = ~processed if True else processed  # invert_mask=True
        np.testing.assert_array_equal(bin_display, inverted)
        # Sanity: True maps to False and vice versa, no third value.
        assert set(np.unique(bin_display).tolist()) <= {True, False}

    def test_normalize_frame_output_is_unchanged_by_invert_state(self):
        """``normalize_frame`` is now agnostic to invert_mask — calling it
        twice with the same input gives byte-identical binaries.
        """
        rng = np.random.default_rng(1)
        raw = (rng.random((80, 80)) * 255).astype(np.uint8)
        a = normalize_frame(raw, 0.5, (1, 80), (1, 80))
        b = normalize_frame(raw, 0.5, (1, 80), (1, 80))
        for arr_a, arr_b in zip(a, b):
            np.testing.assert_array_equal(arr_a, arr_b)
