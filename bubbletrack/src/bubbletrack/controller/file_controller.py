"""FileController — folder/video loading, frame navigation, tab switching."""

from __future__ import annotations

import logging
import os

from bubbletrack.controller.base import BaseController
from bubbletrack.controller.display_mixin import display_frame
from bubbletrack.event_bus import EventBus
from bubbletrack.model.cache import ImageCache
from bubbletrack.model.conventions import frame_to_display
from bubbletrack.model.image_io import (
    VideoFrameReader,
    detect_bit_depth,
    load_and_normalize,
    normalize_frame,
    scan_folder,
)
from bubbletrack.model.state import update_state

logger = logging.getLogger(__name__)


class FileController(BaseController):
    """Handles folder selection, frame navigation, and tab switching."""

    def __init__(self, bus: EventBus, get_state, set_state, window,
                 set_max_radius, cache: ImageCache | None = None) -> None:
        super().__init__(bus, get_state, set_state, window)
        self._set_max_radius = set_max_radius
        self._cache = cache

    # -- public handlers -------------------------------------------------- #

    def on_folder_selected(self, folder: str) -> None:
        # Close any previous video reader
        if self.state.video_reader is not None:
            self.state.video_reader.close()
            self._update(video_reader=None, video_path="")

        images = scan_folder(folder)
        if not images:
            self.w.header.set_status("No images found", "#ef4444")
            return

        logger.info("Loaded %d images from %s", len(images), folder)

        self._update(
            folder_path=folder,
            images=tuple(images),
            image_no=0,
            img_grayscale_max=detect_bit_depth(images[0]),
        )
        self.state = self.state.with_results_initialized(len(images))

        # Set default ROI to full image
        first_img, _, _, _ = load_and_normalize(images[0], 0.5, (1, 99999), (1, 99999))
        h, w = first_img.shape
        self._update(gridx=(1, h), gridy=(1, w))
        self._set_max_radius(float(max(h, w)))

        # Update UI
        lp = self.w.left_panel
        lp.image_source.set_info(f"{len(images)} images  |  {os.path.basename(images[0])}")
        lp.pretune_tab.set_roi(self.state.gridx, self.state.gridy)
        lp.pretune_tab.set_frame_range(len(images))
        lp.manual_tab.set_frame_range(len(images))
        lp.automatic_tab.set_range(len(images))
        self.w.frame_scrubber.set_range(len(images))
        self.w.radius_chart.set_total_frames(len(images))
        self.w.status_bar.update_frame(frame_to_display(0), len(images))
        self.w.status_bar.update_format(os.path.splitext(images[0])[1])
        self.w.header.set_status("Ready", "#10b981")

        display_frame(self.state, self.w, 0, self._set_state, self._cache)

    def on_video_selected(self, video_path: str) -> None:
        """Open a video file and set up virtual frame list."""
        # Close any previous video reader
        if self.state.video_reader is not None:
            self.state.video_reader.close()

        try:
            reader = VideoFrameReader(video_path)
        except Exception as exc:
            self.w.header.set_status(f"Cannot open video: {exc}", "#ef4444")
            return

        n = reader.total_frames
        if n == 0:
            self.w.header.set_status("Video has no frames", "#ef4444")
            reader.close()
            return

        logger.info("Opened video %s: %d frames, %.1f fps", video_path, n, reader.fps)

        # Generate virtual image paths ("video:<idx>") for the frame list.
        # These are never used as file paths — they serve as identifiers in
        # state.images so the rest of the pipeline (scrubber, chart, etc.)
        # still sees a frame list of the correct length.
        virtual_images = tuple(f"video:{i}" for i in range(n))

        self._update(
            video_path=video_path,
            video_reader=reader,
            folder_path=os.path.dirname(video_path),
            images=virtual_images,
            image_no=0,
            img_grayscale_max=255,  # video frames are typically 8-bit
        )
        self.state = self.state.with_results_initialized(n)

        # Read first frame to determine dimensions and set default ROI
        first_raw = reader.read_frame(0)
        first_img, _, _, _ = normalize_frame(
            first_raw, 0.5, (1, 99999), (1, 99999),
        )
        h, w = first_img.shape
        self._update(gridx=(1, h), gridy=(1, w))
        self._set_max_radius(float(max(h, w)))

        # If the video has a valid FPS, store it in state
        if reader.fps > 0:
            self._update(fps=reader.fps)

        # Update UI
        lp = self.w.left_panel
        basename = os.path.basename(video_path)
        lp.image_source.set_info(
            f"{n} frames  |  {basename}  |  {reader.fps:.1f} fps"
        )
        lp.pretune_tab.set_roi(self.state.gridx, self.state.gridy)
        lp.pretune_tab.set_frame_range(n)
        lp.manual_tab.set_frame_range(n)
        lp.automatic_tab.set_range(n)
        self.w.frame_scrubber.set_range(n)
        self.w.radius_chart.set_total_frames(n)
        self.w.status_bar.update_frame(frame_to_display(0), n)
        self.w.status_bar.update_format(os.path.splitext(video_path)[1])
        self.w.header.set_status("Ready (video)", "#10b981")

        display_frame(self.state, self.w, 0, self._set_state, self._cache)

    def on_frame_changed(self, idx: int) -> None:
        self._update(image_no=idx)
        display_frame(self.state, self.w, idx, self._set_state, self._cache)
        # Sync tab frame spinboxes
        self.w.left_panel.pretune_tab.set_frame_value(idx)
        self.w.left_panel.manual_tab.set_frame_value(idx)

    def on_tab_frame_selected(self, idx: int) -> None:
        """Frame selected from a tab's frame spinbox."""
        if not self.state.images or idx < 0 or idx >= len(self.state.images):
            return
        self._update(image_no=idx)
        self.w.frame_scrubber.set_value(idx)
        self.w.left_panel.pretune_tab.set_frame_value(idx)
        self.w.left_panel.manual_tab.set_frame_value(idx)
        display_frame(self.state, self.w, idx, self._set_state, self._cache)

    def on_tab_changed(self, idx: int) -> None:
        """Tab bar switched — exit interactive modes, update status."""
        self.w.original_panel.set_mode("normal")
        self.w.left_panel.manual_tab.reset()
        tab_names = ("Pre-tune", "Manual", "Automatic")
        self.w.status_bar.update_mode(tab_names[idx] if idx < len(tab_names) else "")
        self.bus.emit("tab_changed", idx)
