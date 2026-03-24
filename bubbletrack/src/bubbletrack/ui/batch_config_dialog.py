"""Dialog for configuring batch multi-folder processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from bubbletrack.model.constants import (
    DEFAULT_FPS,
    DEFAULT_RMAX_FIT_LENGTH,
    DEFAULT_UM2PX,
)


@dataclass(frozen=True)
class BatchConfig:
    """User-confirmed batch processing configuration."""

    folders: list[Path]
    export_physical: bool = False
    fps: float = DEFAULT_FPS
    um2px: float = DEFAULT_UM2PX
    rmax_fit_length: int = DEFAULT_RMAX_FIT_LENGTH


class BatchConfigDialog(QDialog):
    """Modal dialog for reviewing folders and setting batch export options.

    Layout
    ------
    - Scrollable folder list
    - Always exports R_data.mat (pixel data)
    - Optional checkbox to also export RofT_data.mat (physical data)
      - FPS, um/px, and Rmax Fit Length inputs appear when checked
    - Start / Cancel buttons
    """

    def __init__(
        self,
        folders: list[Path],
        *,
        default_fps: float = DEFAULT_FPS,
        default_um2px: float = DEFAULT_UM2PX,
        default_fit_length: int = DEFAULT_RMAX_FIT_LENGTH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._folders = folders
        self.setWindowTitle("Batch Multi-Folder Processing")
        self.setMinimumWidth(420)
        self._build_ui(default_fps, default_um2px, default_fit_length)

    def _build_ui(
        self,
        default_fps: float,
        default_um2px: float,
        default_fit_length: int,
    ) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # -- Folder list --
        layout.addWidget(QLabel(f"Found {len(self._folders)} experiment folder(s):"))

        self._folder_list = QListWidget()
        self._folder_list.setMaximumHeight(160)
        for f in self._folders:
            self._folder_list.addItem(f.name)
        layout.addWidget(self._folder_list)

        # -- Export options --
        pixel_lbl = QLabel("Pixel Data (R_data.mat) will be exported to each folder.")
        pixel_lbl.setObjectName("dimText")
        pixel_lbl.setWordWrap(True)
        layout.addWidget(pixel_lbl)

        # Physical data checkbox
        self._phys_check = QCheckBox("Also export Physical Data (RofT_data.mat)")
        self._phys_check.toggled.connect(self._on_phys_toggled)
        layout.addWidget(self._phys_check)

        # Physical data parameters (hidden by default)
        self._phys_group = QWidget()
        phys_layout = QVBoxLayout(self._phys_group)
        phys_layout.setContentsMargins(20, 0, 0, 0)
        phys_layout.setSpacing(6)

        note = QLabel("These values apply to all folders (same camera setup):")
        note.setObjectName("dimText")
        note.setWordWrap(True)
        phys_layout.addWidget(note)

        # FPS row
        fps_row = QHBoxLayout()
        fps_row.addWidget(QLabel("FPS:"))
        self._fps_spin = QDoubleSpinBox()
        self._fps_spin.setRange(0.01, 100_000_000)
        self._fps_spin.setDecimals(0)
        self._fps_spin.setValue(default_fps)
        self._fps_spin.setMinimumWidth(120)
        fps_row.addWidget(self._fps_spin)
        fps_row.addStretch()
        phys_layout.addLayout(fps_row)

        # um/px row
        um_row = QHBoxLayout()
        um_row.addWidget(QLabel("µm/px:"))
        self._um_spin = QDoubleSpinBox()
        self._um_spin.setRange(0.001, 10000)
        self._um_spin.setDecimals(3)
        self._um_spin.setValue(default_um2px)
        self._um_spin.setMinimumWidth(120)
        um_row.addWidget(self._um_spin)
        um_row.addStretch()
        phys_layout.addLayout(um_row)

        # Rmax fit length row
        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Rmax Fit Length:"))
        self._fit_spin = QSpinBox()
        self._fit_spin.setRange(3, 101)
        self._fit_spin.setSingleStep(2)
        self._fit_spin.setValue(default_fit_length)
        self._fit_spin.setMinimumWidth(80)
        fit_row.addWidget(self._fit_spin)
        fit_row.addStretch()
        phys_layout.addLayout(fit_row)

        self._phys_group.hide()
        layout.addWidget(self._phys_group)

        # -- Buttons --
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        start_btn = QPushButton("Start Batch")
        start_btn.clicked.connect(self.accept)
        start_btn.setDefault(True)
        btn_row.addWidget(start_btn)

        layout.addLayout(btn_row)

    def _on_phys_toggled(self, checked: bool) -> None:
        self._phys_group.setVisible(checked)
        self.adjustSize()

    def get_config(self) -> BatchConfig:
        """Return the user-confirmed configuration."""
        return BatchConfig(
            folders=list(self._folders),
            export_physical=self._phys_check.isChecked(),
            fps=self._fps_spin.value(),
            um2px=self._um_spin.value(),
            rmax_fit_length=self._fit_spin.value(),
        )
