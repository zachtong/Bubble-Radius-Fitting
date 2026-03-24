# BubbleTrack v3.0 Comprehensive Upgrade Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade BubbleTrack from v2.0 to v3.0 with 38 improvements across architecture, UX, performance, robustness, features, and distribution.

**Architecture:** Refactor the monolithic AppController (613 lines) into domain-specific sub-controllers communicating via an event bus. Introduce immutable state management, LRU caching, multiprocess batch processing, and pyqtgraph for real-time charting. Add session persistence (.brt), CLI mode, anomaly detection, and result editing.

**Tech Stack:** Python 3.10+ / PyQt6 / NumPy / OpenCV / scikit-image / scipy / pyqtgraph / concurrent.futures

---

## Phase Overview

| Phase | Name | Tasks | Dependencies | Focus |
|-------|------|-------|-------------|-------|
| 1 | Foundation & Architecture | 6 | None | Constants, logging, immutable state, event bus, controller split |
| 2 | Robustness & Safety | 8 | Phase 1 | Error handling, validation, thread safety, security |
| 3 | UX & Interaction | 6 | Phase 1 | Shortcuts, undo, ETA, image compare, chart interaction |
| 4 | Performance | 4 | Phase 1 | Caching, pyqtgraph, multiprocess batch |
| 5 | Persistence & Features | 10 | Phases 1-2 | Config, presets, sessions, anomaly detection, video, auto-optimize |
| 6 | Distribution & Polish | 8 | Phases 1-5 | CLI, export formats, EXE slimming, onboarding, PDF reports |

---

## Phase 1: Foundation & Architecture

> **Goal:** Establish the architectural foundation that all subsequent phases depend on.
> **Estimated tasks:** 6 | **Parallel-safe within phase:** Tasks 1.1-1.3 can run in parallel; 1.4-1.6 are sequential.

---

### Task 1.1: Extract Magic Numbers to Constants Module

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/constants.py`
- Modify: `bubbletrack/src/bubbletrack/model/detection.py`
- Modify: `bubbletrack/src/bubbletrack/model/removing_factor.py`
- Modify: `bubbletrack/src/bubbletrack/model/export.py`
- Modify: `bubbletrack/src/bubbletrack/model/state.py`
- Test: `bubbletrack/tests/test_constants.py`

**Step 1: Create constants module with all magic numbers**

```python
# bubbletrack/src/bubbletrack/model/constants.py
"""Centralized constants for the BubbleTrack detection pipeline."""

# --- Detection pipeline (detection.py) ---
MAX_AXIS_RATIO = 2.2        # max major_axis / image_short_side
MAX_ECCENTRICITY = 1.6      # max major_axis / minor_axis
MIN_HOLE_AREA = 40           # min area (px) for imfill hole removal

# --- Removing factor (removing_factor.py) ---
RF_MIN_AREA = 10             # minimum removable area (px)
RF_MAX_AREA_FRACTION = 0.5   # max area = this fraction * ROI area

# --- Circle fitting (circle_fit.py) ---
TAUBIN_EPSILON = 1e-12       # Newton iteration convergence threshold
TAUBIN_MAX_ITER = 20         # Newton iteration max steps
TAUBIN_MIN_POINTS = 3        # minimum boundary points for fitting

# --- Export (export.py) ---
DEFAULT_FPS = 1_000_000.0    # default frame rate (Hz)
DEFAULT_UM2PX = 3.2          # default scale (um/px)
DEFAULT_RMAX_FIT_LENGTH = 11 # default Rmax quadratic fit window

# --- State defaults ---
DEFAULT_REMOVING_FACTOR = 90  # slider default [0, 100]

# --- UI debounce ---
DISPLAY_DEBOUNCE_MS = 50     # slider debounce delay
PREVIEW_DEBOUNCE_MS = 50     # detection preview debounce
AUTO_DISPLAY_THROTTLE_MS = 150  # batch mode UI update throttle
```

**Step 2: Write test to verify constants are importable and have correct types**

```python
# bubbletrack/tests/test_constants.py
from bubbletrack.model.constants import (
    MAX_AXIS_RATIO, MAX_ECCENTRICITY, MIN_HOLE_AREA,
    RF_MIN_AREA, RF_MAX_AREA_FRACTION,
    TAUBIN_EPSILON, TAUBIN_MAX_ITER, TAUBIN_MIN_POINTS,
    DEFAULT_FPS, DEFAULT_UM2PX, DEFAULT_RMAX_FIT_LENGTH,
)

class TestConstants:
    def test_detection_constants_are_positive(self):
        assert MAX_AXIS_RATIO > 0
        assert MAX_ECCENTRICITY > 0
        assert MIN_HOLE_AREA > 0

    def test_removing_factor_bounds(self):
        assert RF_MIN_AREA > 0
        assert 0 < RF_MAX_AREA_FRACTION <= 1.0

    def test_taubin_constants(self):
        assert TAUBIN_EPSILON > 0
        assert TAUBIN_MAX_ITER > 0
        assert TAUBIN_MIN_POINTS >= 3

    def test_export_defaults(self):
        assert DEFAULT_FPS > 0
        assert DEFAULT_UM2PX > 0
        assert DEFAULT_RMAX_FIT_LENGTH >= 3
```

**Step 3: Run test to verify it passes**

Run: `cd bubbletrack && python -m pytest tests/test_constants.py -v`
Expected: PASS

**Step 4: Replace magic numbers in detection.py, removing_factor.py, circle_fit.py, export.py, state.py**

In each file, replace hardcoded values with imports from `model.constants`. Example for detection.py:

```python
# detection.py - replace hardcoded values
from bubbletrack.model.constants import MAX_AXIS_RATIO, MAX_ECCENTRICITY, MIN_HOLE_AREA
```

**Step 5: Run full test suite to verify no regressions**

Run: `cd bubbletrack && python -m pytest tests/ -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add bubbletrack/src/bubbletrack/model/constants.py bubbletrack/tests/test_constants.py
git add bubbletrack/src/bubbletrack/model/detection.py bubbletrack/src/bubbletrack/model/removing_factor.py
git add bubbletrack/src/bubbletrack/model/circle_fit.py bubbletrack/src/bubbletrack/model/export.py
git add bubbletrack/src/bubbletrack/model/state.py
git commit -m "refactor: extract magic numbers to model/constants.py"
```

---

### Task 1.2: Add Logging System

**Files:**
- Create: `bubbletrack/src/bubbletrack/logging_config.py`
- Modify: `bubbletrack/src/bubbletrack/app.py` (init logging at startup)
- Modify: `bubbletrack/src/bubbletrack/controller/controller.py` (add log calls)
- Modify: `bubbletrack/src/bubbletrack/controller/worker.py` (add log calls)
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py` (add log calls)
- Test: `bubbletrack/tests/test_logging_config.py`

**Step 1: Create logging configuration module**

```python
# bubbletrack/src/bubbletrack/logging_config.py
"""Logging configuration for BubbleTrack."""

import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(*, level: int = logging.INFO, log_dir: Path | None = None) -> None:
    """Configure root logger with console + optional file handler."""
    root = logging.getLogger("bubbletrack")
    root.setLevel(level)

    # Console handler (always)
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root.addHandler(console)

    # File handler (optional)
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / "bubbletrack.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root.addHandler(fh)
```

**Step 2: Write test**

```python
# bubbletrack/tests/test_logging_config.py
import logging
from bubbletrack.logging_config import setup_logging

class TestLoggingConfig:
    def test_setup_creates_logger(self):
        setup_logging()
        logger = logging.getLogger("bubbletrack")
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

    def test_file_handler_created(self, tmp_path):
        setup_logging(log_dir=tmp_path)
        logger = logging.getLogger("bubbletrack")
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1
        # cleanup
        for h in logger.handlers[:]:
            logger.removeHandler(h)
```

**Step 3: Run test**

Run: `cd bubbletrack && python -m pytest tests/test_logging_config.py -v`
Expected: PASS

**Step 4: Add `setup_logging()` call in `app.py:main()` and sprinkle `logger.info/warning/error` in controller.py, worker.py, image_io.py**

Key log points:
- `controller.py`: folder loaded (info), fit result (info), export success/fail (info/error)
- `worker.py`: batch start/stop/error (info/warning/error)
- `image_io.py`: file load failure (error), bit depth detection (debug)

