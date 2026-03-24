# Auto-Tune + Quality Score Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add one-click automatic parameter optimization (threshold + removing factor + advanced filters) and real-time fit quality feedback, eliminating the manual trial-and-error tuning pain point.

**Architecture:** Pure-function quality scoring + coarse-to-fine grid search in the model layer, QThread worker for non-blocking UI, quality display integrated into the existing PreTuneTab. The quality function returns a `FitQuality` dataclass; the auto-tune function returns an `AutoTuneResult` with best parameters + score.

**Tech Stack:** Python 3.12, NumPy, PyQt6 (QThread, pyqtSignal), existing detection pipeline (load_and_normalize → detect_bubble → circle_fit_taubin).

---

## Task 1: Quality Score Model Function

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/quality.py`
- Modify: `bubbletrack/src/bubbletrack/model/constants.py` (add quality constants)

**Step 1: Add quality constants**

In `model/constants.py`, append:

```python
# ------------------------------------------------------------------ #
#  Fit quality scoring
# ------------------------------------------------------------------ #

QUALITY_TARGET_EDGE_DENSITY: float = 0.6
"""Target edge points per pixel of circumference (≈1 point every 1.7 px)."""

QUALITY_MAX_RMS_RATIO: float = 0.15
"""RMS residual / radius ratio above which the fit is considered poor."""

QUALITY_N_SECTORS: int = 8
"""Number of angular sectors for coverage scoring."""

QUALITY_MIN_RADIUS_FRACTION: float = 0.03
"""Minimum plausible radius as fraction of ROI short side."""

