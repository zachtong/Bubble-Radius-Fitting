"""Tests for anomaly detection on bubble radius time series."""

import numpy as np
import pytest

from bubbletrack.model.anomaly import detect_anomalies


class TestNanAnomalies:
    """Type 1: NaN / non-positive radius detection."""

    def test_nan_values_flagged(self):
        radii = np.array([10.0, np.nan, 10.0, 10.0, 10.0, 10.0, 10.0])
        flags = detect_anomalies(radii)
        assert flags[1] is np.True_
        assert not flags[0]

    def test_zero_radius_flagged(self):
        radii = np.array([10.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0])
        flags = detect_anomalies(radii)
        assert flags[1]

    def test_negative_radius_flagged(self):
        radii = np.array([10.0, -5.0, 10.0, 10.0, 10.0, 10.0, 10.0])
        flags = detect_anomalies(radii)
        assert flags[1]

    def test_nan_detection_disabled(self):
        radii = np.array([10.0, np.nan, 10.0, 10.0, 10.0, 10.0, 10.0])
        flags = detect_anomalies(radii, nan_is_anomaly=False)
        # NaN is not valid, so it can't be flagged by z-score or jump either
        assert not flags[1]

    def test_all_nan(self):
        radii = np.full(5, np.nan)
        flags = detect_anomalies(radii)
        assert flags.all()

    def test_all_zeros(self):
        radii = np.zeros(5)
        flags = detect_anomalies(radii)
        assert flags.all()


class TestZScoreOutliers:
    """Type 2: MAD-based z-score outlier detection."""

    def test_single_outlier_detected(self):
        # 20 stable points + 1 extreme outlier
        radii = np.full(21, 100.0)
        radii[10] = 500.0  # far outlier
        flags = detect_anomalies(radii)
        assert flags[10]

    def test_no_outlier_in_uniform_data(self):
        radii = np.full(20, 50.0)
        flags = detect_anomalies(radii)
        assert not flags.any()

    def test_custom_threshold(self):
        rng = np.random.default_rng(42)
        radii = 100 + rng.normal(0, 2, 50)
        # Inject a moderate outlier
        radii[25] = 115.0
        # With a low threshold, should flag it
        flags_low = detect_anomalies(radii, zscore_threshold=2.0)
        # With a high threshold, might not
        flags_high = detect_anomalies(radii, zscore_threshold=10.0)
        assert flags_low[25]
        assert not flags_high[25]

    def test_outlier_at_boundary(self):
        """Outlier at index 0 and last index are detected."""
        rng = np.random.default_rng(7)
        radii = 100.0 + rng.normal(0, 2, 30)
        radii[0] = 300.0
        radii[-1] = 300.0
        flags = detect_anomalies(radii)
        assert flags[0]
        assert flags[-1]

    def test_mad_zero_skips_zscore(self):
        """If all valid values are identical, MAD is 0 — no z-score flags."""
        radii = np.full(10, 42.0)
        flags = detect_anomalies(radii)
        assert not flags.any()


