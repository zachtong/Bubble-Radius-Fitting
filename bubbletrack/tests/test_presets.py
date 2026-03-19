"""Tests for parameter preset management (model/presets.py)."""

from __future__ import annotations

import json

import pytest

from bubbletrack.model.presets import (
    delete_preset,
    list_presets,
    load_preset,
    save_preset,
)


@pytest.fixture(autouse=True)
def _isolate_presets(tmp_path, monkeypatch):
    """Redirect PRESETS_DIR to a temp directory for every test."""
    presets_dir = tmp_path / ".bubbletrack" / "presets"
    monkeypatch.setattr("bubbletrack.model.presets.PRESETS_DIR", presets_dir)


class TestSavePreset:
    """Verify save_preset creates the expected file."""

    def test_creates_directory_and_file(self, tmp_path):
        path = save_preset("test1", {"img_thr": 0.5})
        assert path.exists()
        assert path.name == "test1.json"

    def test_writes_valid_json(self, tmp_path):
        params = {"img_thr": 0.7, "fps": 500_000.0}
        path = save_preset("params_a", params)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded == params

    def test_converts_tuples_to_lists(self, tmp_path):
        params = {"bubble_cross_edges": (True, False, True, False)}
        path = save_preset("edges", params)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["bubble_cross_edges"] == [True, False, True, False]

    def test_overwrites_existing_preset(self, tmp_path):
        save_preset("dup", {"img_thr": 0.3})
        save_preset("dup", {"img_thr": 0.9})
        loaded = load_preset("dup")
        assert loaded["img_thr"] == 0.9

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="empty"):
            save_preset("", {"img_thr": 0.5})

    def test_rejects_name_with_slash(self):
        with pytest.raises(ValueError, match="path separators"):
            save_preset("bad/name", {"img_thr": 0.5})

    def test_rejects_name_with_backslash(self):
        with pytest.raises(ValueError, match="path separators"):
            save_preset("bad\\name", {"img_thr": 0.5})


class TestLoadPreset:
    """Verify load_preset reads the correct file."""

    def test_load_existing_preset(self, tmp_path):
        save_preset("p1", {"fps": 1_000_000.0})
        result = load_preset("p1")
        assert result["fps"] == 1_000_000.0

    def test_raises_on_missing_preset(self):
        with pytest.raises(FileNotFoundError):
            load_preset("nonexistent")

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="empty"):
            load_preset("")


class TestListPresets:
    """Verify list_presets returns sorted names."""

    def test_empty_when_no_presets(self):
        assert list_presets() == []

    def test_lists_multiple_presets_sorted(self, tmp_path):
        save_preset("charlie", {"x": 1})
        save_preset("alpha", {"x": 2})
        save_preset("bravo", {"x": 3})
        names = list_presets()
        assert names == ["alpha", "bravo", "charlie"]

    def test_ignores_non_json_files(self, tmp_path):
        presets_dir = tmp_path / ".bubbletrack" / "presets"
        presets_dir.mkdir(parents=True, exist_ok=True)
        (presets_dir / "notes.txt").write_text("not a preset", encoding="utf-8")
        save_preset("valid", {"x": 1})
        assert list_presets() == ["valid"]


class TestDeletePreset:
    """Verify delete_preset removes files correctly."""

    def test_deletes_existing_preset(self, tmp_path):
        save_preset("doomed", {"x": 1})
        assert "doomed" in list_presets()
        delete_preset("doomed")
        assert "doomed" not in list_presets()

    def test_noop_for_missing_preset(self):
        # Should not raise
        delete_preset("nonexistent")

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="empty"):
            delete_preset("")


class TestPresetRoundTrip:
    """End-to-end test: save → list → load → delete cycle."""

    def test_full_cycle(self, tmp_path):
        params = {
            "img_thr": 0.65,
            "removing_factor": 75,
            "bubble_cross_edges": [True, False, False, True],
            "gaussian_sigma": 1.2,
            "clahe_clip": 3.0,
            "closing_radius": 5,
            "opening_radius": 2,
            "um2px": 3.5,
            "fps": 750_000.0,
            "rmax_fit_length": 13,
        }
        save_preset("full_test", params)
        assert "full_test" in list_presets()

        loaded = load_preset("full_test")
        assert loaded == params

        delete_preset("full_test")
        assert "full_test" not in list_presets()
