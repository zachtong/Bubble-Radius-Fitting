"""ExportController — pixel-data and physical-data export."""

from __future__ import annotations

import logging
import os
from datetime import datetime

from PyQt6.QtWidgets import QFileDialog

from bubbletrack.controller.base import BaseController
from bubbletrack.event_bus import EventBus
from bubbletrack.model.export import (
    export_csv,
    export_excel,
    export_r_data,
    export_rof_t_data,
)

logger = logging.getLogger(__name__)

# File dialog filter strings keyed by format
_FORMAT_FILTERS: dict[str, str] = {
    "mat": "MAT Files (*.mat);;All Files (*)",
    "csv": "CSV Files (*.csv);;All Files (*)",
    "xlsx": "Excel Files (*.xlsx);;All Files (*)",
}

_FORMAT_EXT: dict[str, str] = {
    "mat": ".mat",
    "csv": ".csv",
    "xlsx": ".xlsx",
}


class ExportController(BaseController):
    """Handles exporting radius data to .mat / CSV / Excel files."""

    # -- public handlers -------------------------------------------------- #

    def on_export_r_data(self) -> None:
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        fmt = pp.get_format()
        ext = _FORMAT_EXT.get(fmt, ".mat")
        default = os.path.join(
            self._default_export_dir(),
            self._default_filename("R_data", ext=ext),
        )
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Pixel Data", default,
            _FORMAT_FILTERS.get(fmt, _FORMAT_FILTERS["mat"]),
        )
        if not path:
            return  # user cancelled

        try:
            self._do_export_r_data(path, fmt)
            logger.info("Export: %s", path)
            pp.set_status(f"Exported: {os.path.basename(path)}", True)
        except Exception as exc:
            pp.set_status(f"Error: {exc}", False)

    def on_export_rof_t(self) -> None:
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        fmt = pp.get_format()
        ext = _FORMAT_EXT.get(fmt, ".mat")
        default = os.path.join(
            self._default_export_dir(),
            self._default_filename("RofT_data", ext=ext),
        )
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Physical Data", default,
            _FORMAT_FILTERS.get(fmt, _FORMAT_FILTERS["mat"]),
        )
        if not path:
            return  # user cancelled

        try:
            if fmt in ("csv", "xlsx"):
                self._do_export_r_data(
                    path, fmt,
                    fps=pp.get_fps(),
                    um2px=pp.get_scale(),
                )
                logger.info("Export: %s", path)
                pp.set_status(f"Exported: {os.path.basename(path)}", True)
                self.w.status_bar.update_scale(pp.get_scale())
            else:
                ok, msg = export_rof_t_data(
                    path,
                    self.state.radius,
                    pp.get_scale(),
                    pp.get_fps(),
                    pp.get_fit_length(),
                )
                if ok:
                    logger.info("Export: %s", path)
                    pp.set_status(f"Exported: {os.path.basename(path)}", True)
                    self.w.status_bar.update_scale(pp.get_scale())
                else:
                    pp.set_status(msg, False)
        except Exception as exc:
            pp.set_status(f"Error: {exc}", False)

    # -- private helpers -------------------------------------------------- #

    def _do_export_r_data(
        self,
        path: str,
        fmt: str,
        *,
        fps: float | None = None,
        um2px: float | None = None,
    ) -> None:
        """Dispatch pixel-data export to the correct format handler."""
        if fmt == "csv":
            export_csv(
                path,
                self.state.radius,
                self.state.circle_fit_par,
                fps=fps,
                um2px=um2px,
            )
        elif fmt == "xlsx":
            export_excel(
                path,
                self.state.radius,
                self.state.circle_fit_par,
                fps=fps,
                um2px=um2px,
            )
        else:
            export_r_data(
                path,
                self.state.radius,
                self.state.circle_fit_par,
                self.state.circle_xy,
            )

    def _default_export_dir(self) -> str:
        """Return the image folder as default export directory, or home."""
        return self.state.folder_path or os.path.expanduser("~")

    @staticmethod
    def _default_filename(prefix: str, ext: str = ".mat") -> str:
        """Generate a timestamped filename like ``R_data_20260319_143012.mat``."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{ts}{ext}"
