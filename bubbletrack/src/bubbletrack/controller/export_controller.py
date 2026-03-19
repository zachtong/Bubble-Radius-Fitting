"""ExportController — pixel-data and physical-data export."""

from __future__ import annotations

import logging
import os
from datetime import datetime

from PyQt6.QtWidgets import QFileDialog

from bubbletrack.controller.base import BaseController
from bubbletrack.event_bus import EventBus
from bubbletrack.model.export import export_r_data, export_rof_t_data

logger = logging.getLogger(__name__)


class ExportController(BaseController):
    """Handles exporting radius data to .mat files."""

    # -- public handlers -------------------------------------------------- #

    def on_export_r_data(self) -> None:
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        default = os.path.join(
            self._default_export_dir(), self._default_filename("R_data"),
        )
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Pixel Data", default,
            "MAT Files (*.mat);;All Files (*)",
        )
        if not path:
            return  # user cancelled

        try:
            export_r_data(
                path,
                self.state.radius,
                self.state.circle_fit_par,
                self.state.circle_xy,
            )
            logger.info("Export: %s", path)
            pp.set_status(f"Exported: {os.path.basename(path)}", True)
        except Exception as exc:
            pp.set_status(f"Error: {exc}", False)

    def on_export_rof_t(self) -> None:
        pp = self.w.left_panel.post_processing
        if self.state.radius is None:
            pp.set_status("No data to export", False)
            return

        default = os.path.join(
            self._default_export_dir(), self._default_filename("RofT_data"),
        )
        path, _ = QFileDialog.getSaveFileName(
            self.w, "Export Physical Data", default,
            "MAT Files (*.mat);;All Files (*)",
        )
        if not path:
            return  # user cancelled

        try:
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

    def _default_export_dir(self) -> str:
        """Return the image folder as default export directory, or home."""
        return self.state.folder_path or os.path.expanduser("~")

    @staticmethod
    def _default_filename(prefix: str, ext: str = ".mat") -> str:
        """Generate a timestamped filename like ``R_data_20260319_143012.mat``."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{ts}{ext}"
