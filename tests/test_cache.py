"""Tests for the LRU image cache."""

import numpy as np

from bubbletrack.model.cache import ImageCache


class TestImageCache:
    """Unit tests for ImageCache."""

    def test_put_and_get(self):
        c = ImageCache()
        arr = np.zeros((100, 100), dtype=np.uint8)
        c.put("key1", (arr,))
        assert c.get("key1") is not None

    def test_miss_returns_none(self):
        c = ImageCache()
        assert c.get("missing") is None

    def test_lru_eviction(self):
        # Room for ~1 image of 10000 bytes
        c = ImageCache(max_bytes=100 * 100 + 50)
        a1 = np.zeros((100, 100), dtype=np.uint8)  # 10000 bytes
        a2 = np.zeros((100, 100), dtype=np.uint8)
        c.put("k1", (a1,))
        c.put("k2", (a2,))
        assert c.get("k1") is None  # evicted
        assert c.get("k2") is not None

    def test_invalidate_clears_all(self):
        c = ImageCache()
        c.put("k", (np.zeros(10),))
        c.invalidate()
        assert c.count == 0
        assert c.total_bytes == 0

    def test_access_refreshes_lru(self):
        # Room for 2 images of 10000 bytes each
        c = ImageCache(max_bytes=200 * 100 + 50)
        a = np.zeros((100, 100), dtype=np.uint8)
        c.put("k1", (a.copy(),))
        c.put("k2", (a.copy(),))
        c.get("k1")  # refresh k1
        c.put("k3", (a.copy(),))  # should evict k2, not k1
        assert c.get("k1") is not None
        assert c.get("k2") is None

    def test_count_and_total_bytes(self):
        c = ImageCache()
        arr = np.zeros((50, 50), dtype=np.uint8)  # 2500 bytes
        c.put("a", (arr.copy(),))
        c.put("b", (arr.copy(),))
        assert c.count == 2
        assert c.total_bytes == 5000

    def test_put_replaces_existing_key(self):
        c = ImageCache()
        small = np.zeros((10,), dtype=np.uint8)  # 10 bytes
        big = np.zeros((100,), dtype=np.uint8)    # 100 bytes
        c.put("k", (small,))
        assert c.total_bytes == 10
        c.put("k", (big,))
        assert c.total_bytes == 100
        assert c.count == 1

    def test_multiple_arrays_in_value(self):
        c = ImageCache()
        a = np.zeros((10, 10), dtype=np.uint8)   # 100 bytes
        b = np.ones((20, 20), dtype=np.float64)   # 3200 bytes
        c.put("k", (a, b))
        assert c.total_bytes == 100 + 3200
        result = c.get("k")
        assert result is not None
        assert len(result) == 2

    def test_mixed_value_types_only_counts_ndarrays(self):
        c = ImageCache()
        arr = np.zeros((10,), dtype=np.uint8)  # 10 bytes
        c.put("k", (arr, "not_an_array", 42))
        assert c.total_bytes == 10

    def test_empty_cache_properties(self):
        c = ImageCache()
        assert c.count == 0
        assert c.total_bytes == 0
        assert c.get("anything") is None
