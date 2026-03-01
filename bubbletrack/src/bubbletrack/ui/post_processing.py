"""Post-processing panel: export controls, FPS / scale inputs."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from bubbletrack.ui.widgets import CollapsibleSection


class PostProcessing(QWidget):
    """Collapsible export panel with FPS, scale, fit-length inputs."""

    export_r_data_clicked = pyqtSignal()
    export_rof_t_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("Post Processing", collapsed=True)

        grid = QGridLayout()
        grid.setSpacing(6)

        # Save path
        grid.addWidget(QLabel("Save Path:"), 0, 0)
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Select output folder...")
        self._path_edit.setReadOnly(True)
        grid.addWidget(self._path_edit, 0, 1)
        self._browse_btn = QPushButton("...")
        self._browse_btn.setFixedWidth(32)
        self._browse_btn.setObjectName("secondaryBtn")
        self._browse_btn.clicked.connect(self._browse)
        grid.addWidget(self._browse_btn, 0, 2)

        # FPS with unit selector
        grid.addWidget(QLabel("FPS:"), 1, 0)
        self._fps_spin = QDoubleSpinBox()
        self._fps_spin.setRange(0.001, 99999)
        self._fps_spin.setDecimals(1)
        self._fps_spin.setValue(10)
        grid.addWidget(self._fps_spin, 1, 1)
        self._fps_unit = QComboBox()
        self._fps_unit.addItems(["Hz", "k", "M"])
        self._fps_unit.setCurrentIndex(2)  # default M
        grid.addWidget(self._fps_unit, 1, 2)

        # um/px
        grid.addWidget(QLabel("\u00b5m/px:"), 2, 0)
        self._scale_spin = QDoubleSpinBox()
        self._scale_spin.setRange(0.001, 9999)
        self._scale_spin.setDecimals(3)
        self._scale_spin.setValue(3.2)
        grid.addWidget(self._scale_spin, 2, 1, 1, 2)

        # Rmax fit length
        grid.addWidget(QLabel("Rmax Fit:"), 3, 0)
        self._fit_len_spin = QSpinBox()
        self._fit_len_spin.setRange(3, 999)
        self._fit_len_spin.setSingleStep(2)
        self._fit_len_spin.setValue(11)
        grid.addWidget(self._fit_len_spin, 3, 1, 1, 2)

        container = QWidget()
        container.setLayout(grid)
        section.add_widget(container)

        # Export buttons
        btn_row = QHBoxLayout()
        self._export_r_btn = QPushButton("Export R_data")
        self._export_r_btn.clicked.connect(self.export_r_data_clicked)
        btn_row.addWidget(self._export_r_btn)

        self._export_rt_btn = QPushButton("Export R(t)")
        self._export_rt_btn.clicked.connect(self.export_rof_t_clicked)
        btn_row.addWidget(self._export_rt_btn)

        btn_container = QWidget()
        btn_container.setLayout(btn_row)
        section.add_widget(btn_container)

        # Status label
        self._status = QLabel("")
        self._status.setObjectName("dimText")
        section.add_widget(self._status)

        layout.addWidget(section)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self._path_edit.setText(folder)

    def get_save_path(self) -> str:
        return self._path_edit.text()

    def get_fps(self) -> float:
        multipliers = {"Hz": 1, "k": 1_000, "M": 1_000_000}
        unit = self._fps_unit.currentText()
        return self._fps_spin.value() * multipliers.get(unit, 1)

    def get_scale(self) -> float:
        return self._scale_spin.value()

    def get_fit_length(self) -> int:
        return self._fit_len_spin.value()

    def set_status(self, text: str, success: bool = True):
        colour = "#22C55E" if success else "#EF4444"
        self._status.setStyleSheet(f"color:{colour}; font-size:11px;")
        self._status.setText(text)
