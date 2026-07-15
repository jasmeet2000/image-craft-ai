"""Image storage service — handles advanced saving and loading of generations.

This service is responsible for persisting GenerationResult objects
to disk with meaningful filenames, date-based folder structures, sidecar JSON
metadata, and embedded PNG metadata. It also provides methods to load
history for the UI.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL.PngImagePlugin import PngInfo

from src.config.settings import get_settings
from src.models.generation import GenerationResult

logger = logging.getLogger(__name__)


class ImageStorageService:
    """Handles advanced persistence and retrieval of generation results."""

    def __init__(self) -> None:
        """Initialize the storage service."""
        self._settings = get_settings()
        self._base_dir = self._settings.image_output_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_slug(self, prompt: str) -> str:
        """Generate a short, filesystem-safe slug from the prompt.

        Args:
            prompt: The text prompt.

        Returns:
            A clean string suitable for a filename (max 40 chars).
        """
        # Replace non-alphanumeric chars with spaces, collapse spaces, replace with hyphen
        slug = re.sub(r"[^\w\s-]", "", prompt.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        if not slug:
            return "unnamed-prompt"
        return slug[:40].strip("-")

    def save_result(self, result: GenerationResult) -> Path:
        """Save a generation result to disk with sidecars and metadata.

        Args:
            result: The generation result to save.

        Returns:
            The path where the image was saved.

        Raises:
            RuntimeError: If saving fails (e.g., disk full, permissions).
        """
        fmt = self._settings.image_format.lower()
        save_fmt = "jpeg" if fmt == "jpg" else fmt

        # Generate date-based directory
        try:
            dt = datetime.fromisoformat(result.timestamp)
        except ValueError:
            dt = datetime.now()

        date_str = dt.strftime("%Y-%m-%d")
        date_dir = self._base_dir / date_str
        
        try:
            date_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(f"Failed to create directory {date_dir}: {exc}") from exc

        # Generate base filename
        time_str = dt.strftime("%Y%m%d_%H%M%S")
        slug = self._generate_slug(result.prompt)
        base_name = f"{time_str}_{slug}_seed{result.seed}"

        # Handle collisions
        filepath = date_dir / f"{base_name}.{fmt}"
        json_path = date_dir / f"{base_name}.json"
        
        counter = 1
        while filepath.exists() or json_path.exists():
            base_name_col = f"{base_name}_{counter}"
            filepath = date_dir / f"{base_name_col}.{fmt}"
            json_path = date_dir / f"{base_name_col}.json"
            counter += 1

        # Write Sidecar JSON
        metadata: dict[str, Any] = {
            "prompt": result.prompt,
            "engine": result.engine,
            "generation_time_s": result.generation_time,
            "timestamp": result.timestamp,
            "seed": result.seed,
            "parameters": result.parameters,
        }
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except OSError as exc:
            raise RuntimeError(f"Failed to write metadata JSON: {exc}") from exc

        # Prepare Image Saving
        kwargs: dict[str, Any] = {}
        image = result.image

        if save_fmt in ("jpeg", "webp"):
            kwargs["quality"] = self._settings.image_quality
            if save_fmt == "jpeg" and image.mode == "RGBA":
                image = image.convert("RGB")
        elif save_fmt == "png":
            # Embed metadata into PNG directly
            png_info = PngInfo()
            png_info.add_text("prompt", result.prompt)
            png_info.add_text("parameters", json.dumps(metadata))
            kwargs["pnginfo"] = png_info

        # Write Image
        try:
            image.save(filepath, format=save_fmt.upper(), **kwargs)
            logger.info(
                "Saved image and metadata to %s (format=%s)",
                filepath.name,
                fmt,
            )
        except OSError as exc:
            # Clean up the JSON if image failed to save (e.g. disk full)
            if json_path.exists():
                try:
                    json_path.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"Failed to save image {filepath.name}. Disk full or permissions error? {exc}") from exc

        return filepath

    def load_history(self) -> list[tuple[str, str]]:
        """Load history from saved JSON metadata files.

        Returns:
            A list of tuples (absolute_image_path, prompt) sorted by newest first.
        """
        history: list[tuple[str, str]] = []
        if not self._base_dir.exists():
            return history

        # Iterate through all JSON files in subdirectories
        json_files = list(self._base_dir.rglob("*.json"))
        
        # Parse and sort
        records = []
        for j_path in json_files:
            try:
                with open(j_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Try to find corresponding image
                # Check for png, jpg, jpeg, webp
                img_path = None
                for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    candidate = j_path.with_suffix(ext)
                    if candidate.exists():
                        img_path = str(candidate.absolute())
                        break
                
                if not img_path:
                    continue
                    
                timestamp = data.get("timestamp", "")
                prompt = data.get("prompt", "Unknown prompt")
                records.append((timestamp, img_path, prompt))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Failed to read metadata %s: %s", j_path, exc)

        # Sort newest first
        records.sort(key=lambda x: x[0], reverse=True)
        
        for _, path, prompt in records:
            history.append((path, prompt))
            
        return history
