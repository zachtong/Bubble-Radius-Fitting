"""Tests for batch experiment processing."""

from pathlib import Path

import pytest

from bubbletrack.model.batch_experiments import (
    batch_process_experiments,
    find_experiment_folders,
)


class TestFindExperimentFolders:
    def test_finds_folders_with_images(self, tmp_path):
        """Should find subfolders that contain image files."""
        exp1 = tmp_path / "exp_001"
        exp1.mkdir()
        (exp1 / "frame_000.tiff").write_bytes(b"fake")
        (exp1 / "frame_001.tiff").write_bytes(b"fake")

        exp2 = tmp_path / "exp_002"
        exp2.mkdir()
        (exp2 / "img.png").write_bytes(b"fake")

        result = find_experiment_folders(str(tmp_path))
        names = [f.name for f in result]
        assert names == ["exp_001", "exp_002"]

    def test_skips_empty_folders(self, tmp_path):
        """Folders with no image files should be excluded."""
        empty = tmp_path / "empty"
        empty.mkdir()

        has_txt = tmp_path / "text_only"
        has_txt.mkdir()
        (has_txt / "notes.txt").write_text("not an image")

        result = find_experiment_folders(str(tmp_path))
        assert result == []

    def test_skips_hidden_folders(self, tmp_path):
        """Dotfiles / hidden directories should be skipped."""
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "frame.png").write_bytes(b"fake")

        result = find_experiment_folders(str(tmp_path))
        assert result == []

    def test_nonexistent_root(self):
        """Non-existent root directory should return empty list."""
        result = find_experiment_folders("/this/does/not/exist")
        assert result == []

    def test_sorted_order(self, tmp_path):
        """Results should be sorted by folder name."""
        for name in ["c_exp", "a_exp", "b_exp"]:
            d = tmp_path / name
            d.mkdir()
            (d / "img.jpg").write_bytes(b"fake")

        result = find_experiment_folders(str(tmp_path))
        names = [f.name for f in result]
        assert names == ["a_exp", "b_exp", "c_exp"]

    def test_only_immediate_children(self, tmp_path):
        """Nested subfolders should not be discovered."""
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "frame.png").write_bytes(b"fake")

        nested = parent / "nested"
        nested.mkdir()
        (nested / "frame.png").write_bytes(b"fake")

        result = find_experiment_folders(str(tmp_path))
        names = [f.name for f in result]
        assert names == ["parent"]

    def test_all_image_extensions(self, tmp_path):
        """All supported image extensions should be recognized."""
        for ext in [".tiff", ".tif", ".png", ".jpg", ".jpeg", ".bmp"]:
            d = tmp_path / f"folder_{ext.lstrip('.')}"
            d.mkdir()
            (d / f"img{ext}").write_bytes(b"fake")

        result = find_experiment_folders(str(tmp_path))
        assert len(result) == 6


class TestBatchProcessExperiments:
    def test_processes_all_folders(self, tmp_path):
        """Should call process_fn for every folder and collect results."""
        folders = [tmp_path / "a", tmp_path / "b"]
        for f in folders:
            f.mkdir()

        def mock_process(path: Path) -> dict:
            return {"success": True, "n_frames": 10, "output": str(path)}

        results = batch_process_experiments(folders, mock_process)
        assert len(results) == 2
        assert results["a"]["success"] is True
        assert results["b"]["n_frames"] == 10

    def test_handles_exception(self, tmp_path):
        """If process_fn raises, the error should be captured in results."""
        folder = tmp_path / "bad"
        folder.mkdir()

        def failing_process(path: Path) -> dict:
            raise RuntimeError("disk full")

        results = batch_process_experiments([folder], failing_process)
        assert results["bad"]["success"] is False
        assert "disk full" in results["bad"]["error"]

    def test_callback_invoked(self, tmp_path):
        """Progress callback should be called after each folder."""
        folders = [tmp_path / f"exp_{i}" for i in range(3)]
        for f in folders:
            f.mkdir()

        progress: list[tuple[int, int]] = []

        def mock_process(path: Path) -> dict:
            return {"success": True, "n_frames": 1, "output": "ok"}

        batch_process_experiments(
            folders, mock_process, callback=lambda c, t: progress.append((c, t))
        )

        assert progress == [(1, 3), (2, 3), (3, 3)]

    def test_empty_folders_list(self):
        """Processing an empty folder list should return empty results."""
        results = batch_process_experiments([], lambda p: {"success": True})
        assert results == {}

    def test_mixed_success_failure(self, tmp_path):
        """Should handle a mix of successful and failed processing."""
        folders = [tmp_path / "good", tmp_path / "bad", tmp_path / "also_good"]
        for f in folders:
            f.mkdir()

        def mixed_process(path: Path) -> dict:
            if path.name == "bad":
                raise ValueError("corrupted data")
            return {"success": True, "n_frames": 5, "output": str(path)}

        results = batch_process_experiments(folders, mixed_process)
        assert results["good"]["success"] is True
        assert results["bad"]["success"] is False
        assert results["also_good"]["success"] is True

    def test_no_callback(self, tmp_path):
        """Should work fine without a callback."""
        folder = tmp_path / "exp"
        folder.mkdir()

        results = batch_process_experiments(
            [folder],
            lambda p: {"success": True, "n_frames": 1, "output": "ok"},
            callback=None,
        )
        assert results["exp"]["success"] is True
