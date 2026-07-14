"""UI smoke tests — verify the Gradio app can be created and handlers work."""

from unittest import mock

import gradio as gr
import pytest
from PIL import Image

from src.models.generation import GenerationRequest, GenerationResult
from src.ui.app import _format_result_info, _parse_seed, create_app, handle_generate


class TestParsesSeed:
    """Tests for the seed parsing helper."""

    def test_empty_string_returns_none(self) -> None:
        """Empty seed text should return None (random)."""
        assert _parse_seed("") is None

    def test_whitespace_returns_none(self) -> None:
        """Whitespace-only seed should return None."""
        assert _parse_seed("   ") is None

    def test_valid_integer(self) -> None:
        """Valid integer string should parse correctly."""
        assert _parse_seed("42") == 42

    def test_valid_integer_with_whitespace(self) -> None:
        """Integer with surrounding whitespace should parse."""
        assert _parse_seed("  123  ") == 123

    def test_invalid_seed_raises_error(self) -> None:
        """Non-integer seed should raise gr.Error."""
        with pytest.raises(gr.Error, match="whole number"):
            _parse_seed("not_a_number")


class TestFormatResultInfo:
    """Tests for result info formatting."""

    def test_formats_all_fields(self) -> None:
        """Should include engine, time, size, steps, guidance, seed."""
        img = Image.new("RGB", (64, 64))
        result = GenerationResult(
            image=img, prompt="test", engine="test_engine",
            generation_time=5.23, seed=42,
        )
        request = GenerationRequest(
            prompt="test", width=512, height=512,
            num_steps=20, guidance_scale=7.5,
        )
        info = _format_result_info(result, request)
        assert "test_engine" in info
        assert "5.23" in info
        assert "512" in info
        assert "42" in info


class TestCreateApp:
    """Tests for Gradio app creation."""

    def test_creates_blocks_instance(self) -> None:
        """create_app should return a gr.Blocks instance."""
        app = create_app()
        assert isinstance(app, gr.Blocks)

    def test_app_has_title(self) -> None:
        """App should have a title set."""
        app = create_app()
        assert app.title is not None
        assert "Image Craft" in app.title


class TestHandleGenerate:
    """Tests for the generate handler with mocked service."""

    def test_successful_generation(self) -> None:
        """Handler should return image and info on success."""
        mock_image = Image.new("RGB", (512, 512), color="green")
        mock_result = GenerationResult(
            image=mock_image,
            prompt="test prompt",
            engine="mock_engine",
            generation_time=1.5,
            seed=42,
        )

        with mock.patch(
            "src.ui.app.GenerationService"
        ) as MockService:
            instance = MockService.return_value
            instance.generate.return_value = mock_result

            image, info, gallery, state = handle_generate(
                prompt="test prompt",
                negative_prompt="",
                engine_name="mock_engine",
                width=512.0,
                height=512.0,
                steps=20.0,
                guidance=7.5,
                seed_text="42",
                history=[],
            )

            assert image.size == (512, 512)
            assert "mock_engine" in info
            assert "1.50" in info

    def test_empty_prompt_raises_error(self) -> None:
        """Handler should raise gr.Error for empty prompt."""
        with mock.patch(
            "src.ui.app.GenerationService"
        ) as MockService:
            instance = MockService.return_value
            instance.generate.side_effect = ValueError(
                "Please enter a prompt before generating."
            )

            with pytest.raises(gr.Error):
                handle_generate(
                    "", "", "mock_engine", 512.0, 512.0, 20.0, 7.5, "", []
                )