QUALITY_MAX_RADIUS_FRACTION: float = 0.85
"""Maximum plausible radius as fraction of ROI short side."""
```

**Step 2: Create `model/quality.py`**

```python
"""Fit quality scoring for auto-tune and real-time feedback."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bubbletrack.model.constants import (
    QUALITY_MAX_RADIUS_FRACTION,
    QUALITY_MAX_RMS_RATIO,
    QUALITY_MIN_RADIUS_FRACTION,
    QUALITY_N_SECTORS,
    QUALITY_TARGET_EDGE_DENSITY,
)


@dataclass(frozen=True)
class FitQuality:
    """Quality metrics for a single circle fit."""

    score: float           # Composite [0, 1], higher = better
    n_edge_points: int     # Number of detected edge pixels
    edge_density: float    # Points per px of circumference
    rms_residual: float    # RMS distance from fitted circle (px)
    sector_coverage: float # Fraction of angular sectors with points [0, 1]
    radius: float          # Fitted radius (px)


def compute_fit_quality(
    edge_xy: np.ndarray,
    rc: float,
    cc: float,
    radius: float,
    roi_short_side: int,
) -> FitQuality:
    """Score a circle fit result.

    Parameters
    ----------
    edge_xy : (N, 2) array of [row, col] edge points (full-image coords).
    rc, cc  : Circle centre (row, col).
    radius  : Fitted radius in pixels.
    roi_short_side : min(ROI height, ROI width) for plausibility check.

    Returns
    -------
    FitQuality with composite score in [0, 1].
    """
    n = edge_xy.shape[0]
    circumference = 2.0 * np.pi * radius

    # 1. Edge density
    edge_density = n / circumference if circumference > 0 else 0.0
    density_score = min(edge_density / QUALITY_TARGET_EDGE_DENSITY, 1.0)

    # 2. RMS residual
    dists = np.linalg.norm(edge_xy - np.array([rc, cc]), axis=1)
    residuals = dists - radius
    rms = float(np.sqrt(np.mean(residuals ** 2)))
    rms_ratio = rms / radius if radius > 0 else 1.0
    rms_score = max(0.0, 1.0 - rms_ratio / QUALITY_MAX_RMS_RATIO)

    # 3. Angular sector coverage
    dy = edge_xy[:, 0] - rc
    dx = edge_xy[:, 1] - cc
    angles = np.arctan2(dy, dx)  # [-pi, pi]
    # Map to sector indices
    sector_edges = np.linspace(-np.pi, np.pi, QUALITY_N_SECTORS + 1)
    sectors_hit = set()
    for a in angles:
        idx = int(np.searchsorted(sector_edges, a, side="right")) - 1
        idx = max(0, min(idx, QUALITY_N_SECTORS - 1))
        sectors_hit.add(idx)
    sector_coverage = len(sectors_hit) / QUALITY_N_SECTORS

    # 4. Radius plausibility
    if roi_short_side > 0:
        r_frac = radius / roi_short_side
        if QUALITY_MIN_RADIUS_FRACTION <= r_frac <= QUALITY_MAX_RADIUS_FRACTION:
            plausibility = 1.0
        else:
            plausibility = 0.0
    else:
        plausibility = 0.5

    # Composite score (weighted)
    score = (
        0.25 * density_score
        + 0.30 * rms_score
        + 0.30 * sector_coverage
        + 0.15 * plausibility
    )

    return FitQuality(
        score=round(score, 3),
        n_edge_points=n,
        edge_density=round(edge_density, 3),
        rms_residual=round(rms, 2),
        sector_coverage=round(sector_coverage, 3),
        radius=round(radius, 2),
    )


def score_failed_fit() -> FitQuality:
    """Return a zero-score FitQuality for failed detections."""
    return FitQuality(
        score=0.0,
        n_edge_points=0,
        edge_density=0.0,
        rms_residual=float("inf"),
        sector_coverage=0.0,
        radius=0.0,
    )
```

**Step 3: Verify**

Run: `python -c "from bubbletrack.model.quality import compute_fit_quality, FitQuality; print('OK')"`

---

## Task 2: Auto-Tune Search Algorithm

**Files:**
- Create: `bubbletrack/src/bubbletrack/model/autotune.py`
- Modify: `bubbletrack/src/bubbletrack/model/constants.py` (add autotune grid constants)

**Step 1: Add autotune constants**

In `model/constants.py`, append:

```python
# ------------------------------------------------------------------ #
#  Auto-tune grid search
# ------------------------------------------------------------------ #

AUTOTUNE_THR_COARSE: tuple[float, ...] = (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80)
"""Coarse threshold grid for auto-tune."""

AUTOTUNE_RF_COARSE: tuple[int, ...] = (40, 55, 70, 80, 90, 95)
"""Coarse removing-factor grid for auto-tune."""

AUTOTUNE_THR_FINE_STEP: float = 0.05
"""Fine-search threshold step around best coarse value."""

AUTOTUNE_RF_FINE_STEP: int = 5
"""Fine-search removing-factor step around best coarse value."""

AUTOTUNE_TOP_K: int = 3
"""Number of top coarse candidates to refine."""
```

**Step 2: Create `model/autotune.py`**

```python
"""Automatic parameter tuning via coarse-to-fine grid search."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

import numpy as np

from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.constants import (
    AUTOTUNE_RF_COARSE,
    AUTOTUNE_RF_FINE_STEP,
    AUTOTUNE_THR_COARSE,
    AUTOTUNE_THR_FINE_STEP,
    AUTOTUNE_TOP_K,
)
from bubbletrack.model.detection import detect_bubble
from bubbletrack.model.image_io import load_and_normalize
from bubbletrack.model.quality import FitQuality, compute_fit_quality, score_failed_fit
from bubbletrack.model.removing_factor import compute_removing_factor

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AutoTuneResult:
    """Result of automatic parameter tuning."""

    threshold: float       # Best img_thr [0, 1]
    removing_factor: int   # Best RF slider value [0, 100]
    quality: FitQuality    # Quality metrics at best params
    candidates_evaluated: int  # Total combinations tested


