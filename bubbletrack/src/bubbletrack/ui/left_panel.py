"""Left sidebar panel — assembles image source, tabs, and post-processing."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QScrollArea, QStackedWidget, QVBoxLayout, QWidget, QSizePolicy,
)

from bubbletrack.ui.image_source import ImageSource
from bubbletrack.ui.tab_bar import TabBar
from bubbletrack.ui.pretune_tab import PreTuneTab
from bubbletrack.ui.manual_tab import ManualTab
from bubbletrack.ui.automatic_tab import AutomaticTab
from bubbletrack.ui.post_processing import PostProcessing


class LeftPanel(QWidget):
    """300-px-wide collapsible sidebar."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("LeftPanel")
        self.setFixedWidth(300)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Sections
        self.image_source = ImageSource()
        layout.addWidget(self.image_source)

        self.tab_bar = TabBar()
        layout.addWidget(self.tab_bar)

        # Stacked tabs
        self._stack = QStackedWidget()
        self.pretune_tab = PreTuneTab()
        self.manual_tab = ManualTab()
        self.automatic_tab = AutomaticTab()
        self._stack.addWidget(self.pretune_tab)
        self._stack.addWidget(self.manual_tab)
        self._stack.addWidget(self.automatic_tab)
        layout.addWidget(self._stack)

        self.tab_bar.tab_changed.connect(self._stack.setCurrentIndex)

        # Post processing
        self.post_processing = PostProcessing()
        layout.addWidget(self.post_processing)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
