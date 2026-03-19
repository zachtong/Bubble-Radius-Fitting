"""LRU image cache with memory limit."""

from __future__ import annotations

from collections import OrderedDict

import numpy as np


class ImageCache:
    """LRU cache for loaded and normalized images.

    Stores (img_norm, binary, roi, binary_roi) tuples.
    Evicts oldest entries when memory limit is reached.
    """

    def __init__(self, max_bytes: int = 200 * 1024 * 1024) -> None:
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._sizes: dict[str, int] = {}
        self._total = 0
        self._max = max_bytes

    def get(self, key: str) -> tuple | None:
        """Retrieve a cached value, promoting it to most-recently-used."""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: tuple) -> None:
        """Insert or update a cache entry, evicting LRU items if over budget."""
        # Remove existing entry if present
        if key in self._cache:
            self._total -= self._sizes.pop(key)
            del self._cache[key]

        size = sum(v.nbytes for v in value if isinstance(v, np.ndarray))

        # Evict oldest until there's room
        while self._total + size > self._max and self._cache:
            old_key, _ = self._cache.popitem(last=False)
            self._total -= self._sizes.pop(old_key)

        self._cache[key] = value
        self._sizes[key] = size
        self._total += size

    def invalidate(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._sizes.clear()
        self._total = 0

    @property
    def total_bytes(self) -> int:
        """Total memory used by cached numpy arrays in bytes."""
        return self._total

    @property
    def count(self) -> int:
        """Number of entries currently in the cache."""
        return len(self._cache)
