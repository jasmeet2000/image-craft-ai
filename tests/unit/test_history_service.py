"""Unit tests for the history service."""

from pathlib import Path
from unittest import mock

from PIL import Image

from src.models.generation import GenerationResult
from src.services.history_service import HistoryService


class TestHistoryService:
    """Tests for HistoryService."""

    @mock.patch("src.services.history_service.get_settings")
    def test_save_result_png(self, mock_get_settings, tmp_path: Path) -> None:
        """Test saving a PNG image."""
        mock_settings = mock.Mock()
        mock_settings.image_output_dir = tmp_path
        mock_settings.image_format = "png"
        mock_get_settings.return_value = mock_settings

        service = HistoryService()
        
        img = Image.new("RGB", (64, 64), color="red")
        result = GenerationResult(
            image=img,
            prompt="test",
            engine="mock_engine",
            generation_time=1.0,
            seed=42,
            timestamp="2026-07-14T12:00:00+00:00"
        )

        filepath = service.save_result(result)

        assert filepath.exists()
        assert filepath.suffix == ".png"
        assert "mock" in filepath.name
        assert "42" in filepath.name
        assert "20260714_120000" in filepath.name

    @mock.patch("src.services.history_service.get_settings")
    def test_save_result_jpeg(self, mock_get_settings, tmp_path: Path) -> None:
        """Test saving a JPEG image converts RGBA to RGB."""
        mock_settings = mock.Mock()
        mock_settings.image_output_dir = tmp_path
        mock_settings.image_format = "jpg"
        mock_settings.image_quality = 90
        mock_get_settings.return_value = mock_settings

        service = HistoryService()
        
        # JPEG doesn't support RGBA, so the service should convert it
        img = Image.new("RGBA", (64, 64), color=(255, 0, 0, 128))
        result = GenerationResult(
            image=img,
            prompt="test",
            engine="cloud_engine",
            generation_time=1.0,
            seed=100,
            timestamp="2026-07-14T12:00:00+00:00"
        )

        filepath = service.save_result(result)

        assert filepath.exists()
        assert filepath.suffix == ".jpg"
        
        # Verify it was saved as RGB
        saved_img = Image.open(filepath)
        assert saved_img.mode == "RGB"

    @mock.patch("src.services.history_service.get_settings")
    def test_save_result_fallback_timestamp(self, mock_get_settings, tmp_path: Path) -> None:
        """Test fallback if timestamp is an invalid ISO string."""
        mock_settings = mock.Mock()
        mock_settings.image_output_dir = tmp_path
        mock_settings.image_format = "webp"
        mock_settings.image_quality = 80
        mock_get_settings.return_value = mock_settings

        service = HistoryService()
        
        img = Image.new("RGB", (64, 64))
        result = GenerationResult(
            image=img,
            prompt="test",
            engine="test",
            generation_time=1.0,
            timestamp="not-iso-format"
        )

        filepath = service.save_result(result)
        assert filepath.exists()
        assert filepath.name.startswith("notisoformat")