**Step 5: Run full test suite**

Run: `cd bubbletrack && python -m pytest tests/ -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add bubbletrack/src/bubbletrack/logging_config.py bubbletrack/tests/test_logging_config.py
git add bubbletrack/src/bubbletrack/app.py bubbletrack/src/bubbletrack/controller/controller.py
git add bubbletrack/src/bubbletrack/controller/worker.py bubbletrack/src/bubbletrack/model/image_io.py
git commit -m "feat: add structured logging system with file output"
```

---

### Task 1.3: Unify Frame Index Convention

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/state.py` (add docstring)
- Modify: `bubbletrack/src/bubbletrack/model/detection.py` (add comments)
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py` (add comments)
- Create: `bubbletrack/src/bubbletrack/model/conventions.py` (index conversion helpers)
- Test: `bubbletrack/tests/test_conventions.py`

**Step 1: Create conventions module with conversion helpers**

```python
# bubbletrack/src/bubbletrack/model/conventions.py
"""Index convention helpers.

Convention summary:
- Frame indices: 0-based internally, 1-based in UI display
- ROI bounds (gridx, gridy): 1-based inclusive (MATLAB convention)
  - gridx = (row_min, row_max), gridy = (col_min, col_max)
  - To slice NumPy arrays: img[gridx[0]-1 : gridx[1], gridy[0]-1 : gridy[1]]
- Edge coordinates from detection: 1-based (row, col) in full image space
- Circle fit input/output: same coordinate space as edge coordinates
"""

def roi_to_slice(gridx: tuple[int, int], gridy: tuple[int, int]) -> tuple[slice, slice]:
    """Convert 1-based inclusive ROI bounds to NumPy slices.

    Parameters
    ----------
    gridx : (row_min, row_max), 1-based inclusive
    gridy : (col_min, col_max), 1-based inclusive

    Returns
    -------
    (row_slice, col_slice) for direct NumPy indexing
    """
    return slice(gridx[0] - 1, gridx[1]), slice(gridy[0] - 1, gridy[1])


def frame_to_display(idx: int) -> int:
    """Convert 0-based frame index to 1-based display number."""
    return idx + 1


def display_to_frame(display_num: int) -> int:
    """Convert 1-based display number to 0-based frame index."""
    return display_num - 1
```

**Step 2: Write tests**

```python
# bubbletrack/tests/test_conventions.py
from bubbletrack.model.conventions import roi_to_slice, frame_to_display, display_to_frame

class TestConventions:
    def test_roi_to_slice_basic(self):
        rs, cs = roi_to_slice((1, 100), (1, 200))
        assert rs == slice(0, 100)
        assert cs == slice(0, 200)

    def test_roi_to_slice_offset(self):
        rs, cs = roi_to_slice((50, 150), (30, 120))
        assert rs == slice(49, 150)
        assert cs == slice(29, 120)

    def test_frame_display_roundtrip(self):
        for i in range(10):
            assert display_to_frame(frame_to_display(i)) == i

    def test_frame_to_display_is_1_based(self):
        assert frame_to_display(0) == 1
        assert frame_to_display(99) == 100
```

**Step 3: Run test, verify pass**

Run: `cd bubbletrack && python -m pytest tests/test_conventions.py -v`

**Step 4: Replace raw slice arithmetic in image_io.py and controller.py with `roi_to_slice()`**

Search for patterns like `gridx[0]-1` and replace with the helper.

**Step 5: Run full test suite, commit**

```bash
git add bubbletrack/src/bubbletrack/model/conventions.py bubbletrack/tests/test_conventions.py
git add -u
git commit -m "refactor: unify frame index conventions with helper module"
```

---

### Task 1.4: Refactor AppState to Immutable Pattern

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/state.py`
- Create: `bubbletrack/tests/test_state.py`

**Step 1: Write failing test for immutable update**

```python
# bubbletrack/tests/test_state.py
import numpy as np
from bubbletrack.model.state import AppState, update_state

class TestAppStateImmutability:
    def test_update_returns_new_instance(self):
        s1 = AppState.create_empty()
        s2 = update_state(s1, image_no=5)
        assert s1 is not s2
        assert s1.image_no != s2.image_no

    def test_update_preserves_other_fields(self):
        s1 = AppState.create_empty()
        s2 = update_state(s1, img_thr=0.5)
        assert s2.img_thr == 0.5
        assert s2.image_no == s1.image_no

    def test_create_empty_has_defaults(self):
        s = AppState.create_empty()
        assert s.images == []
        assert s.image_no == 0
        assert s.radius is None
```

**Step 2: Run test to verify it fails (update_state doesn't exist yet)**

Run: `cd bubbletrack && python -m pytest tests/test_state.py -v`
Expected: FAIL with ImportError

**Step 3: Implement immutable state with `dataclasses.replace`**

```python
# state.py additions
from dataclasses import dataclass, field, replace

@dataclass(frozen=True)  # Change from mutable to frozen
class AppState:
    # ... existing fields (mark mutable defaults with field(default_factory=...))
    images: tuple[str, ...] = ()          # Change list to tuple for true immutability
    folder_path: str = ""
    image_no: int = 0
    img_thr: float = 0.45
    gridx: tuple[int, int] = (1, 1)
    gridy: tuple[int, int] = (1, 1)
    removing_factor: int = 90
    bubble_cross_edges: tuple[bool, ...] = (False, False, False, False)
    # ... rest of fields ...

    # Results are NumPy arrays - can't be truly frozen, but we treat them as immutable
    # Use a wrapper or accept this limitation
    radius: object = None         # np.ndarray | None
    circle_fit_par: object = None # np.ndarray | None
    circle_xy: tuple = ()         # tuple of arrays

    @classmethod
    def create_empty(cls) -> "AppState":
        return cls()

    @property
    def total_frames(self) -> int:
        return len(self.images)


def update_state(state: AppState, **kwargs) -> AppState:
    """Create a new AppState with specified fields replaced.

    Returns a new instance; original is not modified.
    """
    return replace(state, **kwargs)
```

**Note:** NumPy arrays inside a frozen dataclass are a known limitation. The `frozen=True` prevents reassigning fields, but array contents can still be mutated. For result arrays (radius, circle_fit_par), we accept this pragmatic compromise and use `update_state()` for all field changes.

**Step 4: Update controller.py to use `update_state()` instead of direct mutation**

Replace all `self.state.field = value` with `self.state = update_state(self.state, field=value)`.

**Step 5: Run full test suite**

Run: `cd bubbletrack && python -m pytest tests/ -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add bubbletrack/src/bubbletrack/model/state.py bubbletrack/tests/test_state.py
git add bubbletrack/src/bubbletrack/controller/controller.py
git commit -m "refactor: make AppState frozen dataclass with update_state()"
```

---

### Task 1.5: Introduce Event Bus

**Files:**
- Create: `bubbletrack/src/bubbletrack/event_bus.py`
- Test: `bubbletrack/tests/test_event_bus.py`

**Step 1: Write failing test**

```python
# bubbletrack/tests/test_event_bus.py
from bubbletrack.event_bus import EventBus

class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        results = []
        bus.subscribe("frame_changed", lambda idx: results.append(idx))
        bus.emit("frame_changed", 5)
        assert results == [5]

    def test_multiple_subscribers(self):
        bus = EventBus()
        a, b = [], []
        bus.subscribe("fit_done", lambda r: a.append(r))
        bus.subscribe("fit_done", lambda r: b.append(r))
        bus.emit("fit_done", 3.14)
        assert a == [3.14] and b == [3.14]

    def test_unsubscribe(self):
        bus = EventBus()
        results = []
        token = bus.subscribe("x", lambda v: results.append(v))
        bus.emit("x", 1)
        bus.unsubscribe(token)
        bus.emit("x", 2)
        assert results == [1]

    def test_emit_unknown_event_is_noop(self):
        bus = EventBus()
        bus.emit("nonexistent", 42)  # should not raise
```

**Step 2: Implement EventBus**

```python
# bubbletrack/src/bubbletrack/event_bus.py
"""Simple event bus for decoupled communication between controllers and UI."""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

