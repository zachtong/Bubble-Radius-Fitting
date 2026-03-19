"""AppController — thin signal router that owns state and sub-controllers."""

from __future__ import annotations

from PyQt6.QtCore import QTimer

from bubbletrack.controller.auto_controller import AutoController
from bubbletrack.controller.display_mixin import display_frame
from bubbletrack.controller.export_controller import ExportController
from bubbletrack.controller.file_controller import FileController
from bubbletrack.controller.manual_controller import ManualController
from bubbletrack.controller.pretune_controller import PretuneController
from bubbletrack.event_bus import EventBus
from bubbletrack.model.constants import DISPLAY_DEBOUNCE_MS, PREVIEW_DEBOUNCE_MS
from bubbletrack.model.state import AppState
from bubbletrack.ui.shortcuts import setup_shortcuts


class AppController:
    """Thin orchestrator: owns state, creates sub-controllers, wires Qt signals.

    All domain logic lives in the sub-controllers.  This class only:
    1. Holds the canonical ``AppState`` instance.
    2. Creates and configures sub-controllers.
    3. Connects Qt widget signals to the correct handler.
    """

    def __init__(self, window) -> None:
        self.w = window
        self._state = AppState()
        self._max_radius: float = float("inf")

        # Event bus for decoupled inter-controller communication
        self.bus = EventBus()

        # Debounce timers for slider-driven updates
        self._display_timer = QTimer()
        self._display_timer.setSingleShot(True)
        self._display_timer.setInterval(DISPLAY_DEBOUNCE_MS)
        self._display_timer.timeout.connect(
            lambda: display_frame(
                self._state, self.w, self._state.image_no, self._set_state,
            )
        )

        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)

        # Create sub-controllers (shared state via get/set accessors)
        gs, ss = self._get_state, self._set_state

        self.file_ctrl = FileController(
            self.bus, gs, ss, self.w, self._set_max_radius,
        )
        self.pretune_ctrl = PretuneController(
            self.bus, gs, ss, self.w,
            self._display_timer, self._preview_timer, self._get_max_radius,
        )
        self.manual_ctrl = ManualController(
            self.bus, gs, ss, self.w, self._get_max_radius,
        )
        self.auto_ctrl = AutoController(
            self.bus, gs, ss, self.w, self._get_max_radius,
        )
        self.export_ctrl = ExportController(self.bus, gs, ss, self.w)

        # Wire preview timer to pretune handler
        self._preview_timer.timeout.connect(self.pretune_ctrl.preview_detection)

        # Clear manual points on tab change
        self.bus.subscribe("tab_changed", lambda idx: self.manual_ctrl.clear_points())

        self._connect_signals()

        # Keyboard shortcuts
        self._shortcuts = setup_shortcuts(self.w, {
            "frame_prev": lambda: self.file_ctrl.on_frame_changed(
                max(0, self._state.image_no - 1),
            ),
            "frame_next": lambda: self.file_ctrl.on_frame_changed(
                min(self._state.total_frames - 1, self._state.image_no + 1),
            ),
            "zoom_in": self.w.original_panel._zoom_in,
            "zoom_out": self.w.original_panel._zoom_out,
            "zoom_reset": self.w.original_panel._zoom_reset,
        })

    # ------------------------------------------------------------------ #
    #  State accessors (shared with sub-controllers)
    # ------------------------------------------------------------------ #

    def _get_state(self) -> AppState:
        return self._state

    def _set_state(self, new: AppState) -> None:
        self._state = new

    def _get_max_radius(self) -> float:
        return self._max_radius

    def _set_max_radius(self, value: float) -> None:
        self._max_radius = value

    # ------------------------------------------------------------------ #
    #  Signal wiring
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        lp = self.w.left_panel

        # Image source
        lp.image_source.folder_selected.connect(self.file_ctrl.on_folder_selected)

        # Frame scrubber
        self.w.frame_scrubber.value_changed.connect(self.file_ctrl.on_frame_changed)

        # Pre-tune
        pt = lp.pretune_tab
        pt.threshold_changed.connect(self.pretune_ctrl.on_threshold_changed)
        pt.removing_factor_changed.connect(self.pretune_ctrl.on_removing_factor_changed)
        pt.edges_changed.connect(self.pretune_ctrl.on_edges_changed)
        pt.fit_clicked.connect(self.pretune_ctrl.on_pretune_fit)
        pt.select_roi_clicked.connect(self.pretune_ctrl.on_select_roi)
        pt.frame_selected.connect(self.file_ctrl.on_tab_frame_selected)
        pt.filters_changed.connect(self.pretune_ctrl.on_filters_changed)

        # Manual
        mt = lp.manual_tab
        mt.select_clicked.connect(self.manual_ctrl.on_manual_select)
        mt.done_clicked.connect(self.manual_ctrl.on_manual_done)
        mt.clear_clicked.connect(self.manual_ctrl.on_manual_clear)
        mt.frame_selected.connect(self.file_ctrl.on_tab_frame_selected)
        self.w.original_panel.point_clicked.connect(self.manual_ctrl.on_point_clicked)

        # Tab switching
        lp.tab_bar.tab_changed.connect(self.file_ctrl.on_tab_changed)

        # Automatic
        at = lp.automatic_tab
        at.fit_clicked.connect(self.auto_ctrl.on_auto_fit)
        at.stop_clicked.connect(self.auto_ctrl.on_auto_stop)
        at.clear_clicked.connect(self.auto_ctrl.on_auto_clear)

        # Post processing
        pp = lp.post_processing
        pp.export_r_data_clicked.connect(self.export_ctrl.on_export_r_data)
        pp.export_rof_t_clicked.connect(self.export_ctrl.on_export_rof_t)

        # ROI selection from image panel
        self.w.original_panel.roi_selected.connect(self.pretune_ctrl.on_roi_selected)
