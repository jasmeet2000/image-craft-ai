"""History service — handles saving generated images and metadata to disk.

This service is responsible for persisting GenerationResult objects
to the configured image_output_dir with proper compression settings.
"""

import logging
from datetime import datetime
from pathlib import Path

from src.config.settings import get_settings
from src.models.generation import GenerationResult

logger = logging.getLogger(__name__)


class HistoryService:
    """Handles persistence of generation results."""

    def __init__(self) -> None:
        """Initialize the history service."""
        self._settings = get_settings()
        self._output_dir = self._settings.image_output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_result(self, result: GenerationResult) -> Path:
        """Save a generation result to disk.

        Uses the configured image format and quality settings.

        Args:
            result: The generation result containing the image and metadata.

        Returns:
            The path where the image was saved.
        """
        fmt = self._settings.image_format.lower()
        save_fmt = "jpeg" if fmt == "jpg" else fmt

        # Generate a unique filename: YYYYMMDD_HHMMSS_engine_seed.ext
        try:
            dt = datetime.fromisoformat(result.timestamp)
            time_str = dt.strftime("%Y%m%d_%H%M%S")
        except ValueError:
            # Fallback if timestamp is not standard ISO format
            time_str = result.timestamp.replace(":", "").replace("-", "")[:15]

        engine_prefix = result.engine.split("_")[0]
        filename = f"{time_str}_{engine_prefix}_{result.seed}.{fmt}"
        filepath = self._output_dir / filename

        kwargs = {}
        image = result.image

        if save_fmt in ("jpeg", "webp"):
            kwargs["quality"] = self._settings.image_quality
            # JPEG cannot handle RGBA
            if save_fmt == "jpeg" and image.mode == "RGBA":
                image = image.convert("RGB")

        try:
            image.save(filepath, format=save_fmt.upper(), **kwargs)
            logger.info(
                "Saved image to %s (format=%s, quality=%d)",
                filepath.name,
                fmt,
                self._settings.image_quality if save_fmt in ("jpeg", "webp") else 100,
            )
        except Exception as exc:
            logger.error("Failed to save image %s: %s", filepath, exc)

        return filepath
