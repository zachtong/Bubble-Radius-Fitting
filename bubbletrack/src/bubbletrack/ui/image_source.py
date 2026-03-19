"""Image source panel — folder browser with file count."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QWidget,
)


class ImageSource(QWidget):
    """Folder/video selector that emits the chosen path."""

    folder_selected = pyqtSignal(str)
    video_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        lbl = QLabel("Image Source")
        lbl.setObjectName("sectionTitle")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Select image folder or video...")
        self._path_edit.setReadOnly(True)
        row.addWidget(self._path_edit, 1)

        self._browse_btn = QPushButton("Folder")
        self._browse_btn.setToolTip("Browse for image folder")
        self._browse_btn.clicked.connect(self._browse)
        row.addWidget(self._browse_btn)

        self._browse_video_btn = QPushButton("Video")
        self._browse_video_btn.setToolTip("Browse for video file (AVI, MP4, MOV, MKV)")
        self._browse_video_btn.clicked.connect(self._browse_video)
        row.addWidget(self._browse_video_btn)

        layout.addLayout(row)

        self._info_label = QLabel("")
        self._info_label.setObjectName("dimText")
        layout.addWidget(self._info_label)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self._path_edit.setText(folder)
            self.folder_selected.emit(folder)

    def _browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.avi *.mp4 *.mov *.mkv);;All Files (*)",
        )
        if path:
            self._path_edit.setText(path)
            self.video_selected.emit(path)

    def set_info(self, text: str):
        self._info_label.setText(text)

    def set_path(self, path: str):
        self._path_edit.setText(path)