def run_autotune(
    image_path: str,
    gridx: tuple[int, int],
    gridy: tuple[int, int],
    bubble_cross_edges: tuple[bool, ...],
    *,
    gaussian_sigma: float = 0.0,
    clahe_clip: float = 0.0,
    opening_radius: int = 0,
    closing_radius: int = 0,
    max_radius: float = float("inf"),
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> AutoTuneResult | None:
    """Find optimal (threshold, removing_factor) via coarse-to-fine grid search.

    Parameters
    ----------
    image_path : Path to the image file to tune on.
    gridx, gridy : 1-indexed ROI bounds.
    bubble_cross_edges : Edge crossing flags.
    gaussian_sigma, clahe_clip, opening_radius, closing_radius :
        Fixed advanced filter values (not searched).
    max_radius : Upper bound for plausible radius.
    progress_callback : Called with (current_step, total_steps).
    cancel_check : Returns True if user cancelled.

    Returns
    -------
    AutoTuneResult or None if cancelled / all candidates fail.
    """
    roi_h = gridx[1] - gridx[0] + 1
    roi_w = gridy[1] - gridy[0] + 1
    roi_short_side = min(roi_h, roi_w)

    # Estimate total steps for progress reporting
    coarse_total = len(AUTOTUNE_THR_COARSE) * len(AUTOTUNE_RF_COARSE)
    fine_total = AUTOTUNE_TOP_K * 9  # 3x3 fine grid per candidate
    total_steps = coarse_total + fine_total
    step = 0

    def _report(s: int) -> None:
        nonlocal step
        step = s
        if progress_callback:
            progress_callback(step, total_steps)

    def _cancelled() -> bool:
        return cancel_check is not None and cancel_check()

    # ---- Phase 1: Coarse search ----
    # Cache: group by threshold to reuse binary_roi across RF values
    coarse_results: list[tuple[float, int, FitQuality]] = []

    for thr in AUTOTUNE_THR_COARSE:
        if _cancelled():
            return None

        # One load_and_normalize per threshold value
        try:
            _, _, _, binary_roi = load_and_normalize(
                image_path, thr, gridx, gridy,
                gaussian_sigma=gaussian_sigma,
                clahe_clip=clahe_clip,
            )
        except Exception:
            step += len(AUTOTUNE_RF_COARSE)
            _report(step)
            continue

        for rf_slider in AUTOTUNE_RF_COARSE:
            if _cancelled():
                return None

            quality = _evaluate_params(
                binary_roi, bubble_cross_edges, rf_slider,
                gridx, gridy, opening_radius, closing_radius,
                max_radius, roi_short_side,
            )
            coarse_results.append((thr, rf_slider, quality))

            step += 1
            _report(step)

    if not coarse_results:
        return None

    # Sort by score descending, take top K
    coarse_results.sort(key=lambda x: x[2].score, reverse=True)
    top_candidates = coarse_results[:AUTOTUNE_TOP_K]

    # ---- Phase 2: Fine search around top candidates ----
    fine_results: list[tuple[float, int, FitQuality]] = []
    seen: set[tuple[float, int]] = set()

    for base_thr, base_rf, _ in top_candidates:
        fine_thrs = [
            round(base_thr - AUTOTUNE_THR_FINE_STEP, 2),
            round(base_thr, 2),
            round(base_thr + AUTOTUNE_THR_FINE_STEP, 2),
        ]
        fine_rfs = [
            base_rf - AUTOTUNE_RF_FINE_STEP,
            base_rf,
            base_rf + AUTOTUNE_RF_FINE_STEP,
        ]

        for thr in fine_thrs:
            if thr < 0.05 or thr > 0.95:
                step += len(fine_rfs)
                _report(step)
                continue
            if _cancelled():
                return None

            try:
                _, _, _, binary_roi = load_and_normalize(
                    image_path, thr, gridx, gridy,
                    gaussian_sigma=gaussian_sigma,
                    clahe_clip=clahe_clip,
                )
            except Exception:
                step += len(fine_rfs)
                _report(step)
                continue

            for rf_slider in fine_rfs:
                if _cancelled():
                    return None
                rf_slider = max(0, min(100, rf_slider))
                key = (thr, rf_slider)
                if key in seen:
                    step += 1
                    _report(step)
                    continue
                seen.add(key)

                quality = _evaluate_params(
                    binary_roi, bubble_cross_edges, rf_slider,
                    gridx, gridy, opening_radius, closing_radius,
                    max_radius, roi_short_side,
                )
                fine_results.append((thr, rf_slider, quality))

                step += 1
                _report(step)

    # Combine coarse + fine, pick best
    all_results = coarse_results + fine_results
    all_results.sort(key=lambda x: x[2].score, reverse=True)

    best_thr, best_rf, best_quality = all_results[0]
    if best_quality.score <= 0:
        return None

    return AutoTuneResult(
        threshold=best_thr,
        removing_factor=best_rf,
        quality=best_quality,
        candidates_evaluated=len(seen) + coarse_total,
    )


def _evaluate_params(
    binary_roi: np.ndarray,
    bubble_cross_edges: tuple[bool, ...],
    rf_slider: int,
    gridx: tuple[int, int],
    gridy: tuple[int, int],
    opening_radius: int,
    closing_radius: int,
    max_radius: float,
    roi_short_side: int,
) -> FitQuality:
    """Run detect + fit + score for one parameter combination."""
    try:
        rf = compute_removing_factor(rf_slider, gridx, gridy)
        _, edge_xy = detect_bubble(
            binary_roi, list(bubble_cross_edges), rf,
            gridx, gridy, 0,
            opening_radius=opening_radius,
            closing_radius=closing_radius,
        )

        if edge_xy.shape[0] < 3:
            return score_failed_fit()

        rc, cc, radius = circle_fit_taubin(edge_xy)

        if not np.isfinite(radius) or radius <= 0 or radius > max_radius:
            return score_failed_fit()

        return compute_fit_quality(edge_xy, rc, cc, radius, roi_short_side)

    except Exception:
        return score_failed_fit()
```

**Step 3: Verify**

Run: `python -c "from bubbletrack.model.autotune import run_autotune, AutoTuneResult; print('OK')"`

---

## Task 3: UI — Auto Tune Button + Quality Display

**Files:**
- Modify: `bubbletrack/src/bubbletrack/ui/pretune_tab.py`
- Modify: `bubbletrack/src/bubbletrack/resources/style.qss`

**Step 1: Add signals and UI elements to PreTuneTab**

In `pretune_tab.py`, add a new signal:

```python
autotune_clicked = pyqtSignal()
```

After the "Fit Current Frame" button (L169-171), insert:

```python
# -- Auto-Tune button --
self._autotune_btn = QPushButton("Auto Tune")
self._autotune_btn.setToolTip(
    "Automatically find optimal Threshold and Removing Factor\n"
    "by testing multiple combinations on the current frame."
)
self._autotune_btn.clicked.connect(self.autotune_clicked)
layout.addWidget(self._autotune_btn)

# -- Quality display --
self._quality_label = QLabel("")
self._quality_label.setObjectName("qualityLabel")
self._quality_label.setWordWrap(True)
self._quality_label.hide()
layout.addWidget(self._quality_label)
```

Add a public method to update the quality display:

```python
def show_quality(self, n_pts: int, rms: float, score_pct: int) -> None:
    """Show fit quality metrics below the buttons."""
    self._quality_label.setText(
        f'<span style="color:#a1a1aa;">Edge pts:</span> {n_pts} &nbsp; '
        f'<span style="color:#a1a1aa;">RMS:</span> {rms:.1f} px &nbsp; '
        f'<span style="color:#a1a1aa;">Confidence:</span> '
        f'<span style="color:{"#10b981" if score_pct >= 70 else "#f59e0b" if score_pct >= 40 else "#ef4444"};">'
        f'{score_pct}%</span>'
    )
    self._quality_label.show()

def hide_quality(self) -> None:
    self._quality_label.hide()

def set_autotune_enabled(self, enabled: bool) -> None:
    """Enable/disable the auto-tune button (during search)."""
    self._autotune_btn.setEnabled(enabled)
    self._autotune_btn.setText("Searching..." if not enabled else "Auto Tune")
```

**Step 2: Add QSS for quality label**

In `style.qss`, append before the Tooltips section:

```css
/* ---------- Quality label ---------- */
QLabel#qualityLabel {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    color: #a1a1aa;
}
```

---

## Task 4: Auto-Tune Worker Thread

**Files:**
- Create: `bubbletrack/src/bubbletrack/controller/autotune_worker.py`

**Step 1: Create QThread worker**

```python
"""Background worker for automatic parameter tuning."""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from bubbletrack.model.autotune import AutoTuneResult, run_autotune


