"""QGraphicsView-based image viewer with overlay support."""

from __future__ import annotations

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF

from bubbletrack.model.conventions import roi_to_slice
from PyQt6.QtGui import (
    QImage, QPixmap, QPen, QColor, QBrush, QWheelEvent, QMouseEvent,
)
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsEllipseItem, QGraphicsRectItem, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QWidget, QSizePolicy,
)


class ImagePanel(QWidget):
    """Image viewer with zoom controls and overlay items.

    Signals
    -------
    point_clicked(float, float)
        Emitted in *point-select* mode with scene (x, y) = (col, row).
    roi_selected(int, int, int, int)
        Emitted when rubber-band ROI selection finishes: (r0, r1, c0, c1) 1-indexed.
    """

    point_clicked = pyqtSignal(float, float)
    roi_selected = pyqtSignal(int, int, int, int)
    select_roi_clicked = pyqtSignal()

    def __init__(self, title: str = "Image", parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Title bar with zoom buttons
        top = QHBoxLayout()
        top.setContentsMargins(8, 4, 8, 0)
        lbl = QLabel(title)
        lbl.setObjectName("sectionTitle")
        top.addWidget(lbl)
        top.addStretch()

        # ROI button + coordinate label
        self._roi_label = QLabel("")
        self._roi_label.setObjectName("dimText")
        self._roi_label.setStyleSheet("font-size: 11px;")
        top.addWidget(self._roi_label)

        self._select_roi_btn = QPushButton("ROI")
        self._select_roi_btn.setFixedSize(42, 28)
        self._select_roi_btn.setObjectName("secondaryBtn")
        self._select_roi_btn.setToolTip("Drag on image to select Region of Interest")
        self._select_roi_btn.clicked.connect(self.select_roi_clicked)
        top.addWidget(self._select_roi_btn)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setFixedSize(28, 28)
        self._zoom_in_btn.setObjectName("secondaryBtn")
        self._zoom_in_btn.clicked.connect(self._zoom_in)
        top.addWidget(self._zoom_in_btn)

        self._zoom_out_btn = QPushButton("\u2212")
        self._zoom_out_btn.setFixedSize(28, 28)
        self._zoom_out_btn.setObjectName("secondaryBtn")
        self._zoom_out_btn.clicked.connect(self._zoom_out)
        top.addWidget(self._zoom_out_btn)

        self._zoom_reset_btn = QPushButton("\u21BA")
        self._zoom_reset_btn.setFixedSize(28, 28)
        self._zoom_reset_btn.setObjectName("secondaryBtn")
        self._zoom_reset_btn.clicked.connect(self._zoom_reset)
        top.addWidget(self._zoom_reset_btn)

        layout.addLayout(top)

        # Graphics view
        self._scene = QGraphicsScene(self)
        self._view = _PanZoomView(self._scene, self)
        self._view.setStyleSheet("border:1px solid rgba(255,255,255,0.06); border-radius:8px; background:#0c0d12;")
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._view)

        # State
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._overlay_items: list = []
        self._mode = "normal"  # "normal" | "point" | "roi"

    # -- Public API --

    def set_image(self, img: np.ndarray):
        """Display a greyscale or binary image (float [0,1] or bool)."""
        if img.dtype == bool:
            img8 = (img.astype(np.uint8)) * 255
        elif img.dtype in (np.float32, np.float64):
            img8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        else:
            img8 = img.astype(np.uint8)

        h, w = img8.shape[:2]
        qimg = QImage(img8.data.tobytes(), w, h, w, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        self.clear_overlays()
        if self._pixmap_item is not None:
            self._scene.removeItem(self._pixmap_item)
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._scene.setSceneRect(QRectF(0, 0, w, h))
        self._view.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_image_rgb(self, img: np.ndarray):
        """Display an RGB image (H, W, 3) uint8.

        Used by overlay / wipe comparison modes that produce colour
        composites from the original grayscale and binary images.
        """
        if img.ndim != 3 or img.shape[2] != 3:
            raise ValueError("set_image_rgb expects an (H, W, 3) array")
        img8 = img.astype(np.uint8)
        h, w = img8.shape[:2]
        bytes_per_line = 3 * w
        qimg = QImage(
            img8.data.tobytes(), w, h, bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(qimg)

        self.clear_overlays()
        if self._pixmap_item is not None:
            self._scene.removeItem(self._pixmap_item)
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._scene.setSceneRect(QRectF(0, 0, w, h))
        self._view.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def draw_circle(self, row_c: float, col_c: float, radius: float,
                    colour: str = "#6366f1", width: float = 2.0):
        """Draw a circle overlay. Coordinates are (row, col) = (y, x)."""
        pen = QPen(QColor(colour), width)
        item = self._scene.addEllipse(
            col_c - radius, row_c - radius, 2 * radius, 2 * radius, pen,
        )
        self._overlay_items.append(item)

    def draw_points(self, points: np.ndarray, colour: str = "#EF4444", size: float = 3.0):
        """Draw scatter points. *points* is (N, 2) ``[row, col]``."""
        pen = QPen(QColor(colour), 0)
        brush = QBrush(QColor(colour))
        for r, c in points:
            item = self._scene.addEllipse(c - size/2, r - size/2, size, size, pen, brush)
            self._overlay_items.append(item)

    def draw_roi_rect(self, gridx: tuple[int, int], gridy: tuple[int, int],
                      colour: str = "#10b981"):
        """Draw an ROI rectangle (1-indexed coords)."""
        pen = QPen(QColor(colour), 2)
        rs, cs = roi_to_slice(gridx, gridy)
        r0, r1 = rs.start, rs.stop
        c0, c1 = cs.start, cs.stop
        item = self._scene.addRect(c0, r0, c1 - c0, r1 - r0, pen)
        self._overlay_items.append(item)

    def clear_overlays(self):
        for item in self._overlay_items:
            self._scene.removeItem(item)
        self._overlay_items.clear()

    def set_mode(self, mode: str):
        """Set interaction mode: 'normal', 'point', or 'roi'.

        | Mode   | Cursor       | Drag              | Border        |
        |--------|-------------|-------------------|---------------|
        | normal | default     | ScrollHandDrag    | subtle border |
        | point  | CrossCursor | NoDrag            | #6366f1 indigo|
        | roi    | CrossCursor | RubberBandDrag    | #f59e0b amber |
        """
        self._mode = mode
        if mode == "roi":
            self._view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self._view.setCursor(Qt.CursorShape.CrossCursor)
            self._view.setStyleSheet("border:2px solid #f59e0b; border-radius:8px; background:#0c0d12;")
        elif mode == "point":
            self._view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self._view.setCursor(Qt.CursorShape.CrossCursor)
            self._view.setStyleSheet("border:2px solid #6366f1; border-radius:8px; background:#0c0d12;")
        else:
            self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self._view.unsetCursor()
            self._view.setStyleSheet("border:1px solid rgba(255,255,255,0.06); border-radius:8px; background:#0c0d12;")

    # -- ROI label --
    def set_roi_text(self, gridx: tuple[int, int], gridy: tuple[int, int]) -> None:
        """Update the ROI coordinate display in the toolbar."""
        self._roi_label.setText(
            f"X: {gridy[0]}\u2013{gridy[1]}  Y: {gridx[0]}\u2013{gridx[1]}"
        )

    # -- Zoom helpers --
    def _zoom_in(self):
        self._view.scale(1.25, 1.25)

    def _zoom_out(self):
        self._view.scale(0.8, 0.8)

    def _zoom_reset(self):
        self._view.resetTransform()
        if self._scene.sceneRect():
            self._view.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class _PanZoomView(QGraphicsView):
    """QGraphicsView with wheel-zoom and pan."""

    def __init__(self, scene, panel: ImagePanel):
        super().__init__(scene)
        self._panel = panel
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setRenderHint(self.renderHints())

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent):
        if (self._panel._mode == "point"
                and event.button() == Qt.MouseButton.LeftButton):
            pos = self.mapToScene(event.pos())
            self._panel.point_clicked.emit(pos.x(), pos.y())  # (col, row) in scene
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._panel._mode == "roi" and self.rubberBandRect():
            rect = self.mapToScene(self.rubberBandRect()).boundingRect()
            r0, r1 = int(rect.top()) + 1, int(rect.bottom()) + 1
            c0, c1 = int(rect.left()) + 1, int(rect.right()) + 1
            self._panel.roi_selected.emit(r0, r1, c0, c1)
            self._panel.set_mode("normal")
        super().mouseReleaseEvent(event)
