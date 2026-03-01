"""Tests for image I/O utilities."""

import os
import tempfile

import cv2
import numpy as np
import pytest

from bubbletrack.model.image_io import (
    detect_bit_depth,
    load_and_normalize,
    scan_folder,
)


@pytest.fixture()
def img_folder(tmp_path):
    """Create a temp folder with a few synthetic 8-bit PNG images."""
    for i in range(3):
        img = np.full((100, 120), 128, dtype=np.uint8)
        cv2.imwrite(str(tmp_path / f"frame_{i:03d}.png"), img)
    return str(tmp_path)


@pytest.fixture()
def img_16bit(tmp_path):
    """Create a single 16-bit TIFF."""
    img = np.full((64, 64), 30000, dtype=np.uint16)
    path = str(tmp_path / "img16.tiff")
    cv2.imwrite(path, img)
    return path


class TestScanFolder:
    def test_finds_png(self, img_folder):
        paths = scan_folder(img_folder)
        assert len(paths) == 3
        assert all(p.endswith(".png") for p in paths)

    def test_natural_sort(self, tmp_path):
        for name in ["img_2.png", "img_10.png", "img_1.png"]:
            cv2.imwrite(str(tmp_path / name), np.zeros((10, 10), np.uint8))
        paths = scan_folder(str(tmp_path))
        basenames = [os.path.basename(p) for p in paths]
        assert basenames == ["img_1.png", "img_2.png", "img_10.png"]

    def test_empty_folder(self, tmp_path):
        assert scan_folder(str(tmp_path)) == []

    def test_tiff_priority(self, tmp_path):
        cv2.imwrite(str(tmp_path / "a.png"), np.zeros((10, 10), np.uint8))
        cv2.imwrite(str(tmp_path / "b.tiff"), np.zeros((10, 10), np.uint8))
        paths = scan_folder(str(tmp_path))
        assert all(p.endswith(".tiff") for p in paths)


class TestDetectBitDepth:
    def test_8bit(self, img_folder):
        paths = scan_folder(img_folder)
        assert detect_bit_depth(paths[0]) == 255

    def test_16bit(self, img_16bit):
        assert detect_bit_depth(img_16bit) == 65535


class TestLoadAndNormalize:
    def test_output_shapes(self, img_folder):
        paths = scan_folder(img_folder)
        full_img, full_bin, roi_img, roi_bin = load_and_normalize(
            paths[0], 0.5, (1, 50), (1, 60)
        )
        assert full_img.shape == (100, 120)
        assert full_bin.shape == (100, 120)
        assert roi_img.shape == (50, 60)
        assert roi_bin.shape == (50, 60)

    def test_normalised_range(self, img_folder):
        paths = scan_folder(img_folder)
        full_img, _, _, _ = load_and_normalize(paths[0], 0.5, (1, 100), (1, 120))
        # uniform image normalises to all-zero
        assert full_img.min() >= 0.0
        assert full_img.max() <= 1.0

    def test_binary_is_bool(self, img_folder):
        paths = scan_folder(img_folder)
        _, full_bin, _, roi_bin = load_and_normalize(paths[0], 0.5, (1, 100), (1, 120))
        assert full_bin.dtype == bool
        assert roi_bin.dtype == bool

    def test_sensitivity_affects_binary(self, tmp_path):
        # Gradient image so threshold matters
        grad = np.tile(np.arange(256, dtype=np.uint8), (100, 1))
        path = str(tmp_path / "grad.png")
        cv2.imwrite(path, grad)
        _, bin_low, _, _ = load_and_normalize(path, 0.3, (1, 100), (1, 256))
        _, bin_high, _, _ = load_and_normalize(path, 0.7, (1, 100), (1, 256))
        # Higher sensitivity => more white
        assert bin_high.sum() >= bin_low.sum()

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_and_normalize("/nonexistent.png", 0.5, (1, 10), (1, 10))

    def test_full_roi(self, img_folder):
        paths = scan_folder(img_folder)
        full, _, roi, _ = load_and_normalize(paths[0], 0.5, (1, 100), (1, 120))
        np.testing.assert_array_equal(full, roi)