class AutoTuneWorker(QThread):
    """Runs auto-tune grid search in a background thread.

    Signals
    -------
    progress(int, int) : (current_step, total_steps)
    finished(object)   : AutoTuneResult or None
    """

    progress = pyqtSignal(int, int)
    finished = pyqtSignal(object)

    def __init__(
        self,
        image_path: str,
        gridx: tuple[int, int],
        gridy: tuple[int, int],
        bubble_cross_edges: tuple[bool, ...],
        *,
        gaussian_sigma: float = 0.0,
        clahe_clip: float = 0.0,
        opening_radius: int = 0,
        closing_radius: int = 0,
        max_radius: float = float("inf"),
    ) -> None:
        super().__init__()
        self._image_path = image_path
        self._gridx = gridx
        self._gridy = gridy
        self._edges = bubble_cross_edges
        self._gaussian_sigma = gaussian_sigma
        self._clahe_clip = clahe_clip
        self._opening_radius = opening_radius
        self._closing_radius = closing_radius
        self._max_radius = max_radius
        self._cancelled = False

    def run(self) -> None:
        result = run_autotune(
            self._image_path,
            self._gridx,
            self._gridy,
            self._edges,
            gaussian_sigma=self._gaussian_sigma,
            clahe_clip=self._clahe_clip,
            opening_radius=self._opening_radius,
            closing_radius=self._closing_radius,
            max_radius=self._max_radius,
            progress_callback=self._on_progress,
            cancel_check=lambda: self._cancelled,
        )
        self.finished.emit(result)

    def cancel(self) -> None:
        self._cancelled = True

    def _on_progress(self, current: int, total: int) -> None:
        self.progress.emit(current, total)
