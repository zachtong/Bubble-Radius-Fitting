"""Shared display helpers used by multiple sub-controllers.

These are standalone functions that accept (state, window) to avoid
diamond inheritance issues.  Sub-controllers call them by passing
``self.state`` and ``self.w``.
"""

from __future__ import annotations

import numpy as np

from bubbletrack.model.circle_fit import circle_fit_taubin
from bubbletrack.model.conventions import frame_to_display
from bubbletrack.model.detection import detect_bubble
from bubbletrack.model.image_io import load_and_normalize
from bubbletrack.model.removing_factor import compute_removing_factor
from bubbletrack.model.state import AppState, update_state


def display_frame(state: AppState, window, idx: int, set_state) -> None:
    """Load, process and display frame *idx* on both image panels.

    Parameters
    ----------
    state : AppState
        Current application state.
    window : MainWindow
        Reference to the Qt main window (for UI updates).
    idx : int
        0-based frame index to display.
    set_state : callable
        Callback to persist the updated state (with cur_img etc.).
    """
    if not state.images:
        return
    try:
        cur_img, _, _, binary_roi = load_and_normalize(
            state.images[idx],
            state.img_thr,
            state.gridx,
            state.gridy,
            gaussian_sigma=state.gaussian_sigma,
            clahe_clip=state.clahe_clip,
        )
        state = update_state(
            state, cur_img=cur_img, cur_img_binary_roi=binary_roi,
        )
        set_state(state)

        window.original_panel.set_image(cur_img)

        # For fitted frames, show the actual detection result;
        # for unfitted frames, show the raw threshold.
        if state.radius is not None and state.radius[idx] > 0:
            rf = compute_removing_factor(
                state.removing_factor,
                state.gridx, state.gridy,
            )
            processed, _ = detect_bubble(
                binary_roi, state.bubble_cross_edges, rf,
                state.gridx, state.gridy,
                state.removing_obj_radius,
                opening_radius=state.opening_radius,
                closing_radius=state.closing_radius,
            )
            window.binary_panel.set_image(processed)
        else:
            window.binary_panel.set_image(~binary_roi)

        # Draw ROI rectangle on original
        window.original_panel.draw_roi_rect(state.gridx, state.gridy)

        # Draw existing circle fit if available
        if (state.radius is not None
                and state.radius[idx] > 0
                and state.circle_fit_par is not None):
            rc = state.circle_fit_par[idx, 0]
            cc = state.circle_fit_par[idx, 1]
            r = state.radius[idx]
            window.original_panel.draw_circle(rc, cc, r, "#3B82F6")
            if state.circle_xy and state.circle_xy[idx] is not None:
                window.original_panel.draw_points(
                    state.circle_xy[idx], "#EF4444", 2.0,
                )

        window.status_bar.update_frame(
            frame_to_display(idx), state.total_frames,
        )
        window.status_bar.update_roi(state.gridx, state.gridy)
    except Exception as exc:
        window.header.set_status(f"Error: {exc}", "#EF4444")


def refresh_chart(state: AppState, window) -> None:
    """Redraw R-t chart from state data (prevents duplicate markers)."""
    if state.radius is not None:
        frames = np.arange(1, len(state.radius) + 1)
        window.radius_chart.plot_all(frames, state.radius)


def redraw_original(state: AppState, window) -> None:
    """Clear overlays on original panel and re-draw ROI rect."""
    window.original_panel.clear_overlays()
    window.original_panel.draw_roi_rect(state.gridx, state.gridy)
