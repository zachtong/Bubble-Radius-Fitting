"""Path-independence guard for the binary preview panel.

Bug history (2026-04-06):
``display_frame()`` and ``PretuneController.preview_detection()`` are two
independent rendering entry points. They are wired to two different debounce
timers — threshold changes go through ``display_frame``, while removing-factor
changes go through ``preview_detection``. They were meant to render the same
visual for the same ``(state, frame)`` but had drifted apart in two ways:

1. ``display_frame``'s "unfitted frame" branch returned ``~binary_roi`` (raw
   inverted mask) and **skipped detect_bubble entirely** — so the Removing
   Factor had no visible effect.
2. ``preview_detection`` hard-coded the legacy ``removing_obj_radius`` argument
   to ``0`` "for preview speed" instead of reading ``state.removing_obj_radius``.

The combined effect was *path-dependent rendering*: dragging the threshold
slider away from ``a`` and back produced a different binary than dragging the
RF slider away from ``b`` and back, even though both ended at the same
``(threshold=a, remove=b)`` state.

These tests pin down the contract: *for a given (state, frame), both render
paths must produce the same binary image*.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from bubbletrack.controller.display_mixin import display_frame
from bubbletrack.controller.pretune_controller import PretuneController
from bubbletrack.event_bus import EventBus
from bubbletrack.model.state import AppState, update_state
from bubbletrack.ui.image_compare import CompareMode


@pytest.fixture()
def disk_image_path(tmp_path):
    """Write a synthetic dark-disk-on-bright image to a temp file.

    Canonical polarity (bubble interior dark) so the default pipeline can
    process it without ``invert_mask``.
    """
    size = 120
    img = np.full((size, size), 220, dtype=np.uint8)  # bright background
    rr, cc = np.indices((size, size))
    dist2 = (rr - size // 2) ** 2 + (cc - size // 2) ** 2
    img[dist2 <= 30 ** 2] = 30  # dark disk = bubble interior
    path = tmp_path / "frame.png"
    cv2.imwrite(str(path), img)
    return str(path), size


def _make_state(image_path: str, size: int, *, removing_obj_radius: int) -> AppState:
    """Build a minimal but realistic AppState pointing at *image_path*."""
    state = AppState.create_empty()
    state = update_state(
        state,
        images=(image_path,),
        image_no=0,
        img_thr=0.5,
        gridx=(1, size),
        gridy=(1, size),
        removing_factor=50,
        removing_obj_radius=removing_obj_radius,
        bubble_cross_edges=(False, False, False, False),
    )
    # Allocate result arrays so radius[0] = -1 (unfitted) — this is the
    # branch in display_frame that historically skipped detect_bubble.
    return state.with_results_initialized(1)


def _capture_display_frame_binary(state: AppState) -> np.ndarray:
    """Call display_frame with a mock window and return the binary panel image."""
    window = MagicMock()
    window.compare_mode = CompareMode.SIDE_BY_SIDE
    captured: dict = {}
    window.binary_panel.set_image = lambda img: captured.setdefault("img", img)
    display_frame(state, window, 0, lambda _s: None, cache=None)
    assert "img" in captured, "display_frame did not call binary_panel.set_image"
    return captured["img"]


def _capture_preview_detection_binary(state: AppState) -> np.ndarray:
    """Call PretuneController.preview_detection and return the binary panel image."""
    window = MagicMock()
    window.compare_mode = CompareMode.SIDE_BY_SIDE
    captured: dict = {}
    window.binary_panel.set_image = lambda img: captured.setdefault("img", img)

    holder = {"state": state}
    ctrl = PretuneController(
        bus=EventBus(),
        get_state=lambda: holder["state"],
        set_state=lambda s: holder.update(state=s),
        window=window,
        display_timer=MagicMock(),
        preview_timer=MagicMock(),
        get_max_radius=lambda: float("inf"),
        cache=None,
    )
    ctrl.preview_detection()
    assert "img" in captured, "preview_detection did not call binary_panel.set_image"
    return captured["img"]


class TestDisplayBinaryPathIndependence:
    """The binary panel must be a pure function of (state, frame).

    These tests catch the family of bugs where rendering depends on which
    debounce timer fired last.
    """

    def test_unfitted_frame_with_default_obj_radius(self, disk_image_path):
        """Default state: both render paths must agree on an unfitted frame."""
        path, size = disk_image_path
        state = _make_state(path, size, removing_obj_radius=0)

        bin_display = _capture_display_frame_binary(state)
        bin_preview = _capture_preview_detection_binary(state)

        np.testing.assert_array_equal(bin_display, bin_preview, err_msg=(
            "display_frame and preview_detection produced different binary "
            "images for the same state. The historical cause is that "
            "display_frame's unfitted-frame branch returned ~binary_roi "
            "without running detect_bubble, while preview_detection always "
            "ran detect_bubble. Both paths must apply the Removing Factor."
        ))

    def test_unfitted_frame_with_nonzero_obj_radius(self, disk_image_path):
        """Non-zero removing_obj_radius: catches the second drift.

        ``preview_detection`` historically hardcoded ``removing_obj_radius=0``,
        which only diverged from ``display_frame`` when the user enabled the
        legacy morphological closing slider. With this test we lock both paths
        to read from ``state.removing_obj_radius``.
        """
        path, size = disk_image_path
        state = _make_state(path, size, removing_obj_radius=2)

        bin_display = _capture_display_frame_binary(state)
        bin_preview = _capture_preview_detection_binary(state)

        np.testing.assert_array_equal(bin_display, bin_preview, err_msg=(
            "When state.removing_obj_radius != 0, preview_detection must "
            "honor it instead of hardcoding 0 — otherwise threshold-driven "
            "and RF-driven redraws diverge."
        ))
