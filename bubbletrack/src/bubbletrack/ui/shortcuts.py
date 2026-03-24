"""Keyboard shortcuts for BubbleTrack."""

from __future__ import annotations

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget


def setup_shortcuts(window: QWidget, callbacks: dict) -> list[QShortcut]:
    """Register keyboard shortcuts.

    Parameters
    ----------
    window : QWidget
        The top-level widget that owns the shortcuts.
    callbacks : dict
        Maps action names to callables:
        ``"frame_prev"``, ``"frame_next"``, ``"zoom_in"``,
        ``"zoom_out"``, ``"zoom_reset"``, ``"undo"``, ``"play_pause"``.

    Returns
    -------
    list[QShortcut]
        Created shortcuts (caller should keep a reference to prevent GC).
    """
    bindings = {
        "Left": "frame_prev",
        "Right": "frame_next",
        "+": "zoom_in",
        "=": "zoom_in",  # for keyboards without numpad
        "-": "zoom_out",
        "0": "zoom_reset",
        "Ctrl+Z": "undo",
        "Space": "play_pause",
    }
    shortcuts: list[QShortcut] = []
    for key, action in bindings.items():
        if action in callbacks:
            sc = QShortcut(QKeySequence(key), window)
            sc.activated.connect(callbacks[action])
            shortcuts.append(sc)
    return shortcuts
