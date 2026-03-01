"""Tests for the removing-factor log-scale mapping."""

from bubbletrack.model.removing_factor import compute_removing_factor


class TestComputeRemovingFactor:
    def test_slider_zero_returns_min_area(self):
        assert compute_removing_factor(0, (1, 501), (1, 501)) == 10

    def test_slider_100_returns_max_area(self):
        gridx = (1, 501)  # 500 rows
        gridy = (1, 501)  # 500 cols
        roi_area = 500 * 500
        expected_max = round(roi_area * 0.5)
        result = compute_removing_factor(100, gridx, gridy)
        assert result == expected_max

    def test_monotonically_increasing(self):
        gridx, gridy = (1, 401), (1, 301)
        values = [compute_removing_factor(s, gridx, gridy) for s in range(0, 101)]
        for a, b in zip(values, values[1:]):
            assert b >= a

    def test_small_roi(self):
        # ROI 20x20 => area=400, max_area=200
        rf = compute_removing_factor(50, (1, 21), (1, 21))
        assert 10 < rf < 200

    def test_negative_slider_clamped(self):
        assert compute_removing_factor(-5, (1, 101), (1, 101)) == 10

    def test_midpoint_is_geometric_mean(self):
        gridx, gridy = (1, 501), (1, 501)
        roi_area = 500 * 500
        min_a = 10
        max_a = round(roi_area * 0.5)
        mid = compute_removing_factor(50, gridx, gridy)
        geometric_mean = round(min_a * (max_a / min_a) ** 0.5)
        assert mid == geometric_mean
