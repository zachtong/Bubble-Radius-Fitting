"""Tests for the image comparison compositing helpers."""

import numpy as np
import pytest

from bubbletrack.ui.image_compare import (
    CompareMode,
    create_overlay,
    create_wipe,
    _to_uint8,
)


# ---------------------------------------------------------------------------
# _to_uint8
# ---------------------------------------------------------------------------

class TestToUint8:
    def test_bool_input(self):
        img = np.array([[True, False], [False, True]])
        result = _to_uint8(img)
        assert result.dtype == np.uint8
        assert result[0, 0] == 255
        assert result[0, 1] == 0

    def test_float64_input(self):
        img = np.array([[0.0, 0.5], [1.0, 0.25]], dtype=np.float64)
        result = _to_uint8(img)
        assert result.dtype == np.uint8
        assert result[0, 0] == 0
        assert result[0, 1] == 127  # int(0.5 * 255)
        assert result[1, 0] == 255

    def test_float32_input(self):
        img = np.ones((4, 4), dtype=np.float32) * 0.8
        result = _to_uint8(img)
        assert result.dtype == np.uint8
        assert result[0, 0] == 204  # int(0.8 * 255)

    def test_all_zero_float(self):
        img = np.zeros((3, 3), dtype=np.float64)
        result = _to_uint8(img)
        assert result.dtype == np.uint8
        assert np.all(result == 0)

    def test_uint8_passthrough(self):
        img = np.array([[10, 20], [30, 40]], dtype=np.uint8)
        result = _to_uint8(img)
        assert result.dtype == np.uint8
        np.testing.assert_array_equal(result, img)


# ---------------------------------------------------------------------------
# create_overlay
# ---------------------------------------------------------------------------

class TestCreateOverlay:
    def test_output_shape(self):
        orig = np.random.rand(100, 200).astype(np.float64)
        binary = np.zeros((100, 200), dtype=bool)
        result = create_overlay(orig, binary)
        assert result.shape == (100, 200, 3)
        assert result.dtype == np.uint8

    def test_no_mask_unchanged(self):
        """With an all-False mask, overlay = pure grayscale RGB."""
        orig = np.full((10, 10), 128, dtype=np.uint8)
        binary = np.zeros((10, 10), dtype=bool)
        result = create_overlay(orig, binary)
        # All channels equal (grayscale)
        np.testing.assert_array_equal(result[:, :, 0], result[:, :, 1])
        np.testing.assert_array_equal(result[:, :, 0], result[:, :, 2])

    def test_mask_tints_green(self):
        """Where mask is True, the green channel should be boosted."""
        orig = np.full((10, 10), 50, dtype=np.uint8)
        binary = np.ones((10, 10), dtype=bool)
        result = create_overlay(orig, binary, alpha=0.5)
        # Green channel should be higher than red/blue
        assert result[0, 0, 1] > result[0, 0, 0]
        assert result[0, 0, 1] > result[0, 0, 2]

    def test_green_boost_is_clamped(self):
        """Green channel should not exceed 255."""
        orig = np.full((5, 5), 250, dtype=np.uint8)
        binary = np.ones((5, 5), dtype=bool)
        result = create_overlay(orig, binary, alpha=1.0)
        assert result[0, 0, 1] == 255

    def test_alpha_zero_no_tint(self):
        """With alpha=0, overlay should equal pure grayscale."""
        orig = np.full((8, 8), 100, dtype=np.uint8)
        binary = np.ones((8, 8), dtype=bool)
        result = create_overlay(orig, binary, alpha=0.0)
        np.testing.assert_array_equal(result[:, :, 0], result[:, :, 1])

    def test_float_original(self):
        orig = np.random.rand(20, 30).astype(np.float32)
        binary = np.random.randint(0, 2, (20, 30)).astype(bool)
        result = create_overlay(orig, binary)
        assert result.shape == (20, 30, 3)
        assert result.dtype == np.uint8


# ---------------------------------------------------------------------------
# create_wipe
# ---------------------------------------------------------------------------

class TestCreateWipe:
    def test_output_shape(self):
        orig = np.random.rand(100, 200).astype(np.float64)
        binary = np.zeros((100, 200), dtype=bool)
        result = create_wipe(orig, binary)
        assert result.shape == (100, 200, 3)
        assert result.dtype == np.uint8

    def test_left_is_original(self):
        """Left half should be the grayscale original."""
        orig = np.full((10, 20), 128, dtype=np.uint8)
        binary = np.ones((10, 20), dtype=bool)
        result = create_wipe(orig, binary, split_fraction=0.5)
        # First few columns (away from the red line) should be grayscale 128
        np.testing.assert_array_equal(result[:, 0, :], [[128, 128, 128]] * 10)

    def test_right_is_binary(self):
        """Right half should be the binary image as white-on-black."""
        orig = np.full((10, 20), 128, dtype=np.uint8)
        binary = np.ones((10, 20), dtype=bool)
        result = create_wipe(orig, binary, split_fraction=0.5)
        # Last column should be white (binary=True -> 255)
        np.testing.assert_array_equal(result[:, -1, :], [[255, 255, 255]] * 10)

    def test_red_divider_line(self):
        """There should be a red divider at the split position."""
        orig = np.full((10, 100), 128, dtype=np.uint8)
        binary = np.zeros((10, 100), dtype=bool)
        result = create_wipe(orig, binary, split_fraction=0.5)
        split_x = 50
        # Check that at least one column near split is red
        line_pixels = result[:, split_x - 1:split_x + 1, :]
        # Red channel should be 255
        assert np.all(line_pixels[:, :, 0] == 255)
        # Green and blue should be 0
        assert np.all(line_pixels[:, :, 1] == 0)
        assert np.all(line_pixels[:, :, 2] == 0)

    def test_split_fraction_zero(self):
        """split_fraction=0 means entire image is binary."""
        orig = np.full((10, 20), 128, dtype=np.uint8)
        binary = np.ones((10, 20), dtype=bool)
        result = create_wipe(orig, binary, split_fraction=0.0)
        # Last column should be white (binary=True -> 255)
        assert np.all(result[:, -1, 0] == 255)

    def test_split_fraction_one(self):
        """split_fraction=1 means entire image is original."""
        orig = np.full((10, 20), 100, dtype=np.uint8)
        binary = np.ones((10, 20), dtype=bool)
        result = create_wipe(orig, binary, split_fraction=1.0)
        # All columns should be grayscale 100 (except the red line at the edge)
        assert result[0, 0, 0] == 100

    def test_bool_binary(self):
        orig = np.full((10, 20), 60, dtype=np.uint8)
        binary = np.zeros((10, 20), dtype=bool)
        binary[:, 15:] = True
        result = create_wipe(orig, binary, split_fraction=0.5)
        assert result.shape == (10, 20, 3)


# ---------------------------------------------------------------------------
# CompareMode enum
# ---------------------------------------------------------------------------

class TestCompareMode:
    def test_values(self):
        assert CompareMode.SIDE_BY_SIDE.value == "side_by_side"
        assert CompareMode.OVERLAY.value == "overlay"
        assert CompareMode.WIPE.value == "wipe"

    def test_from_value(self):
        assert CompareMode("side_by_side") is CompareMode.SIDE_BY_SIDE
        assert CompareMode("overlay") is CompareMode.OVERLAY
        assert CompareMode("wipe") is CompareMode.WIPE

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            CompareMode("invalid")
