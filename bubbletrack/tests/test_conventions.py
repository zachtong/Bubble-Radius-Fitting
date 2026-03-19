"""Tests for model/conventions.py — index convention helpers."""

from bubbletrack.model.conventions import (
    display_to_frame,
    frame_to_display,
    roi_to_slice,
)


class TestRoiToSlice:
    def test_basic_full_image(self):
        """(1, 100), (1, 200) maps to slice(0, 100), slice(0, 200)."""
        rs, cs = roi_to_slice((1, 100), (1, 200))
        assert rs == slice(0, 100)
        assert cs == slice(0, 200)

    def test_offset_region(self):
        """(50, 150), (30, 120) maps to slice(49, 150), slice(29, 120)."""
        rs, cs = roi_to_slice((50, 150), (30, 120))
        assert rs == slice(49, 150)
        assert cs == slice(29, 120)

    def test_single_pixel_roi(self):
        """(5, 5), (10, 10) maps to slice(4, 5), slice(9, 10) — one pixel."""
        rs, cs = roi_to_slice((5, 5), (10, 10))
        assert rs == slice(4, 5)
        assert cs == slice(9, 10)


class TestFrameDisplay:
    def test_frame_to_display_is_1_based(self):
        assert frame_to_display(0) == 1
        assert frame_to_display(99) == 100

    def test_display_to_frame_is_0_based(self):
        assert display_to_frame(1) == 0
        assert display_to_frame(100) == 99

    def test_roundtrip(self):
        """display_to_frame(frame_to_display(i)) == i for all i."""
        for i in range(10):
            assert display_to_frame(frame_to_display(i)) == i

    def test_reverse_roundtrip(self):
        """frame_to_display(display_to_frame(d)) == d for all d >= 1."""
        for d in range(1, 11):
            assert frame_to_display(display_to_frame(d)) == d