```

---

## Task 5: Controller — Wire Auto-Tune + Quality Score

**Files:**
- Modify: `bubbletrack/src/bubbletrack/controller/pretune_controller.py`
- Modify: `bubbletrack/src/bubbletrack/controller/controller.py`

**Step 1: Add auto-tune handler to PretuneController**

In `pretune_controller.py`, add imports:

```python
from bubbletrack.controller.autotune_worker import AutoTuneWorker
from bubbletrack.model.quality import compute_fit_quality, score_failed_fit
```

Add new methods to `PretuneController`:

```python
def __init__(self, ...):
    # ... existing code ...
    self._autotune_worker: AutoTuneWorker | None = None

def on_autotune(self) -> None:
    """Launch auto-tune grid search in background thread."""
    if not self.state.images:
        return
    if self._autotune_worker is not None and self._autotune_worker.isRunning():
        return  # Already running

    idx = self.state.image_no
    self.w.header.set_status("Auto-tuning...", "#f59e0b")
    self.w.left_panel.pretune_tab.set_autotune_enabled(False)

    self._autotune_worker = AutoTuneWorker(
        self.state.images[idx],
        self.state.gridx,
        self.state.gridy,
        self.state.bubble_cross_edges,
        gaussian_sigma=self.state.gaussian_sigma,
        clahe_clip=self.state.clahe_clip,
        opening_radius=self.state.opening_radius,
        closing_radius=self.state.closing_radius,
        max_radius=self._get_max_radius(),
    )
    self._autotune_worker.progress.connect(self._on_autotune_progress)
    self._autotune_worker.finished.connect(self._on_autotune_finished)
    self._autotune_worker.start()