@dataclass
class _Subscription:
    event: str
    callback: Callable
    id: int

class EventBus:
    """Publish-subscribe event bus.

    Usage:
        bus = EventBus()
        token = bus.subscribe("frame_changed", handler)
        bus.emit("frame_changed", new_idx)
        bus.unsubscribe(token)
    """

    def __init__(self) -> None:
        self._subs: dict[str, list[_Subscription]] = {}
        self._next_id = 0

    def subscribe(self, event: str, callback: Callable) -> int:
        """Subscribe to an event. Returns a token for unsubscribing."""
        token = self._next_id
        self._next_id += 1
        sub = _Subscription(event=event, callback=callback, id=token)
        self._subs.setdefault(event, []).append(sub)
        return token

    def unsubscribe(self, token: int) -> None:
        """Remove a subscription by token."""
        for event, subs in self._subs.items():
            self._subs[event] = [s for s in subs if s.id != token]

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all subscribers."""
        for sub in self._subs.get(event, []):
            try:
                sub.callback(*args, **kwargs)
            except Exception:
                logger.exception("Error in event handler for %r", event)
```

**Step 3: Run test, verify pass**

Run: `cd bubbletrack && python -m pytest tests/test_event_bus.py -v`

**Step 4: Commit**

```bash
git add bubbletrack/src/bubbletrack/event_bus.py bubbletrack/tests/test_event_bus.py
git commit -m "feat: add EventBus for decoupled controller communication"
```

---

### Task 1.6: Split Controller into Domain Sub-Controllers

**Files:**
- Create: `bubbletrack/src/bubbletrack/controller/file_controller.py`
- Create: `bubbletrack/src/bubbletrack/controller/pretune_controller.py`
- Create: `bubbletrack/src/bubbletrack/controller/manual_controller.py`
- Create: `bubbletrack/src/bubbletrack/controller/auto_controller.py`
- Create: `bubbletrack/src/bubbletrack/controller/export_controller.py`
- Create: `bubbletrack/src/bubbletrack/controller/display_mixin.py`
- Modify: `bubbletrack/src/bubbletrack/controller/controller.py` (reduce to <100 lines, signal router)
- Modify: `bubbletrack/src/bubbletrack/app.py` (wire sub-controllers)

**Depends on:** Task 1.4 (immutable state), Task 1.5 (event bus)

**Step 1: Define sub-controller base and split plan**

```python
# Each sub-controller follows this pattern:
class BaseController:
    def __init__(self, bus: EventBus, get_state, set_state):
        self.bus = bus
        self._get_state = get_state   # callable returning current AppState
        self._set_state = set_state   # callable accepting new AppState

    @property
    def state(self) -> AppState:
        return self._get_state()

    @state.setter
    def state(self, new_state: AppState) -> None:
        self._set_state(new_state)
```

**Split mapping (from controller.py analysis):**

| Sub-controller | Methods to move | Lines |
|---------------|----------------|-------|
| `file_controller.py` | `_on_folder_selected`, `_on_frame_changed`, `_on_tab_frame_selected`, `_on_tab_changed` | ~80 |
| `pretune_controller.py` | `_on_threshold_changed`, `_on_removing_factor_changed`, `_on_filters_changed`, `_on_edges_changed`, `_on_select_roi`, `_on_roi_selected`, `_on_pretune_fit`, `_preview_detection` | ~150 |
| `manual_controller.py` | `_on_manual_select`, `_on_point_clicked`, `_on_manual_done`, `_on_manual_clear` | ~80 |
| `auto_controller.py` | `_on_auto_fit`, `_on_auto_progress`, `_on_auto_frame_done`, `_on_auto_finished`, `_on_auto_stop`, `_on_auto_clear` | ~120 |
| `export_controller.py` | `_on_export_r_data`, `_on_export_rof_t`, `_default_export_dir` | ~70 |
| `display_mixin.py` | `_display_frame`, `_refresh_chart`, `_redraw_original` | ~80 |

**Step 2: Implement each sub-controller, moving methods 1:1 from controller.py**

Each sub-controller communicates with UI via the EventBus rather than direct `self.w` references. The main `AppController.__init__` creates all sub-controllers and connects Qt signals to bus events.

**Step 3: Refactor main controller.py to <100 lines**

```python
# controller/controller.py (after refactor)
class AppController:
    """Thin orchestrator: owns state, creates sub-controllers, wires Qt signals to EventBus."""

    def __init__(self, window: MainWindow) -> None:
        self.w = window
        self.bus = EventBus()
        self._state = AppState.create_empty()

        # Create sub-controllers
        self.file_ctrl = FileController(self.bus, self._get_state, self._set_state)
        self.pretune_ctrl = PretuneController(self.bus, self._get_state, self._set_state)
        self.manual_ctrl = ManualController(self.bus, self._get_state, self._set_state)
        self.auto_ctrl = AutoController(self.bus, self._get_state, self._set_state)
        self.export_ctrl = ExportController(self.bus, self._get_state, self._set_state)

        self._connect_qt_signals()
        self._connect_bus_to_ui()

    def _get_state(self) -> AppState:
        return self._state

    def _set_state(self, new: AppState) -> None:
        self._state = new
```

**Step 4: Run full test suite (existing tests should still pass since model layer is unchanged)**

Run: `cd bubbletrack && python -m pytest tests/ -v`

**Step 5: Manual smoke test the GUI**

Run: `cd bubbletrack && python -m bubbletrack`
Verify: folder loading, frame switching, pretune fit, manual mode, auto fit, export all work.

**Step 6: Commit**

```bash
git add bubbletrack/src/bubbletrack/controller/
git add bubbletrack/src/bubbletrack/app.py
git commit -m "refactor: split monolithic controller into 5 domain sub-controllers + event bus"
```

---

## Phase 2: Robustness & Safety

> **Goal:** Harden error handling, input validation, thread safety, and security.
> **Depends on:** Phase 1 (controller split, logging)
> **Parallel-safe:** All tasks in this phase can run in parallel.

---

### Task 2.1: Image Loading Exception Handling

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py`
- Test: `bubbletrack/tests/test_image_io.py` (add test cases)

**Implementation:**

Wrap `cv2.imread()` in try-except. Return `None` or raise a custom `ImageLoadError` with friendly message. The controller should catch this and show a warning while continuing to next frame.

```python
# model/image_io.py
class ImageLoadError(Exception):
    """Raised when an image file cannot be loaded."""

def load_and_normalize(filepath, sensitivity, gridx, gridy, **kwargs):
    img = cv2.imread(str(filepath), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ImageLoadError(f"Cannot read image: {filepath}")
    # ... rest of function
```

**Tests to add:**
- `test_corrupted_file_raises_ImageLoadError`: Write garbage bytes to a temp file, assert `ImageLoadError` raised
- `test_missing_file_raises_ImageLoadError`: Non-existent path

**Commit:** `fix: add ImageLoadError for corrupted/missing image files`

---

### Task 2.2: ROI Bounds Clamping

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/state.py` (add `clamp_roi` method or standalone function)
- Modify: controller pretune sub-controller (call clamp on ROI set)
- Test: `bubbletrack/tests/test_state.py` (add ROI clamping tests)

**Implementation:**

```python
# model/state.py or model/conventions.py
def clamp_roi(gridx: tuple[int,int], gridy: tuple[int,int],
              img_height: int, img_width: int) -> tuple[tuple[int,int], tuple[int,int]]:
    """Clamp 1-based inclusive ROI to image dimensions."""
    rx = (max(1, gridx[0]), min(img_height, gridx[1]))
    ry = (max(1, gridy[0]), min(img_width, gridy[1]))
    return rx, ry
```

**Tests:**
- `test_clamp_roi_within_bounds`: No change when valid
- `test_clamp_roi_exceeds_height`: Clamps row to image height
- `test_clamp_roi_negative`: Clamps to 1

**Commit:** `fix: clamp ROI bounds to image dimensions`

---

### Task 2.3: Worker Thread Per-Frame Exception Handling

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/worker.py`
- Test: `bubbletrack/tests/test_worker.py` (new)

**Implementation:**

In `BatchWorker.run()`, wrap per-frame processing in try-except. On failure: emit `frame_error(idx, msg)` signal, log the error, continue to next frame.

```python
# worker.py - in run() loop
for i in range(start, end):
    if self._stop_requested:
        break
    try:
        # ... existing processing ...
        self.frame_done.emit(i, radius, edge_xy, binary_roi)
    except Exception as e:
        logger.error("Frame %d failed: %s", i, e)
        self.frame_error.emit(i, str(e))
    self.progress.emit(i - start + 1, total)
```

Add new signal: `frame_error = pyqtSignal(int, str)`

**Commit:** `fix: worker continues on per-frame errors instead of aborting`

---

### Task 2.4: Thread Safety for Result Arrays

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/auto_controller.py`
- Modify: `bubbletrack/src/bubbletrack/controller/worker.py`

**Implementation:**

Change approach: Worker thread should NOT write directly to state. Instead, emit results via `frame_done` signal. The main thread (auto_controller) receives the signal and updates state. This is already partially the pattern, but ensure NO direct state mutation in worker thread.

Verify that `_on_auto_frame_done` runs on the main thread (Qt signal/slot with `QueuedConnection` guarantees this for cross-thread signals).

**Commit:** `fix: ensure result array updates happen on main thread only`

---

### Task 2.5: Rmax Fit Window Validation

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/export.py`
- Test: `bubbletrack/tests/test_export.py` (add edge case tests)

**Implementation:**

Before quadratic fit, filter `radius > 0` and check window has enough valid points:

```python
# export.py - in export_rof_t_data()
valid_mask = radius > 0
valid_radii = radius[valid_mask]
if len(valid_radii) < 3:
    return False, "Not enough valid frames (need >= 3)"
```

**Tests:**
- `test_rmax_fit_with_gaps`: radius array with -1 gaps near peak
- `test_rmax_fit_all_invalid`: all -1 returns error message

**Commit:** `fix: filter invalid frames before Rmax quadratic fit`

---

### Task 2.6: Manual Mode Point Deduplication

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/manual_controller.py`
- Test: `bubbletrack/tests/test_manual_dedup.py` (new)

**Implementation:**

```python
MIN_POINT_DISTANCE_PX = 5.0

def _on_point_clicked(self, x: float, y: float) -> None:
    new_pt = np.array([y, x])  # row, col
    for pt in self._manual_points:
        if np.linalg.norm(pt - new_pt) < MIN_POINT_DISTANCE_PX:
            logger.info("Ignoring duplicate point at (%.1f, %.1f)", x, y)
            return
    self._manual_points.append(new_pt)
    # ... update UI
```

**Commit:** `fix: deduplicate manual points within 5px distance`

---

### Task 2.7: Path Validation in scan_folder

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py`
- Test: `bubbletrack/tests/test_image_io.py` (add security tests)

**Implementation:**

```python
def scan_folder(folder: str) -> list[str]:
    p = Path(folder).resolve()
    if not p.is_dir():
        logger.warning("Not a directory: %s", folder)
        return []
    # Verify no symlink escape
    for f in p.iterdir():
        if f.is_symlink():
            logger.warning("Skipping symlink: %s", f)
            continue
        # ... existing logic
```

**Commit:** `fix: validate folder path and skip symlinks in scan_folder`

---

### Task 2.8: loadmat Deserialization Protection

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/export.py` (add safe_loadmat)
- Test: `bubbletrack/tests/test_export.py`

**Implementation:**

```python
def safe_loadmat(filepath: str, expected_keys: set[str]) -> dict:
    """Load .mat file with structure validation."""
    try:
        data = scipy.io.loadmat(filepath)
    except Exception as e:
        raise ValueError(f"Invalid MAT file: {e}") from e
    missing = expected_keys - set(data.keys())
    if missing:
        raise ValueError(f"MAT file missing keys: {missing}")
    return data
```

**Commit:** `fix: add safe_loadmat with structure validation`

---

## Phase 3: UX & Interaction

> **Goal:** Keyboard shortcuts, undo, ETA, image comparison, chart interaction.
> **Depends on:** Phase 1 (event bus, controller split)

---

### Task 3.1: Keyboard Shortcuts

**Files:**
- Create: `bubbletrack/src/bubbletrack/ui/shortcuts.py`
- Modify: `bubbletrack/src/bubbletrack/ui/main_window.py`

**Implementation:**

```python
# ui/shortcuts.py
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget

def setup_shortcuts(window: QWidget, bus) -> list[QShortcut]:
    """Register keyboard shortcuts."""
    shortcuts = []
    def _add(key: str, event: str, *args):
        sc = QShortcut(QKeySequence(key), window)
        sc.activated.connect(lambda: bus.emit(event, *args))
        shortcuts.append(sc)

    _add("Left",      "frame_prev")
    _add("Right",     "frame_next")
    _add("Space",     "toggle_play")
    _add("Ctrl+Z",    "undo")
    _add("Ctrl+S",    "quick_export")
    _add("Ctrl+Shift+Z", "redo")
    _add("+",         "zoom_in")
    _add("-",         "zoom_out")
    _add("0",         "zoom_reset")
    return shortcuts
```

**Commit:** `feat: add keyboard shortcuts for frame nav, undo, zoom, export`

---

### Task 3.2: Undo/Redo for Manual Mode

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/undo.py`
- Modify: `bubbletrack/src/bubbletrack/controller/manual_controller.py`
- Test: `bubbletrack/tests/test_undo.py`

**Implementation:**

```python
# model/undo.py
from __future__ import annotations
from typing import Any

class UndoStack:
    """Generic undo/redo stack."""

    def __init__(self, max_size: int = 100) -> None:
        self._undo: list[Any] = []
        self._redo: list[Any] = []
        self._max = max_size

    def push(self, state: Any) -> None:
        self._undo.append(state)
        if len(self._undo) > self._max:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> Any | None:
        if not self._undo:
            return None
        state = self._undo.pop()
        self._redo.append(state)
        return state

    def redo(self) -> Any | None:
        if not self._redo:
            return None
        state = self._redo.pop()
        self._undo.append(state)
        return state

    def can_undo(self) -> bool:
        return len(self._undo) > 0

    def can_redo(self) -> bool:
        return len(self._redo) > 0

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()
```

Use in manual_controller: each `_on_point_clicked` pushes the point list snapshot; undo pops last point.

**Commit:** `feat: undo/redo stack for manual point selection`

---

### Task 3.3: Auto Fit ETA Display

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/auto_controller.py`
- Modify: `bubbletrack/src/bubbletrack/ui/automatic_tab.py`

**Implementation:**

Track `_auto_start_time = time.monotonic()` when batch starts. In `_on_auto_progress(current, total)`:

```python
elapsed = time.monotonic() - self._auto_start_time
if current > 0:
    eta_sec = elapsed / current * (total - current)
    minutes, secs = divmod(int(eta_sec), 60)
    self.bus.emit("auto_eta", f"{minutes}m {secs}s remaining")
```

**Commit:** `feat: show ETA during automatic batch fitting`

---

### Task 3.4: Smart Export Path

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/export_controller.py`

**Implementation:**

Default export directory = image folder. Default filename includes timestamp:

```python
from datetime import datetime

def _default_filename(self, prefix: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.mat"
```

**Commit:** `feat: smart default export path with timestamp`

---

### Task 3.5: Image Comparison Mode (Overlay / Slider Wipe)

**Files:**
- Create: `bubbletrack/src/bubbletrack/ui/image_compare.py`
- Modify: `bubbletrack/src/bubbletrack/ui/main_window.py`

**Implementation:**

Add a toggle button in the image area toolbar: "Side-by-side | Overlay | Wipe"

- **Overlay mode**: Alpha-blend original (grayscale) with binary (colored) in a single QGraphicsView
- **Wipe mode**: Vertical slider divides the view; left = original, right = binary. Drag the slider to compare.

```python
# ui/image_compare.py
class CompareMode(Enum):
    SIDE_BY_SIDE = "side_by_side"
    OVERLAY = "overlay"
    WIPE = "wipe"

class ImageCompareWidget(QWidget):
    """Combines two images with selectable comparison mode."""
    mode_changed = pyqtSignal(str)

    def set_images(self, original: np.ndarray, binary: np.ndarray) -> None: ...
    def set_mode(self, mode: CompareMode) -> None: ...
```

**Commit:** `feat: image comparison modes (side-by-side, overlay, wipe)`

---

### Task 3.6: R-t Chart Interaction Enhancement

**Files:**
- Modify: `bubbletrack/src/bubbletrack/ui/radius_chart.py` (rewrite with pyqtgraph)
- Modify: `bubbletrack/pyproject.toml` (add pyqtgraph dependency)

**Implementation:**

Replace Matplotlib with pyqtgraph:
- Click on data point → emit `point_selected(frame_idx)` → controller jumps to that frame
- Box select → emit `region_selected(frame_start, frame_end)` → controller highlights anomalies
- Built-in zoom/pan via mouse wheel and drag
- Right-click context menu: "Delete selected points", "Refit selected range"

**Note:** This task overlaps with Phase 4 Task 4.3 (pyqtgraph replacement). Implement together.

**Commit:** `feat: interactive R-t chart with pyqtgraph (click, select, zoom)`

---

## Phase 4: Performance

> **Goal:** Caching, faster charting, parallel batch processing.
> **Depends on:** Phase 1

---

### Task 4.1: Image LRU Cache

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/cache.py`
- Modify: `bubbletrack/src/bubbletrack/controller/file_controller.py`
- Test: `bubbletrack/tests/test_cache.py`

**Implementation:**

```python
# model/cache.py
from functools import lru_cache
from collections import OrderedDict
import numpy as np

class ImageCache:
    """LRU cache for loaded and normalized images.

    Stores (img_norm, binary, roi, binary_roi) tuples.
    Evicts oldest entries when memory limit is reached.
    """

    def __init__(self, max_bytes: int = 200 * 1024 * 1024) -> None:  # 200 MB
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._sizes: dict[str, int] = {}
        self._total = 0
        self._max = max_bytes

    def get(self, key: str) -> tuple | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: tuple) -> None:
        size = sum(v.nbytes for v in value if isinstance(v, np.ndarray))
        while self._total + size > self._max and self._cache:
            old_key, _ = self._cache.popitem(last=False)
            self._total -= self._sizes.pop(old_key)
        self._cache[key] = value
        self._sizes[key] = size
        self._total += size

    def invalidate(self) -> None:
        self._cache.clear()
        self._sizes.clear()
        self._total = 0
```

Cache key = `f"{filepath}:{sensitivity}:{gridx}:{gridy}:{gaussian}:{clahe}"`. Invalidate on parameter change.

**Commit:** `feat: LRU image cache (200MB limit) for frame navigation`

---

### Task 4.2: Preview Detection Cache

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/pretune_controller.py`

**Implementation:**

Store `_last_binary_roi` and `_last_binary_params`. In `_preview_detection()`:

```python
current_params = (self.state.img_thr, self.state.gridx, self.state.gridy,
                  self.state.gaussian_sigma, self.state.clahe_clip)
if current_params == self._last_binary_params and self._last_binary_roi is not None:
    # Skip normalization + binarization, reuse cached binary ROI
    binary_roi = self._last_binary_roi
else:
    # Full recompute
    _, _, _, binary_roi = load_and_normalize(...)
    self._last_binary_roi = binary_roi
    self._last_binary_params = current_params
```

**Commit:** `perf: cache binary ROI to skip recompute when only RF changes`

---

### Task 4.3: Replace Matplotlib with pyqtgraph

**Files:**
- Modify: `bubbletrack/src/bubbletrack/ui/radius_chart.py` (full rewrite)
- Modify: `bubbletrack/pyproject.toml` (add `pyqtgraph` dependency)
- Modify: `bubbletrack/build.spec` and `build_onefile.spec` (add hidden import)

**Implementation:**

```python
# ui/radius_chart.py (rewritten)
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal

class RadiusChart(pg.PlotWidget):
    point_clicked = pyqtSignal(int)        # frame index
    region_selected = pyqtSignal(int, int)  # start, end frame

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("w")
        self.setLabel("left", "Radius [px]")
        self.setLabel("bottom", "Frame No.")
        self._scatter = pg.ScatterPlotItem(pen="r", symbol="+", size=10)
        self.addItem(self._scatter)
        self._scatter.sigClicked.connect(self._on_click)

    def plot_all(self, radius: np.ndarray) -> None:
        valid = radius > 0
        frames = np.where(valid)[0] + 1  # 1-based display
        self._scatter.setData(frames, radius[valid])

    def clear(self) -> None:
        self._scatter.setData([], [])

    def _on_click(self, _, points):
        if points:
            idx = int(points[0].pos().x()) - 1  # back to 0-based
            self.point_clicked.emit(idx)
```

Remove `matplotlib` from dependencies (unless used elsewhere).

**Commit:** `perf: replace Matplotlib with pyqtgraph for 10-100x faster chart updates`

---

### Task 4.4: Multiprocess Batch Processing

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/worker.py`
- Test: `bubbletrack/tests/test_worker.py`

**Implementation:**

Use `concurrent.futures.ProcessPoolExecutor` with chunked frame ranges:

```python
# worker.py
from concurrent.futures import ProcessPoolExecutor, as_completed

def _process_single_frame(args):
    """Standalone function (must be picklable for multiprocessing)."""
    idx, filepath, sensitivity, gridx, gridy, edges, rf, params = args
    img_norm, binary, roi, binary_roi = load_and_normalize(filepath, sensitivity, gridx, gridy, **params)
    processed, edge_xy = detect_bubble(binary_roi, edges, rf, gridx, gridy, **params)
    row_c, col_c, radius = circle_fit_taubin(edge_xy)
    return idx, radius, (row_c, col_c), edge_xy, processed

class BatchWorker(QThread):
    def run(self):
        n_workers = min(4, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = {pool.submit(_process_single_frame, args): args[0]
                       for args in self._build_args()}
            for fut in as_completed(futures):
                if self._stop_requested:
                    pool.shutdown(wait=False, cancel_futures=True)
                    break
                idx = futures[fut]
                try:
                    result = fut.result()
                    self.frame_done.emit(*result[:4])
                except Exception as e:
                    self.frame_error.emit(idx, str(e))
                self.progress.emit(self._done_count, self._total)
```

**Note:** `_process_single_frame` must be a module-level function (not a method) for pickling.

**Commit:** `perf: multiprocess batch processing (4 workers default)`

---

## Phase 5: Persistence & New Features

> **Goal:** Configuration persistence, session files, anomaly detection, video input, auto-optimization, batch experiments, image enhancement.
> **Depends on:** Phases 1-2

---

### Task 5.1: Parameter Persistence

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/config.py`
- Modify: `bubbletrack/src/bubbletrack/controller/controller.py`
- Test: `bubbletrack/tests/test_config.py`

**Implementation:**

```python
# model/config.py
import json
from pathlib import Path
from dataclasses import asdict

CONFIG_DIR = Path.home() / ".bubbletrack"
CONFIG_FILE = CONFIG_DIR / "config.json"

PERSIST_KEYS = {"img_thr", "removing_factor", "bubble_cross_edges",
                "gaussian_sigma", "clahe_clip", "closing_radius",
                "opening_radius", "um2px", "fps", "rmax_fit_length"}

def save_config(state) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {k: getattr(state, k) for k in PERSIST_KEYS}
    # Convert tuples to lists for JSON
    for k, v in data.items():
        if isinstance(v, tuple):
            data[k] = list(v)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
```

Auto-save on app close (`QApplication.aboutToQuit`). Auto-load on startup.

**Commit:** `feat: persist user parameters to ~/.bubbletrack/config.json`

---

### Task 5.2: Parameter Preset Management

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/presets.py`
- Modify: `bubbletrack/src/bubbletrack/ui/pretune_tab.py` (add preset dropdown)
- Test: `bubbletrack/tests/test_presets.py`

**Implementation:**

Presets stored as JSON files in `~/.bubbletrack/presets/`. Each preset = named parameter snapshot.

```python
# model/presets.py
PRESETS_DIR = Path.home() / ".bubbletrack" / "presets"

def save_preset(name: str, params: dict) -> Path:
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    path = PRESETS_DIR / f"{name}.json"
    path.write_text(json.dumps(params, indent=2), encoding="utf-8")
    return path

def load_preset(name: str) -> dict:
    path = PRESETS_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))

def list_presets() -> list[str]:
    if not PRESETS_DIR.exists():
        return []
    return sorted(p.stem for p in PRESETS_DIR.glob("*.json"))

def delete_preset(name: str) -> None:
    (PRESETS_DIR / f"{name}.json").unlink(missing_ok=True)
```

**Commit:** `feat: named parameter presets (save/load/delete)`

---

### Task 5.3: Session / Project File (.brt)

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/session.py`
- Modify: `bubbletrack/src/bubbletrack/ui/main_window.py` (File menu)
- Test: `bubbletrack/tests/test_session.py`

**Implementation:**

`.brt` file = JSON containing full AppState snapshot (excluding image data, only paths + parameters + result indices).

```python
# model/session.py
import json
from pathlib import Path
import numpy as np

def save_session(filepath: str, state) -> None:
    data = {
        "version": "3.0",
        "folder_path": state.folder_path,
        "image_no": state.image_no,
        "img_thr": state.img_thr,
        "gridx": list(state.gridx),
        "gridy": list(state.gridy),
        "removing_factor": state.removing_factor,
        "bubble_cross_edges": list(state.bubble_cross_edges),
        "gaussian_sigma": state.gaussian_sigma,
        "clahe_clip": state.clahe_clip,
        "closing_radius": state.closing_radius,
        "opening_radius": state.opening_radius,
        "um2px": state.um2px,
        "fps": state.fps,
        "rmax_fit_length": state.rmax_fit_length,
        "radius": state.radius.tolist() if state.radius is not None else None,
        "circle_fit_par": state.circle_fit_par.tolist() if state.circle_fit_par is not None else None,
    }
    Path(filepath).write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_session(filepath: str):
    data = json.loads(Path(filepath).read_text(encoding="utf-8"))
    # Validate version
    if data.get("version", "1.0") < "3.0":
        raise ValueError("Session file from older version, cannot load")
    return data
```

**Commit:** `feat: session file (.brt) save/load for full state persistence`

---

### Task 5.4: Incremental Auto-Save During Batch Processing

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/auto_controller.py`

**Implementation:**

Every 50 frames (configurable), auto-save intermediate results to `{folder}/.bubbletrack_autosave.mat`:

```python
AUTOSAVE_INTERVAL = 50  # frames

def _on_auto_frame_done(self, idx, radius, edge_xy, binary_roi):
    # ... existing logic ...
    if (idx + 1) % AUTOSAVE_INTERVAL == 0:
        autosave_path = Path(self.state.folder_path) / ".bubbletrack_autosave.mat"
        export_r_data(str(autosave_path), self.state.radius,
                      self.state.circle_fit_par, self.state.circle_xy)
        logger.info("Auto-saved at frame %d to %s", idx, autosave_path)
```

**Commit:** `feat: incremental auto-save every 50 frames during batch processing`

---

### Task 5.5: Anomaly Detection & Marking

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/anomaly.py`
- Modify: `bubbletrack/src/bubbletrack/ui/radius_chart.py` (highlight anomalies)
- Modify: `bubbletrack/src/bubbletrack/controller/auto_controller.py`
- Test: `bubbletrack/tests/test_anomaly.py`

**Implementation:**

```python
# model/anomaly.py
import numpy as np

def detect_anomalies(radius: np.ndarray, *,
                     nan_is_anomaly: bool = True,
                     zscore_threshold: float = 3.0,
                     jump_threshold_pct: float = 50.0) -> np.ndarray:
    """Return boolean mask of anomalous frames.

    Anomaly types:
    1. NaN / negative radius (fit failure)
    2. Z-score outlier (|z| > threshold from local median)
    3. Frame-to-frame jump > jump_threshold_pct of median radius
    """
    n = len(radius)
    flags = np.zeros(n, dtype=bool)
    valid = radius > 0

    # Type 1: fit failures
    if nan_is_anomaly:
        flags[~valid] = True

    if valid.sum() < 5:
        return flags

    r_valid = radius[valid]
    median_r = np.median(r_valid)
    mad = np.median(np.abs(r_valid - median_r))
    if mad > 0:
        z = np.abs(radius - median_r) / (mad * 1.4826)
        flags[valid & (z > zscore_threshold)] = True

    # Type 3: jumps
    for i in range(1, n):
        if valid[i] and valid[i-1]:
            jump = abs(radius[i] - radius[i-1])
            if jump > median_r * jump_threshold_pct / 100:
                flags[i] = True

    return flags
```

In chart: anomalous points shown as yellow triangles. In status bar: "N anomalies detected".

**Commit:** `feat: automatic anomaly detection (NaN, outlier, jump)`

---

### Task 5.6: Result Editing (Delete / Refit Single Frame)

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/pretune_controller.py`
- Modify: `bubbletrack/src/bubbletrack/ui/radius_chart.py` (right-click context menu)

**Implementation:**

Right-click on chart point → context menu:
- "Delete this point" → set `radius[idx] = -1`, refresh chart
- "Refit this frame" → run single-frame pretune fit on that frame
- "Delete range" → after box select, set all selected `radius[idx] = -1`

```python
# In radius_chart.py
def _on_right_click(self, event):
    menu = QMenu(self)
    menu.addAction("Delete point", lambda: self.delete_requested.emit(idx))
    menu.addAction("Refit frame", lambda: self.refit_requested.emit(idx))
    menu.exec(event.screenPos().toPoint())
```

**Commit:** `feat: right-click to delete/refit individual results`

---

### Task 5.7: Video Input Support

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py` (add video reader)
- Modify: `bubbletrack/src/bubbletrack/controller/file_controller.py`
- Modify: `bubbletrack/src/bubbletrack/ui/image_source.py` (add video file filter)
- Test: `bubbletrack/tests/test_image_io.py`

**Implementation:**

```python
# model/image_io.py
VIDEO_EXTS = {".avi", ".mp4", ".mov", ".mkv"}

def is_video_file(path: str) -> bool:
    return Path(path).suffix.lower() in VIDEO_EXTS

class VideoFrameReader:
    """Lazy frame reader for video files using OpenCV VideoCapture."""

    def __init__(self, path: str) -> None:
        self._cap = cv2.VideoCapture(str(path))
        if not self._cap.isOpened():
            raise ImageLoadError(f"Cannot open video: {path}")
        self._total = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)

    @property
    def total_frames(self) -> int:
        return self._total

    @property
    def fps(self) -> float:
        return self._fps

    def read_frame(self, idx: int) -> np.ndarray:
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = self._cap.read()
        if not ret:
            raise ImageLoadError(f"Cannot read frame {idx}")
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def close(self) -> None:
        self._cap.release()
```

In `image_source.py`, add file filter `"Video Files (*.avi *.mp4 *.mov *.mkv)"` to the folder/file dialog.

**Commit:** `feat: video file input support (AVI, MP4, MOV, MKV)`

---

### Task 5.8: Parameter Auto-Optimization

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/auto_optimize.py`
- Modify: `bubbletrack/src/bubbletrack/ui/pretune_tab.py` (add "Auto Optimize" button)
- Test: `bubbletrack/tests/test_auto_optimize.py`

**Implementation:**

Given a few manually-fitted frames as "ground truth", search for optimal threshold + removing_factor:

```python
# model/auto_optimize.py
from scipy.optimize import minimize_scalar
import numpy as np

def optimize_parameters(images: list[str], reference_frames: dict[int, float],
                        gridx, gridy, edges) -> dict:
    """Find threshold & RF that minimize radius error on reference frames.

    Parameters
    ----------
    reference_frames : dict[frame_idx, expected_radius]
        Ground truth from manual fitting

    Returns
    -------
    {"img_thr": float, "removing_factor": int, "error": float}
    """
    def objective(params):
        thr, rf = params
        total_error = 0
        for idx, expected_r in reference_frames.items():
            _, binary, _, binary_roi = load_and_normalize(images[idx], thr, gridx, gridy)
            _, edge_xy = detect_bubble(binary_roi, edges, int(rf), gridx, gridy)
            _, _, r = circle_fit_taubin(edge_xy)
            if np.isnan(r):
                total_error += 1000  # penalty
            else:
                total_error += (r - expected_r) ** 2
        return total_error / len(reference_frames)

    # Grid search (coarse) + refinement
    best = {"error": float("inf")}
    for thr in np.linspace(0.1, 0.9, 9):
        for rf in range(10, 100, 10):
            err = objective((thr, rf))
            if err < best["error"]:
                best = {"img_thr": thr, "removing_factor": rf, "error": err}
    return best
```

**Commit:** `feat: auto-optimize threshold & RF from reference frames`

---

### Task 5.9: Batch Experiment Processing

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/batch_experiments.py`
- Modify: CLI entry (Task 6.2)

**Implementation:**

Process multiple experiment folders with the same parameters:

```python
# model/batch_experiments.py
from pathlib import Path

def find_experiment_folders(root: str, pattern: str = "*") -> list[Path]:
    """Find all subfolders containing images."""
    root_path = Path(root)
    folders = []
    for d in sorted(root_path.iterdir()):
        if d.is_dir() and any(d.glob("*.tif*")):
            folders.append(d)
    return folders

def batch_process_experiments(folders: list[Path], params: dict,
                              output_dir: Path, callback=None) -> dict:
    """Process each folder as an independent experiment.

    Returns dict mapping folder_name -> {"success": bool, "n_frames": int, "output": str}
    """
    results = {}
    for i, folder in enumerate(folders):
        try:
            # ... process folder using existing pipeline ...
            results[folder.name] = {"success": True, "n_frames": n, "output": str(out_path)}
        except Exception as e:
            results[folder.name] = {"success": False, "error": str(e)}
        if callback:
            callback(i + 1, len(folders))
    return results
```

**Commit:** `feat: batch process multiple experiment folders`

---

### Task 5.10: Image Enhancement Preprocessing

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/image_io.py` (add preprocessing functions)
- Modify: `bubbletrack/src/bubbletrack/ui/pretune_tab.py` (add preprocessing controls)
- Test: `bubbletrack/tests/test_image_io.py`

**Implementation:**

Add background subtraction and advanced denoising:

```python
# model/image_io.py (new preprocessing functions)

def subtract_background(img: np.ndarray, method: str = "median",
                        kernel_size: int = 51) -> np.ndarray:
    """Subtract estimated background from image.

    Methods: 'median' (median filter), 'gaussian' (large Gaussian blur)
    """
    if method == "median":
        bg = cv2.medianBlur(img, kernel_size)
    elif method == "gaussian":
        bg = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    else:
        raise ValueError(f"Unknown method: {method}")
    result = cv2.subtract(img, bg)
    return result

def denoise_nlm(img: np.ndarray, h: float = 10.0) -> np.ndarray:
    """Non-local means denoising (better than Gaussian for structured noise)."""
    return cv2.fastNlMeansDenoising(img, None, h, 7, 21)
```

Add to pretune_tab Advanced Filters section: background subtraction toggle + kernel size, NLM denoising toggle + strength.

**Commit:** `feat: background subtraction and NLM denoising preprocessing`

---

## Phase 6: Distribution & Polish

> **Goal:** CLI mode, multi-format export, EXE optimization, onboarding, PDF reports.
> **Depends on:** Phases 1-5

---

### Task 6.1: Multi-Format Export (CSV / Excel)

**Files:**
- Modify: `bubbletrack/src/bubbletrack/model/export.py`
- Modify: `bubbletrack/src/bubbletrack/ui/post_processing.py` (format dropdown)
- Modify: `bubbletrack/pyproject.toml` (add `openpyxl` dependency)
- Test: `bubbletrack/tests/test_export.py`

**Implementation:**

```python
# model/export.py
import csv

def export_csv(filepath: str, radius, circle_fit_par, fps=None, um2px=None) -> None:
    """Export results to CSV format."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["Frame", "Radius_px", "Center_Row_px", "Center_Col_px"]
        if um2px:
            header.extend(["Radius_um", "Center_Row_um", "Center_Col_um"])
        if fps:
            header.insert(1, "Time_s")
        writer.writerow(header)
        for i in range(len(radius)):
            row = [i + 1, radius[i], circle_fit_par[i, 0], circle_fit_par[i, 1]]
            if um2px:
                row.extend([radius[i] * um2px, circle_fit_par[i,0] * um2px, circle_fit_par[i,1] * um2px])
            if fps:
                row.insert(1, i / fps)
            writer.writerow(row)

