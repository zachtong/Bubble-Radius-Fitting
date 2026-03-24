"""Frame scrubber — horizontal slider with frame counter."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QSpinBox, QWidget


class FrameScrubber(QWidget):
    """``[< ] ====o==== [> ]  Frame: 1/100``."""

    value_changed = pyqtSignal(int)  # 0-indexed frame number

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Prev button
        self._prev = _NavButton("\u23EA")
        self._prev.clicked.connect(self._step_back)
        layout.addWidget(self._prev)

        # Play/pause button
        self._play_btn = _NavButton("\u25B6")
        self._play_btn.clicked.connect(lambda _checked: self.toggle_play())
        layout.addWidget(self._play_btn)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(0)
        self._slider.valueChanged.connect(self._on_slider)
        layout.addWidget(self._slider, 1)

        # Next button
        self._next = _NavButton("\u23E9")
        self._next.clicked.connect(self._step_forward)
        layout.addWidget(self._next)

        # FPS control
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(1, 60)
        self._fps_spin.setValue(10)
        self._fps_spin.setSuffix(" fps")
        self._fps_spin.setFixedWidth(72)
        self._fps_spin.valueChanged.connect(self._on_fps_changed)
        layout.addWidget(self._fps_spin)

        # Frame label
        self._label = QLabel("Frame: --/--")
        self._label.setFixedWidth(100)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        # Playback timer
        self._play_timer = QTimer()
        self._play_timer.setInterval(100)  # 1000 / 10 fps
        self._play_timer.timeout.connect(self._play_tick)
        self._playing = False

    def set_range(self, total: int):
        self._slider.setMaximum(max(total - 1, 0))
        self._update_label()

    def set_value(self, idx: int):
        self._slider.setValue(idx)

    def value(self) -> int:
        return self._slider.value()

    def _on_slider(self, v: int):
        self._update_label()
        self.value_changed.emit(v)

    def _step_back(self):
        self._slider.setValue(max(self._slider.value() - 1, 0))

    def _step_forward(self):
        self._slider.setValue(min(self._slider.value() + 1, self._slider.maximum()))

    # -- Playback controls --

    def toggle_play(self) -> None:
        """Toggle play/pause — public method for shortcut binding."""
        if self._playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self) -> None:
        # If at the end, wrap to start
        if self._slider.value() >= self._slider.maximum():
            self._slider.setValue(0)
        self._playing = True
        self._play_btn.setText("\u23F8")  # ⏸
        self._play_timer.setInterval(max(1, 1000 // self._fps_spin.value()))
        self._play_timer.start()

    def _stop_play(self) -> None:
        self._playing = False
        self._play_timer.stop()
        self._play_btn.setText("\u25B6")  # ▶

    def _play_tick(self) -> None:
        nxt = self._slider.value() + 1
        if nxt > self._slider.maximum():
            self._stop_play()
            return
        self._slider.setValue(nxt)

    def _on_fps_changed(self, fps: int) -> None:
        if self._playing:
            self._play_timer.setInterval(max(1, 1000 // fps))

    def _update_label(self):
        cur = self._slider.value() + 1  # 1-indexed display
        total = self._slider.maximum() + 1
        self._label.setText(f"Frame: {cur}/{total}")


class _NavButton(QWidget):
    """Tiny navigation arrow button."""

    def __new__(cls, text: str):
        btn = QPushButton(text)
        btn.setFixedSize(32, 28)
        btn.setObjectName("secondaryBtn")
        return btn
