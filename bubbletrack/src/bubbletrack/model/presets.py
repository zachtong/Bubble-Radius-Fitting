"""Named parameter presets stored as JSON files in ~/.bubbletrack/presets/.

Each preset is a single JSON file whose stem is the preset name.  This
module provides CRUD helpers for managing presets from the config layer
(independent of any particular UI widget).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PRESETS_DIR: Path = Path.home() / ".bubbletrack" / "presets"


def save_preset(name: str, params: dict[str, Any]) -> Path:
    """Write *params* to ``PRESETS_DIR / {name}.json`` and return the path.

    Creates the presets directory if it does not exist.
    Raises ``ValueError`` if *name* is empty or contains path separators.
    """
    _validate_name(name)
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    path = PRESETS_DIR / f"{name}.json"
    # Convert tuples to lists for JSON serialisation
    data: dict[str, Any] = {}
    for key, value in params.items():
        data[key] = list(value) if isinstance(value, tuple) else value
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Preset '%s' saved to %s", name, path)
    return path


def load_preset(name: str) -> dict[str, Any]:
    """Load and return the parameter dict for the named preset.

    Raises ``FileNotFoundError`` if the preset does not exist.
    Raises ``json.JSONDecodeError`` if the file is not valid JSON.
    """
    _validate_name(name)
    path = PRESETS_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def list_presets() -> list[str]:
    """Return a sorted list of available preset names (without extension)."""
    if not PRESETS_DIR.exists():
        return []
    return sorted(p.stem for p in PRESETS_DIR.glob("*.json"))


def delete_preset(name: str) -> None:
    """Delete the named preset file.  No-op if the file does not exist."""
    _validate_name(name)
    (PRESETS_DIR / f"{name}.json").unlink(missing_ok=True)
    logger.info("Preset '%s' deleted", name)


# ------------------------------------------------------------------ #
#  Internal helpers
# ------------------------------------------------------------------ #

def _validate_name(name: str) -> None:
    """Raise ``ValueError`` for invalid preset names."""
    if not name or not name.strip():
        raise ValueError("Preset name must not be empty")
    if "/" in name or "\\" in name:
        raise ValueError(f"Preset name must not contain path separators: {name!r}")