def export_excel(filepath: str, radius, circle_fit_par, fps=None, um2px=None) -> None:
    """Export results to Excel format."""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Bubble Radius Data"
    # ... similar to CSV but with openpyxl API ...
    wb.save(filepath)
```

**Commit:** `feat: export to CSV and Excel in addition to MAT`

---

### Task 6.2: CLI Batch Mode

**Files:**
- Create: `bubbletrack/src/bubbletrack/cli.py`
- Modify: `bubbletrack/pyproject.toml` (add CLI entry point)

**Implementation:**

```python
# cli.py
"""Command-line interface for headless batch processing."""

import argparse
import sys
import numpy as np
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog="bubbletrack",
        description="Bubble Radius Fitting - batch processing mode"
    )
    parser.add_argument("--folder", required=True, help="Image folder path")
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--rf", type=int, default=90, help="Removing factor [0-100]")
    parser.add_argument("--roi", nargs=4, type=int, metavar=("R0","R1","C0","C1"),
                        help="ROI bounds (1-indexed inclusive)")
    parser.add_argument("--edges", nargs=4, type=int, default=[0,0,0,0],
                        metavar=("T","R","D","L"), help="Bubble cross edges flags")
    parser.add_argument("--output", required=True, help="Output file path (.mat/.csv/.xlsx)")
    parser.add_argument("--fps", type=float, default=1e6)
    parser.add_argument("--scale", type=float, default=3.2, help="um/px")
    parser.add_argument("--preset", help="Load named preset")
    parser.add_argument("--format", choices=["mat", "csv", "xlsx"], default="mat")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()
    # ... run processing pipeline headlessly ...
    print(f"Processed {n_frames} frames. Output: {args.output}")

