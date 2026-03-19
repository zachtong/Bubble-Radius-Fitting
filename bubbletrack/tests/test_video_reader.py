"""Tests for video input support (VideoFrameReader, is_video_file, normalize_frame)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from bubbletrack.model.image_io import (
    ImageLoadError,
    VideoFrameReader,
    is_video_file,
    normalize_frame,
)


# ------------------------------------------------------------------ #
#  is_video_file
# ------------------------------------------------------------------ #


class TestIsVideoFile:
    def test_avi(self):
        assert is_video_file("movie.avi") is True

    def test_mp4(self):
        assert is_video_file("/path/to/clip.MP4") is True

    def test_mov(self):
        assert is_video_file("C:\\videos\\test.mov") is True

    def test_mkv(self):
        assert is_video_file("sample.MKV") is True

    def test_png_not_video(self):
        assert is_video_file("image.png") is False

    def test_tiff_not_video(self):
        assert is_video_file("data.tiff") is False

    def test_empty_string(self):
        assert is_video_file("") is False

    def test_no_extension(self):
        assert is_video_file("README") is False


# ------------------------------------------------------------------ #
#  VideoFrameReader (mocked cv2.VideoCapture)
# ------------------------------------------------------------------ #


def _make_mock_cap(total=10, fps=30.0, opened=True, read_ok=True):
    """Create a mock cv2.VideoCapture with configurable behaviour."""
    cap = MagicMock()
    cap.isOpened.return_value = opened

    def get_prop(prop_id):
        if prop_id == cv2.CAP_PROP_FRAME_COUNT:
            return float(total)
        if prop_id == cv2.CAP_PROP_FPS:
            return fps
        return 0.0

    cap.get.side_effect = get_prop

    # read() returns a 3-channel BGR frame
    frame = np.full((64, 80, 3), 128, dtype=np.uint8)
    cap.read.return_value = (read_ok, frame if read_ok else None)
    cap.set.return_value = True
    cap.release.return_value = None
    return cap


class TestVideoFrameReader:
    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_init_success(self, mock_vc_cls):
        mock_vc_cls.return_value = _make_mock_cap(total=100, fps=60.0)
        reader = VideoFrameReader("test.mp4")
        assert reader.total_frames == 100
        assert reader.fps == 60.0
        reader.close()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_init_failure_raises(self, mock_vc_cls):
        mock_vc_cls.return_value = _make_mock_cap(opened=False)
        with pytest.raises(ImageLoadError, match="Cannot open video"):
            VideoFrameReader("bad.avi")

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_read_frame_returns_grayscale(self, mock_vc_cls):
        cap = _make_mock_cap(total=5)
        mock_vc_cls.return_value = cap
        reader = VideoFrameReader("clip.mp4")
        frame = reader.read_frame(2)
        # Should be grayscale (2D)
        assert frame.ndim == 2
        assert frame.shape == (64, 80)
        # Should have called set with the correct frame index
        cap.set.assert_called_with(cv2.CAP_PROP_POS_FRAMES, 2)
        reader.close()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_read_frame_already_grayscale(self, mock_vc_cls):
        """If VideoCapture returns a 2D frame, it should pass through."""
        cap = _make_mock_cap(total=3)
        gray_frame = np.full((64, 80), 200, dtype=np.uint8)
        cap.read.return_value = (True, gray_frame)
        mock_vc_cls.return_value = cap
        reader = VideoFrameReader("gray.mp4")
        frame = reader.read_frame(0)
        assert frame.ndim == 2
        np.testing.assert_array_equal(frame, gray_frame)
        reader.close()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_read_frame_out_of_range(self, mock_vc_cls):
        mock_vc_cls.return_value = _make_mock_cap(total=5)
        reader = VideoFrameReader("clip.mp4")
        with pytest.raises(ImageLoadError, match="out of range"):
            reader.read_frame(5)
        with pytest.raises(ImageLoadError, match="out of range"):
            reader.read_frame(-1)
        reader.close()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_read_frame_decode_failure(self, mock_vc_cls):
        cap = _make_mock_cap(total=5, read_ok=False)
        mock_vc_cls.return_value = cap
        reader = VideoFrameReader("bad_frames.mp4")
        with pytest.raises(ImageLoadError, match="Cannot read frame"):
            reader.read_frame(2)
        reader.close()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_close_releases_capture(self, mock_vc_cls):
        cap = _make_mock_cap()
        mock_vc_cls.return_value = cap
        reader = VideoFrameReader("clip.mp4")
        reader.close()
        cap.release.assert_called_once()
        # Double close should be safe
        reader.close()
        # release only called once since _cap is set to None after first close
        cap.release.assert_called_once()

    @patch("bubbletrack.model.image_io.cv2.VideoCapture")
    def test_del_calls_close(self, mock_vc_cls):
        cap = _make_mock_cap()
        mock_vc_cls.return_value = cap
        reader = VideoFrameReader("clip.mp4")
        del reader
        cap.release.assert_called_once()


# ------------------------------------------------------------------ #
#  normalize_frame (extracted from load_and_normalize)
# ------------------------------------------------------------------ #


class TestNormalizeFrame:
    def test_output_shapes(self):
        raw = np.full((100, 120), 128, dtype=np.uint8)
        cur_img, cur_bin, roi_img, roi_bin = normalize_frame(
            raw, 0.5, (1, 50), (1, 60),
        )
        assert cur_img.shape == (100, 120)
        assert cur_bin.shape == (100, 120)
        assert roi_img.shape == (50, 60)
        assert roi_bin.shape == (50, 60)

    def test_normalised_range(self):
        raw = np.full((80, 80), 100, dtype=np.uint8)
        cur_img, _, _, _ = normalize_frame(raw, 0.5, (1, 80), (1, 80))
        assert cur_img.min() >= 0.0
        assert cur_img.max() <= 1.0

    def test_binary_is_bool(self):
        raw = np.full((40, 40), 50, dtype=np.uint8)
        _, cur_bin, _, roi_bin = normalize_frame(raw, 0.5, (1, 40), (1, 40))
        assert cur_bin.dtype == bool
        assert roi_bin.dtype == bool

    def test_bgr_input_converted(self):
        """3-channel input should be converted to greyscale automatically."""
        bgr = np.full((50, 50, 3), 128, dtype=np.uint8)
        cur_img, _, _, _ = normalize_frame(bgr, 0.5, (1, 50), (1, 50))
        assert cur_img.ndim == 2
        assert cur_img.shape == (50, 50)

    def test_16bit_input(self):
        raw = np.full((32, 32), 30000, dtype=np.uint16)
        cur_img, _, _, _ = normalize_frame(raw, 0.5, (1, 32), (1, 32))
        assert cur_img.shape == (32, 32)
        assert cur_img.min() >= 0.0
        assert cur_img.max() <= 1.0

    def test_gaussian_sigma(self):
        """Gaussian blur reduces edge count."""
        rng = np.random.default_rng(42)
        noisy = rng.integers(0, 256, (100, 100), dtype=np.uint8)
        _, bin_no, _, _ = normalize_frame(noisy, 0.5, (1, 100), (1, 100))
        _, bin_blur, _, _ = normalize_frame(
            noisy, 0.5, (1, 100), (1, 100), gaussian_sigma=5.0,
        )
        edges_no = np.sum(np.abs(np.diff(bin_no.astype(int), axis=1)))
        edges_blur = np.sum(np.abs(np.diff(bin_blur.astype(int), axis=1)))
        assert edges_blur < edges_no

    def test_clahe_preserves_shape(self):
        raw = np.full((60, 60), 128, dtype=np.uint8)
        r1, _, _, _ = normalize_frame(raw, 0.5, (1, 60), (1, 60))
        r2, _, _, _ = normalize_frame(raw, 0.5, (1, 60), (1, 60), clahe_clip=2.0)
        assert r1.shape == r2.shape
