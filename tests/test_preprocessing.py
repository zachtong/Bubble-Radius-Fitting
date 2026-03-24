"""Tests for image preprocessing (background subtraction and denoising)."""

import numpy as np
import pytest

from bubbletrack.model.image_io import denoise_nlm, subtract_background


def _make_gradient_image(h: int = 200, w: int = 200) -> np.ndarray:
    """Create a uint8 image with a smooth horizontal gradient."""
    row = np.linspace(50, 200, w, dtype=np.float64)
    return np.tile(row, (h, 1)).astype(np.uint8)


def _make_noisy_image(
    h: int = 100, w: int = 100, seed: int = 42
) -> np.ndarray:
    """Create a uint8 image with Gaussian noise added to a flat background."""
    rng = np.random.default_rng(seed)
    base = np.full((h, w), 128, dtype=np.float64)
    noise = rng.normal(0, 30, (h, w))
    return np.clip(base + noise, 0, 255).astype(np.uint8)


class TestSubtractBackground:
    def test_removes_gradient(self):
        """Background subtraction should flatten a smooth gradient."""
        img = _make_gradient_image()
        result = subtract_background(img, method="gaussian", kernel_size=51)

        # After removing the gradient, the image should be much more uniform
        original_std = float(np.std(img.astype(np.float64)))
        result_std = float(np.std(result.astype(np.float64)))
        assert result_std < original_std

    def test_median_method(self):
        """Median background subtraction should work without error."""
        img = _make_gradient_image()
        result = subtract_background(img, method="median", kernel_size=51)
        assert result.shape == img.shape
        assert result.dtype == img.dtype

    def test_gaussian_method(self):
        """Gaussian background subtraction should work without error."""
        img = _make_gradient_image()
        result = subtract_background(img, method="gaussian", kernel_size=51)
        assert result.shape == img.shape
        assert result.dtype == img.dtype

    def test_unknown_method_raises(self):
        """Unknown method should raise ValueError."""
        img = np.zeros((10, 10), dtype=np.uint8)
        with pytest.raises(ValueError, match="Unknown background method"):
            subtract_background(img, method="magic")

    def test_even_kernel_size_corrected(self):
        """Even kernel_size should be bumped to odd automatically."""
        img = _make_gradient_image(50, 50)
        # Should not raise; 50 gets bumped to 51
        result = subtract_background(img, method="median", kernel_size=50)
        assert result.shape == img.shape

    def test_preserves_dtype_uint8(self):
        """Output dtype should match input dtype (uint8)."""
        img = np.full((50, 50), 128, dtype=np.uint8)
        result = subtract_background(img, method="gaussian", kernel_size=11)
        assert result.dtype == np.uint8

    def test_preserves_dtype_uint16(self):
        """Output dtype should match input dtype (uint16)."""
        img = np.full((50, 50), 30000, dtype=np.uint16)
        result = subtract_background(img, method="gaussian", kernel_size=11)
        assert result.dtype == np.uint16

    def test_no_negative_overflow(self):
        """cv2.subtract should clamp at 0 (no wraparound)."""
        img = np.full((50, 50), 10, dtype=np.uint8)
        result = subtract_background(img, method="gaussian", kernel_size=11)
        # Uniform image: bg ~ image, so result should be near 0
        assert result.max() <= 10

    def test_preserves_local_features(self):
        """A bright spot on a dark background should be preserved."""
        img = np.full((100, 100), 20, dtype=np.uint8)
        # Add a bright 10x10 spot
        img[45:55, 45:55] = 200
        result = subtract_background(img, method="gaussian", kernel_size=51)
        # The spot region should still be the brightest area
        spot_mean = float(result[45:55, 45:55].mean())
        bg_mean = float(result[0:10, 0:10].mean())
        assert spot_mean > bg_mean


class TestDenoiseNlm:
    def test_reduces_noise(self):
        """NLM denoising should reduce the standard deviation of a noisy image."""
        # Use a larger image so NLM has enough context for neighbourhood matching
        noisy = _make_noisy_image(h=200, w=200)
        denoised = denoise_nlm(noisy, h=20.0)

        noisy_std = float(np.std(noisy.astype(np.float64)))
        denoised_std = float(np.std(denoised.astype(np.float64)))
        assert denoised_std < noisy_std

    def test_preserves_shape(self):
        """Output shape should match input."""
        img = _make_noisy_image(80, 120)
        result = denoise_nlm(img, h=10.0)
        assert result.shape == (80, 120)

    def test_preserves_dtype(self):
        """Output should be uint8."""
        img = _make_noisy_image()
        result = denoise_nlm(img, h=10.0)
        assert result.dtype == np.uint8

    def test_stronger_filter_smoother(self):
        """Higher h should produce a smoother (lower std) result."""
        noisy = _make_noisy_image()
        mild = denoise_nlm(noisy, h=5.0)
        strong = denoise_nlm(noisy, h=30.0)

        mild_std = float(np.std(mild.astype(np.float64)))
        strong_std = float(np.std(strong.astype(np.float64)))
        assert strong_std <= mild_std

    def test_uniform_image_unchanged(self):
        """A uniform image should pass through nearly unchanged."""
        img = np.full((50, 50), 128, dtype=np.uint8)
        result = denoise_nlm(img, h=10.0)
        np.testing.assert_array_equal(result, img)
