"""Batch Results Browser — non-modal dialog for inspecting batch results."""

from __future__ import annotations

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bubbletrack.model.batch_result import BatchResultStore
from bubbletrack.model.constants import QUALITY_GOOD_THRESHOLD, QUALITY_WARN_THRESHOLD
from bubbletrack.ui.radius_chart import RadiusChart


class BatchResultsBrowserDialog(QDialog):
    """Non-modal dialog showing all batch folder results with R-t preview.

    Signals
    -------
    load_folder_requested(str)
        Emitted with the folder path when user clicks "Load into Main View".
    """

    # Emits the selected FolderResult when user clicks "Load into Main View"
    load_folder_requested = pyqtSignal(object)

    def __init__(
        self,
        store: BatchResultStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._store = store
        self._selected_result = None  # type: FolderResult | None

        self.setWindowTitle("Batch Results Browser")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)
        # Non-modal: user can interact with main window
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._build_ui()
        self._populate_folder_list()

    # ------------------------------------------------------------------ #
    #  UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Summary header
        n_ok = sum(1 for r in self._store.results if r.success)
        total_fitted = sum(r.n_fitted for r in self._store.results)
        total_frames = sum(r.n_frames for r in self._store.results)
        self._header = QLabel(
            f"Batch Results — {n_ok}/{len(self._store.results)} folders, "
            f"{total_fitted}/{total_frames} frames fitted"
        )
        self._header.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._header.setStyleSheet("color: #e4e4e7; padding: 4px 0;")
        root.addWidget(self._header)

        # Splitter: folder list (left) + chart preview (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        # -- Left: folder list ----------------------------------------- #
        self._folder_list = QListWidget()
        self._folder_list.setMinimumWidth(220)
        self._folder_list.setMaximumWidth(350)
        self._folder_list.setFont(QFont("Segoe UI", 10))
        self._folder_list.currentRowChanged.connect(self._on_folder_clicked)
        splitter.addWidget(self._folder_list)

        # -- Right: detail + chart + load button ----------------------- #
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(6)

        self._detail_label = QLabel("Select a folder to preview results.")
        self._detail_label.setFont(QFont("Segoe UI", 10))
        self._detail_label.setStyleSheet("color: #a1a1aa;")
        self._detail_label.setWordWrap(True)
        right_layout.addWidget(self._detail_label)

        # Read-only RadiusChart preview (no signals connected)
        self._chart = RadiusChart(parent=right_panel)
        right_layout.addWidget(self._chart, stretch=1)

        self._load_btn = QPushButton("Load into Main View")
        self._load_btn.setObjectName("primaryBtn")
        self._load_btn.setFixedHeight(36)
        self._load_btn.setEnabled(False)
        self._load_btn.setStyleSheet(
            "QPushButton { background: #6366f1; color: white; border-radius: 6px; "
            "font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #818cf8; }"
            "QPushButton:disabled { background: #3f3f46; color: #71717a; }"
        )
        self._load_btn.clicked.connect(self._on_load_clicked)
        right_layout.addWidget(self._load_btn)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # folder list
        splitter.setStretchFactor(1, 3)  # chart panel

        root.addWidget(splitter, stretch=1)

        # Bottom close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setFixedHeight(32)
        close_btn.clicked.connect(self.close)
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        bottom_row.addWidget(close_btn)
        root.addLayout(bottom_row)

    # ------------------------------------------------------------------ #
    #  Folder list population
    # ------------------------------------------------------------------ #

    def _populate_folder_list(self) -> None:
        for result in self._store.results:
            avg_q = self._avg_quality(result)
            item_text = (
                f"{result.folder_name}\n"
                f"{result.n_fitted}/{result.n_frames} fitted · "
                f"Avg Q: {avg_q:.0%}"
            )
            item = QListWidgetItem(item_text)
            item.setFont(QFont("Segoe UI", 9))

            # Color-code by average quality
            if not result.success:
                item.setForeground(QColor("#71717a"))  # gray
                item.setBackground(QColor(113, 113, 122, 20))
            elif avg_q >= QUALITY_GOOD_THRESHOLD:
                item.setForeground(QColor("#d4d4d8"))
                item.setBackground(QColor(16, 185, 129, 25))  # green tint
            elif avg_q >= QUALITY_WARN_THRESHOLD:
                item.setForeground(QColor("#d4d4d8"))
                item.setBackground(QColor(245, 158, 11, 25))  # amber tint
            else:
                item.setForeground(QColor("#d4d4d8"))
                item.setBackground(QColor(239, 68, 68, 25))   # red tint

            self._folder_list.addItem(item)

    # ------------------------------------------------------------------ #
    #  Event handlers
    # ------------------------------------------------------------------ #

    def _on_folder_clicked(self, row: int) -> None:
        if row < 0 or row >= len(self._store.results):
            return
        result = self._store.results[row]
        frames = np.arange(1, result.n_frames + 1)
        self._chart.set_total_frames(result.n_frames)
        self._chart.plot_all(frames, result.radius, result.quality_scores)

        avg_q = self._avg_quality(result)
        self._detail_label.setText(
            f"Path: {result.folder_path}\n"
            f"Fitted: {result.n_fitted}/{result.n_frames} frames\n"
            f"Avg Quality: {avg_q:.0%}"
        )
        self._detail_label.setStyleSheet("color: #e4e4e7;")
        self._load_btn.setEnabled(True)
        self._selected_result = result

    def _on_load_clicked(self) -> None:
        if self._selected_result is not None:
            self.load_folder_requested.emit(self._selected_result)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _avg_quality(result) -> float:
        """Average quality score over fitted frames only."""
        valid = result.radius > 0
        if not np.any(valid):
            return 0.0
        return float(np.mean(result.quality_scores[valid]))
