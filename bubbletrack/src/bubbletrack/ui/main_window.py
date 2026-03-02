"""Main application window — assembles all panels."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QSizePolicy,
)

from bubbletrack.ui.header_bar import HeaderBar
from bubbletrack.ui.status_bar import StatusBar
from bubbletrack.ui.left_panel import LeftPanel
from bubbletrack.ui.image_panel import ImagePanel
from bubbletrack.ui.radius_chart import RadiusChart
from bubbletrack.ui.frame_scrubber import FrameScrubber


class MainWindow(QMainWindow):
    """Top-level window following the Figma 3-panel design."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bubble Radius Fitting")
        self.setMinimumSize(1280, 960)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        self.header = HeaderBar()
        root.addWidget(self.header)

        # Main body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Left sidebar
        self.left_panel = LeftPanel()
        body.addWidget(self.left_panel)

        # Sidebar toggle
        self._sidebar_toggle = QPushButton("\u25C0")
        self._sidebar_toggle.setObjectName("sidebarToggle")
        self._sidebar_toggle.setFixedWidth(20)
        self._sidebar_toggle.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding,
        )
        self._sidebar_toggle.clicked.connect(self._toggle_sidebar)
        body.addWidget(self._sidebar_toggle)

        # Right content area
        right = QVBoxLayout()
        right.setContentsMargins(12, 12, 12, 8)
        right.setSpacing(8)

        # Image viewers row
        images_row = QHBoxLayout()
        images_row.setSpacing(8)
        self.original_panel = ImagePanel("Original Image")
        self.binary_panel = ImagePanel("Binary Mask")
        images_row.addWidget(self.original_panel, 1)
        images_row.addWidget(self.binary_panel, 1)
        right.addLayout(images_row, 1)

        # Frame scrubber
        self.frame_scrubber = FrameScrubber()
        right.addWidget(self.frame_scrubber)

        # Radius chart
        self.radius_chart = RadiusChart()
        right.addWidget(self.radius_chart)

        body.addLayout(right, 1)
        root.addLayout(body, 1)

        # Status bar
        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)

    def _toggle_sidebar(self):
        visible = self.left_panel.isVisible()
        self.left_panel.setVisible(not visible)
        self._sidebar_toggle.setText("\u25B6" if visible else "\u25C0")