if __name__ == "__main__":
    main()
```

Add to `pyproject.toml`:
```toml
[project.scripts]
bubbletrack = "bubbletrack.app:main"
bubbletrack-cli = "bubbletrack.cli:main"
```

**Commit:** `feat: CLI mode for headless batch processing`

---

### Task 6.3: Slim Down EXE Build

**Files:**
- Modify: `bubbletrack/build_onefile.spec`

**Implementation:**

```python
# build_onefile.spec additions
excludes = [
    "tkinter", "unittest", "email", "xml",
    "PyQt6.QtWebEngine", "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets",
    "PyQt6.Qt3D", "PyQt6.QtBluetooth", "PyQt6.QtMultimedia",
    "PyQt6.QtNetwork", "PyQt6.QtSql", "PyQt6.QtTest",
    "PyQt6.QtQml", "PyQt6.QtQuick",
    "matplotlib",  # removed after pyqtgraph migration
]

a = Analysis(
    ...,
    excludes=excludes,
)
```

Also:
- Enable UPX compression: `upx=True` in EXE()
- Strip debug symbols: `strip=True` on non-Windows

**Commit:** `chore: slim EXE by excluding unused Qt/Python modules`

---

### Task 6.4: Move Example Data to Git LFS

**Files:**
- Modify: `.gitattributes` (add LFS tracking)

**Implementation:**

```bash
git lfs install
git lfs track "matlab_implementation/example/*.tif"
git lfs track "matlab_implementation/example/*.tiff"
echo "matlab_implementation/example/*.tif filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "matlab_implementation/example/*.tiff filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git add .gitattributes
git commit -m "chore: track example TIFF files with Git LFS"
# Then: git lfs migrate import --include="matlab_implementation/example/*.tif"
```

**Commit:** `chore: move example TIFF images to Git LFS`

---

### Task 6.5: EXE SHA256 Checksums

**Files:**
- Create: `scripts/generate_checksums.py`

**Implementation:**

```python
# scripts/generate_checksums.py
"""Generate SHA256 checksums for distribution files."""
import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    dist = Path("bubbletrack/dist_onefile")
    for f in sorted(dist.glob("*")):
        print(f"{sha256_file(f)}  {f.name}")
```

Add to README: "Verify download integrity: `python scripts/generate_checksums.py`"

**Commit:** `chore: add SHA256 checksum generation for releases`

---

### Task 6.6: Dependency Security Audit

**Files:**
- Create: `scripts/security_audit.sh`
- Modify: `bubbletrack/pyproject.toml` (add pip-audit to dev deps)

**Implementation:**

```bash
#!/bin/bash
# scripts/security_audit.sh
echo "Running pip-audit..."
pip-audit --requirement <(pip freeze) --desc
echo "Running safety check..."
pip install safety && safety check
```

Add `pip-audit` to dev dependencies:
```toml
[project.optional-dependencies]
dev = ["pytest", "pyinstaller", "pip-audit"]
```

**Commit:** `chore: add pip-audit dependency security audit script`

---

### Task 6.7: Onboarding Welcome Dialog

**Files:**
- Create: `bubbletrack/src/bubbletrack/ui/welcome_dialog.py`
- Modify: `bubbletrack/src/bubbletrack/app.py` (show on first launch)
- Modify: `bubbletrack/src/bubbletrack/model/config.py` (track first_launch)

**Implementation:**

```python
# ui/welcome_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt6.QtCore import Qt

class WelcomeDialog(QDialog):
    """First-launch tutorial overlay showing the 3-step workflow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to BubbleTrack")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        # Step-by-step workflow guide
        steps = [
            ("1. Load Images", "Select a folder containing your high-speed camera images (TIFF, PNG, JPG) or a video file."),
            ("2. Pre-tune Parameters", "Adjust threshold and removing factor until the bubble boundary is clearly detected in the binary image."),
            ("3. Fit & Export", "Use Automatic mode to batch-fit all frames, then export R(t) data to MAT, CSV, or Excel."),
        ]
        for title, desc in steps:
            layout.addWidget(QLabel(f"<b>{title}</b><br>{desc}"))

        self._dont_show = QCheckBox("Don't show this again")
        layout.addWidget(self._dont_show)

        btn = QPushButton("Get Started")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def dont_show_again(self) -> bool:
        return self._dont_show.isChecked()
```

Show only if `config.json` doesn't have `"onboarding_done": true`.

**Commit:** `feat: welcome dialog with 3-step workflow guide on first launch`

---

### Task 6.8: PDF Report Generation

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/report.py`
- Modify: `bubbletrack/src/bubbletrack/ui/post_processing.py` (add "Generate Report" button)
- Modify: `bubbletrack/pyproject.toml` (add `reportlab` or `fpdf2` dependency)

**Implementation:**

```python
# model/report.py
"""Generate PDF summary report of analysis results."""
from fpdf import FPDF
from pathlib import Path
import numpy as np
from datetime import datetime

def generate_report(filepath: str, state, chart_image_path: str | None = None) -> None:
    """Generate a PDF report with parameters, statistics, and R-t chart.

    Contents:
    1. Header: BubbleTrack Analysis Report + timestamp
    2. Parameters table: threshold, RF, ROI, edges, filters
    3. Statistics: N frames, N valid, min/max/mean radius, Rmax frame
    4. R-t chart image (if provided)
    5. Anomaly summary (if any)
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "BubbleTrack Analysis Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.ln(10)

    # Parameters section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    params = {
        "Folder": state.folder_path,
        "Threshold": f"{state.img_thr:.2f}",
        "Removing Factor": str(state.removing_factor),
        "ROI": f"rows {state.gridx}, cols {state.gridy}",
        "FPS": f"{state.fps:.0f} Hz",
        "Scale": f"{state.um2px:.2f} um/px",
    }
    for k, v in params.items():
        pdf.cell(60, 6, k + ":", new_x="RIGHT")
        pdf.cell(0, 6, v, new_x="LMARGIN", new_y="NEXT")

    # Statistics
    valid = state.radius[state.radius > 0] if state.radius is not None else np.array([])
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Results Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    stats = {
        "Total Frames": str(state.total_frames),
        "Valid Fits": str(len(valid)),
        "Min Radius": f"{valid.min():.2f} px" if len(valid) else "N/A",
        "Max Radius": f"{valid.max():.2f} px" if len(valid) else "N/A",
        "Mean Radius": f"{valid.mean():.2f} px" if len(valid) else "N/A",
    }
    for k, v in stats.items():
        pdf.cell(60, 6, k + ":", new_x="RIGHT")
        pdf.cell(0, 6, v, new_x="LMARGIN", new_y="NEXT")

    # Chart image
    if chart_image_path and Path(chart_image_path).exists():
        pdf.ln(5)
        pdf.image(chart_image_path, w=170)

    pdf.output(filepath)
```

**Commit:** `feat: PDF report generation with parameters, stats, and chart`

---

## Dependency Summary

### New Python Dependencies

| Package | Phase | Purpose |
|---------|-------|---------|
| `pyqtgraph` | 3-4 | Fast interactive charting |
| `openpyxl` | 6 | Excel export |
| `fpdf2` | 6 | PDF report generation |
| `pip-audit` | 6 (dev) | Dependency security audit |

### Updated pyproject.toml

```toml
dependencies = [
    "PyQt6>=6.5,<6.8",
    "numpy",
    "opencv-python",
    "scikit-image",
    "scipy",
    "pyqtgraph>=0.13",
    "openpyxl>=3.1",
    "fpdf2>=2.7",
]

[project.optional-dependencies]
dev = ["pytest", "pyinstaller", "pip-audit"]

[project.scripts]
bubbletrack = "bubbletrack.app:main"
bubbletrack-cli = "bubbletrack.cli:main"
```

---

## Execution Order & Dependency Graph

```
Phase 1 (Foundation)
  ├─ 1.1 Constants ─────────┐
  ├─ 1.2 Logging ───────────┤
  ├─ 1.3 Conventions ───────┤
  │                          ▼
  ├─ 1.4 Immutable State ───┐
  ├─ 1.5 Event Bus ─────────┤
  │                          ▼
  └─ 1.6 Controller Split ──┤
                             │
Phase 2 (Robustness) ◄──────┤  (all parallel)
  ├─ 2.1 Image load error   │
  ├─ 2.2 ROI clamping       │
  ├─ 2.3 Worker exceptions  │
  ├─ 2.4 Thread safety      │
  ├─ 2.5 Rmax validation    │
  ├─ 2.6 Point dedup        │
  ├─ 2.7 Path validation    │
  └─ 2.8 loadmat protection │
                             │
Phase 3 (UX) ◄──────────────┤  (all parallel)
  ├─ 3.1 Keyboard shortcuts │
  ├─ 3.2 Undo/Redo          │
  ├─ 3.3 Auto fit ETA       │
  ├─ 3.4 Smart export path  │
  ├─ 3.5 Image compare      │
  └─ 3.6 Chart interaction ─┤─► depends on 4.3
                             │
Phase 4 (Performance) ◄─────┤
  ├─ 4.1 Image cache        │
  ├─ 4.2 Preview cache      │
  ├─ 4.3 pyqtgraph ─────────┤
  └─ 4.4 Multiprocess batch │
                             │
Phase 5 (Features) ◄────────┤
  ├─ 5.1 Config persistence │
  ├─ 5.2 Preset management  │
  ├─ 5.3 Session file (.brt)│
  ├─ 5.4 Incremental save   │
  ├─ 5.5 Anomaly detection  │
  ├─ 5.6 Result editing     │
  ├─ 5.7 Video input        │
  ├─ 5.8 Auto-optimize      │
  ├─ 5.9 Batch experiments  │
  └─ 5.10 Image enhance     │
                             │
Phase 6 (Distribution) ◄────┘
  ├─ 6.1 CSV/Excel export
  ├─ 6.2 CLI mode
  ├─ 6.3 Slim EXE
  ├─ 6.4 Git LFS
  ├─ 6.5 SHA256 checksums
  ├─ 6.6 Security audit
  ├─ 6.7 Onboarding dialog
  └─ 6.8 PDF report
```

---

## Version Bump Plan

| Milestone | Version | Includes |
|-----------|---------|----------|
| Phase 1 complete | v2.1.0 | Architecture refactor |
| Phase 2 complete | v2.2.0 | Robustness hardening |
| Phase 3+4 complete | v2.5.0 | UX + Performance |
| Phase 5 complete | v2.8.0 | New features |
| Phase 6 complete | v3.0.0 | Full release |