def _on_autotune_progress(self, current: int, total: int) -> None:
    pct = int(100 * current / total) if total > 0 else 0
    self.w.header.set_status(f"Auto-tuning... {pct}%", "#f59e0b")

def _on_autotune_finished(self, result) -> None:
    self.w.left_panel.pretune_tab.set_autotune_enabled(True)
    self._autotune_worker = None

    if result is None:
        self.w.header.set_status("Auto-tune: no valid fit found", "#ef4444")
        return

    # Apply best parameters to state + UI
    pt = self.w.left_panel.pretune_tab
    pt.set_threshold(result.threshold)
    pt._removing_factor.set_value(result.removing_factor)

    self._update(
        img_thr=result.threshold,
        removing_factor=result.removing_factor,
    )
    self._invalidate_binary_cache()
    if self._cache is not None:
        self._cache.invalidate()

    # Show quality metrics
    q = result.quality
    pt.show_quality(q.n_edge_points, q.rms_residual, int(q.score * 100))

    # Trigger display refresh + auto-fit
    display_frame(
        self.state, self.w, self.state.image_no,
        self._set_state, self._cache,
    )
    self.on_pretune_fit()

    self.w.header.set_status(
        f"Auto-tuned: thr={result.threshold:.2f}, RF={result.removing_factor}"
        f" — confidence {int(q.score * 100)}%"
        f" ({result.candidates_evaluated} tested)",
        "#10b981",
    )
```

**Step 2: Add quality display to `on_pretune_fit`**

At the end of the success branch in `on_pretune_fit` (after `refresh_chart`), add:

```python
# Show quality metrics
roi_h = self.state.gridx[1] - self.state.gridx[0] + 1
roi_w = self.state.gridy[1] - self.state.gridy[0] + 1
q = compute_fit_quality(
    edge_xy, rc, cc, radius, min(roi_h, roi_w),
)
self.w.left_panel.pretune_tab.show_quality(
    q.n_edge_points, q.rms_residual, int(q.score * 100),
)
```

And at the failure branches (too few edge points, radius outlier), add:

```python
self.w.left_panel.pretune_tab.hide_quality()
```

**Step 3: Connect signal in `controller.py`**

In `_connect_signals`, add after `pt.fit_clicked`:

```python
pt.autotune_clicked.connect(self.pretune_ctrl.on_autotune)
```

**Step 4: Verify**

Run the app: `cd bubbletrack && python -m bubbletrack`

1. Load an image folder
2. Select ROI
3. Click "Auto Tune" → should show progress in header, then apply best params
4. Click "Fit Current Frame" → should show quality metrics below button

---

## File Changes Summary

| File | Action | Task |
|------|--------|------|
| `model/constants.py` | Modify: add quality + autotune constants | 1, 2 |
| `model/quality.py` | **Create**: FitQuality dataclass + compute_fit_quality() | 1 |
| `model/autotune.py` | **Create**: AutoTuneResult + run_autotune() | 2 |
| `ui/pretune_tab.py` | Modify: add Auto Tune button + quality label | 3 |
| `resources/style.qss` | Modify: add qualityLabel style | 3 |
| `controller/autotune_worker.py` | **Create**: QThread worker | 4 |
| `controller/pretune_controller.py` | Modify: add autotune + quality handlers | 5 |
| `controller/controller.py` | Modify: connect autotune signal | 5 |

## Verification Plan

1. Launch app → load folder → select ROI
2. Click "Auto Tune" → header shows progress percentage
3. After completion: sliders move to optimal values, quality label shows metrics
4. Click "Fit Current Frame" manually → quality label updates with new metrics
5. Quality colors: green (≥70%), amber (40-69%), red (<40%)
6. Cancel: click Auto Tune again during search → button re-enables
7. No images loaded: Auto Tune button does nothing (no crash)
