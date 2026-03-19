"""Tests for parameter auto-optimization."""

import math

import numpy as np
import pytest

from bubbletrack.model.auto_optimize import optimize_parameters


def _make_process_fn(true_thr: float, true_rf: int, base_radius: float = 50.0):
    """Return a mock process_fn that returns best radius near *true_thr*/*true_rf*.

    The fitted radius degrades quadratically as parameters move away from the
    optimal values, simulating how real detection quality depends on parameters.
    """

    def process_fn(thr: float, rf: int, idx: int) -> float:
        thr_err = abs(thr - true_thr)
        rf_err = abs(rf - true_rf) / 100.0
        noise = thr_err * 30 + rf_err * 20
        return base_radius + noise

    return process_fn


class TestOptimizeParameters:
    def test_finds_best_parameters(self):
        """Optimizer should find parameters closest to the true optimum."""
        process_fn = _make_process_fn(true_thr=0.5, true_rf=50, base_radius=42.0)
        reference = {0: 42.0, 5: 42.0, 10: 42.0}

        result = optimize_parameters(
            process_fn,
            reference,
            thr_range=(0.1, 0.9, 9),
            rf_range=(10, 100, 10),
        )

        assert result["img_thr"] == pytest.approx(0.5, abs=0.15)
        assert result["removing_factor"] == 50
        assert result["error"] < 1.0

    def test_single_reference_frame(self):
        """Should work with just one reference frame."""
        process_fn = _make_process_fn(true_thr=0.3, true_rf=30, base_radius=100.0)
        reference = {0: 100.0}

        result = optimize_parameters(
            process_fn,
            reference,
            thr_range=(0.1, 0.9, 5),
            rf_range=(10, 50, 10),
        )

        assert "img_thr" in result
        assert "removing_factor" in result
        assert "error" in result
        assert result["error"] < 100.0

    def test_empty_reference_raises(self):
        """Empty reference dict should raise ValueError."""
        with pytest.raises(ValueError, match="No reference frames"):
            optimize_parameters(lambda t, r, i: 10.0, {})

    def test_all_nan_results_still_returns(self):
        """When process_fn always returns NaN, should still return a result."""

        def nan_fn(thr, rf, idx):
            return float("nan")

        reference = {0: 50.0, 1: 50.0}
        result = optimize_parameters(
            nan_fn,
            reference,
            thr_range=(0.1, 0.5, 3),
            rf_range=(10, 30, 10),
        )

        # All combos get the same penalty, so any valid result is fine
        assert math.isfinite(result["error"])
        assert result["error"] == 1000.0  # penalty per frame

    def test_negative_radius_penalized(self):
        """Negative radius values should be penalized like NaN."""

        def neg_fn(thr, rf, idx):
            return -5.0

        reference = {0: 50.0}
        result = optimize_parameters(
            neg_fn,
            reference,
            thr_range=(0.5, 0.5, 1),
            rf_range=(50, 50, 1),
        )

        assert result["error"] == 1000.0

    def test_custom_ranges(self):
        """Custom search ranges should be respected."""

        calls = []

        def tracking_fn(thr, rf, idx):
            calls.append((round(thr, 6), rf, idx))
            return 50.0

        reference = {0: 50.0}
        optimize_parameters(
            tracking_fn,
            reference,
            thr_range=(0.2, 0.4, 3),
            rf_range=(20, 40, 10),
        )

        thrs_seen = sorted(set(c[0] for c in calls))
        rfs_seen = sorted(set(c[1] for c in calls))

        assert len(thrs_seen) == 3  # linspace(0.2, 0.4, 3)
        assert rfs_seen == [20, 30, 40]

    def test_result_types(self):
        """Result values should be plain Python types, not numpy scalars."""
        process_fn = _make_process_fn(true_thr=0.5, true_rf=50)
        reference = {0: 50.0}

        result = optimize_parameters(
            process_fn,
            reference,
            thr_range=(0.3, 0.7, 3),
            rf_range=(40, 60, 10),
        )

        assert isinstance(result["img_thr"], float)
        assert isinstance(result["removing_factor"], int)
        assert isinstance(result["error"], float)
