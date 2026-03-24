"""Process multiple experiment folders with the same parameters."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".tiff", ".tif", ".png", ".jpg", ".jpeg", ".bmp"}


def find_experiment_folders(root: str) -> list[Path]:
    """Find all subfolders of *root* that contain image files.

    Only immediate children of *root* are checked (no recursive descent).
    Hidden directories (names starting with ``"."``) are skipped.

    Parameters
    ----------
    root : str
        Path to the parent directory containing experiment subfolders.

    Returns
    -------
    Sorted list of ``Path`` objects for folders that contain at least one
    image file with a supported extension.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        return []
    folders: list[Path] = []
    for d in sorted(root_path.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            if any(
                f.suffix.lower() in _IMAGE_EXTS
                for f in d.iterdir()
                if f.is_file()
            ):
                folders.append(d)
    return folders


def batch_process_experiments(
    folders: list[Path],
    process_folder_fn: Callable[[Path], dict[str, Any]],
    callback: Callable[[int, int], None] | None = None,
) -> dict[str, dict[str, Any]]:
    """Process each folder as an independent experiment.

    Parameters
    ----------
    folders : list of Path
        Directories to process.
    process_folder_fn : callable(folder_path) -> result dict
        Must return ``{"success": True, "n_frames": int, "output": str}`` on
        success, or ``{"success": False, "error": str}`` on failure.
    callback : optional
        Progress callback invoked as ``callback(current, total)`` after each
        folder is processed.

    Returns
    -------
    dict mapping ``folder_name`` -> result dict
    """
    results: dict[str, dict[str, Any]] = {}
    for i, folder in enumerate(folders):
        try:
            result = process_folder_fn(folder)
            results[folder.name] = result
        except Exception as exc:
            logger.error("Failed to process %s: %s", folder.name, exc)
            results[folder.name] = {"success": False, "error": str(exc)}
        if callback:
            callback(i + 1, len(folders))
    return results
