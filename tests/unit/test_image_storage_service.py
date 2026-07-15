"""Unit tests for the image storage service."""

import json
from datetime import datetime
from pathlib import Path
from unittest import mock

from PIL import Image

from src.models.generation import GenerationResult
from src.services.image_storage_service import ImageStorageService


class TestImageStorageService:
    """Tests for ImageStorageService."""

    @mock.patch("src.services.image_storage_service.get_settings")
    def test_save_result_png_and_json(self, mock_get_settings, tmp_path: Path) -> None:
        """Test saving a PNG image creates JSON and PNG in date folder."""
        mock_settings = mock.Mock()
        mock_settings.image_output_dir = tmp_path
        mock_settings.image_format = "png"
        mock_get_settings.return_value = mock_settings

        service = ImageStorageService()
        
        img = Image.new("RGB", (64, 64), color="red")
        result = GenerationResult(
            image=img,
            prompt="A very nice test prompt!",
            engine="mock_engine",
            generation_time=1.0,
            seed=42,
            timestamp="2026-07-14T12:00:00+00:00"
        )

        filepath = service.save_result(result)

        # Should be in a YYYY-MM-DD folder
        assert filepath.parent.name == "2026-07-14"
        assert filepath.suffix == ".png"
        
        # Check slug
        assert "a-very-nice-test-prompt" in filepath.name
        
        # Check JSON sidecar
        json_path = filepath.with_suffix(".json")
        assert json_path.exists()
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["prompt"] == "A very nice test prompt!"
            assert data["seed"] == 42
            
        # Check load_history
        history = service.load_history()
        assert len(history) == 1
        assert history[0][0] == str(filepath.absolute())

    @mock.patch("src.services.image_storage_service.get_settings")
    def test_save_result_collision(self, mock_get_settings, tmp_path: Path) -> None:
        """Test handling of identical filenames."""
        mock_settings = mock.Mock()
        mock_settings.image_output_dir = tmp_path
        mock_settings.image_format = "png"
        mock_get_settings.return_value = mock_settings

        service = ImageStorageService()
        
        img = Image.new("RGB", (64, 64))
        result = GenerationResult(
            image=img,
            prompt="collision test",
            engine="test",
            generation_time=1.0,
            seed=1,
            timestamp="2026-07-14T12:00:00+00:00"
        )

        # Save twice
        filepath_1 = service.save_result(result)
        filepath_2 = service.save_result(result)

        assert filepath_1 != filepath_2
        assert filepath_2.name.endswith("_1.png")