class TestJumpDetection:
    """Type 3: Frame-to-frame jump anomalies."""

    def test_large_jump_flagged(self):
        radii = np.array([100.0, 100.0, 100.0, 100.0, 100.0,
                          160.0, 100.0, 100.0, 100.0, 100.0])
        # jump_threshold_pct=50 means jumps > 50 px flagged (median=100)
        flags = detect_anomalies(radii, zscore_threshold=100.0)
        # Frame 5 (0-indexed) has a +60 jump from frame 4
        assert flags[5]
        # Frame 6 has a -60 jump from frame 5
        assert flags[6]

    def test_small_jump_not_flagged(self):
        radii = np.array([100.0, 102.0, 98.0, 101.0, 99.0,
                          100.0, 103.0, 97.0, 100.0, 101.0])
        flags = detect_anomalies(radii)
        assert not flags.any()

    def test_custom_jump_threshold(self):
        radii = np.array([100.0, 100.0, 100.0, 100.0, 100.0,
                          130.0, 100.0, 100.0, 100.0, 100.0])
        # 30% jump should be flagged with 25% threshold
        flags_strict = detect_anomalies(
            radii, jump_threshold_pct=25.0, zscore_threshold=100.0,
        )
        assert flags_strict[5]

        # But not with 50% threshold
        flags_loose = detect_anomalies(
            radii, jump_threshold_pct=50.0, zscore_threshold=100.0,
        )
        assert not flags_loose[5]

    def test_jump_across_nan_not_flagged(self):
        """Jump detection skips invalid frames — no false positives."""
        radii = np.array([100.0, 100.0, np.nan, 160.0, 100.0,
                          100.0, 100.0, 100.0, 100.0, 100.0])
        flags = detect_anomalies(radii, zscore_threshold=100.0)
        # Frame 3 (160) follows NaN — jump check should NOT fire
        # because the pair (NaN, 160) has an invalid predecessor
        assert not flags[3]


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_array(self):
        flags = detect_anomalies(np.array([]))
        assert len(flags) == 0

    def test_single_element(self):
        flags = detect_anomalies(np.array([100.0]))
        assert len(flags) == 1
        assert not flags[0]

    def test_fewer_than_5_valid(self):
        """With fewer than 5 valid points, only NaN detection runs."""
        radii = np.array([10.0, np.nan, np.nan, np.nan, 10.0])
        flags = detect_anomalies(radii)
        # NaN slots flagged, valid slots not (no z-score / jump with < 5)
        assert not flags[0]
        assert flags[1]
        assert flags[2]
        assert flags[3]
        assert not flags[4]

    def test_exactly_5_valid(self):
        """With exactly 5 valid points, all detectors run."""
        radii = np.array([10.0, 10.0, 10.0, 10.0, 100.0])
        flags = detect_anomalies(radii, zscore_threshold=2.0)
        assert flags[-1]  # 100 is a clear outlier among 10s

    def test_return_type_and_shape(self):
        radii = np.array([10.0, 20.0, 10.0, 10.0, 10.0, 10.0])
        flags = detect_anomalies(radii)
        assert isinstance(flags, np.ndarray)
        assert flags.dtype == bool
        assert flags.shape == radii.shape

    def test_list_input_converted(self):
        """Plain list input is converted to ndarray internally."""
        radii = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 500.0]
        flags = detect_anomalies(radii)
        assert isinstance(flags, np.ndarray)
        assert flags[-1]  # 500 is outlier

    def test_all_valid_no_anomalies(self):
        rng = np.random.default_rng(123)
        radii = 100 + rng.normal(0, 1, 100)
        flags = detect_anomalies(radii)
        # Very unlikely any point hits z > 3 with std=1
        assert flags.sum() <= 2  # allow up to 2 noise hits


class TestCombined:
    """Multiple anomaly types in a single series."""

    def test_mixed_anomalies(self):
        rng = np.random.default_rng(0)
        radii = 100 + rng.normal(0, 1, 30)
        radii[5] = np.nan       # Type 1: fit failure
        radii[15] = 300.0       # Type 2: z-score outlier
        radii[25] = 200.0       # Type 3: jump (100 -> 200)
        flags = detect_anomalies(radii)
        assert flags[5]   # NaN
        assert flags[15]  # outlier
        # Frame 25 and 26 are jump destinations
        assert flags[25]

    def test_vectorized_jump_matches_loop(self):
        """Verify vectorized jump detection matches naive loop."""
        rng = np.random.default_rng(99)
        radii = 50 + rng.normal(0, 2, 200)
        # Inject some jumps
        radii[50] = 150.0
        radii[100] = 10.0
        radii[150] = 200.0

        flags = detect_anomalies(radii, nan_is_anomaly=False, zscore_threshold=100.0)

        # Naive loop reference
        valid = np.isfinite(radii) & (radii > 0)
        median_r = np.median(radii[valid])
        jump_limit = median_r * 50.0 / 100.0
        expected = np.zeros(len(radii), dtype=bool)
        for i in range(1, len(radii)):
            if valid[i] and valid[i - 1]:
                if abs(radii[i] - radii[i - 1]) > jump_limit:
                    expected[i] = True

        np.testing.assert_array_equal(flags, expected)
