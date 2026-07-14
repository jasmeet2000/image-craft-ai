"""Unit tests for engine registry and generation service."""

from unittest import mock

import pytest
from PIL import Image

from src.engines.base import ImageGenerator
from src.engines.registry import (
    get_engine,
    list_engines,
    register_engine,
    reset_registry,
)
from src.models.generation import GenerationRequest, GenerationResult
from src.services.generation_service import GenerationService


# --- Mock engine for testing ---


class MockEngine(ImageGenerator):
    """A fake engine that returns a solid-color image."""

    def __init__(self) -> None:
        self._available = True

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Return a dummy image."""
        img = Image.new("RGB", (request.width, request.height), color="blue")
        return GenerationResult(
            image=img,
            prompt=request.prompt,
            engine="mock_engine",
            generation_time=0.01,
            seed=request.seed if request.seed is not None else -1,
            parameters=request.to_dict(),
        )

    def is_available(self) -> bool:
        """Return configurable availability."""
        return self._available

    def estimate_time(self, request: GenerationRequest) -> float:
        """Return instant estimate."""
        return 0.1


# --- Registry tests ---


class TestEngineRegistry:
    """Tests for the engine registry."""

    def setup_method(self) -> None:
        """Reset registry cache before each test."""
        reset_registry()

    def test_list_engines_includes_cloud(self) -> None:
        """Registry should include huggingface_cloud."""
        engines = list_engines()
        assert "huggingface_cloud" in engines

    def test_unknown_engine_raises(self) -> None:
        """Getting an unknown engine should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown engine"):
            get_engine("nonexistent_engine")

    def test_register_custom_engine(self) -> None:
        """register_engine should add a new engine to the registry."""
        register_engine(
            "mock",
            "tests.unit.test_engine_service.MockEngine",
        )
        assert "mock" in list_engines()

    def test_get_registered_engine(self) -> None:
        """Getting a registered engine should return an instance."""
        register_engine(
            "mock",
            "tests.unit.test_engine_service.MockEngine",
        )
        engine = get_engine("mock")
        assert isinstance(engine, MockEngine)


# --- GenerationService tests ---


class TestGenerationService:
    """Tests for the generation service orchestration."""

    def test_validate_empty_prompt(self) -> None:
        """Empty prompt should return an error message."""
        service = GenerationService()
        error = service.validate_prompt("")
        assert error is not None
        assert "enter a prompt" in error.lower()

    def test_validate_whitespace_only_prompt(self) -> None:
        """Whitespace-only prompt should return an error."""
        service = GenerationService()
        error = service.validate_prompt("   ")
        assert error is not None

    def test_validate_valid_prompt(self) -> None:
        """Valid prompt should return None (no error)."""
        service = GenerationService()
        error = service.validate_prompt("a cat in space")
        assert error is None

    def test_validate_short_prompt(self) -> None:
        """Single-character prompt should fail validation."""
        service = GenerationService()
        error = service.validate_prompt("a")
        assert error is not None
        assert "too short" in error.lower()

    def test_generate_with_mock_engine(self) -> None:
        """Service should orchestrate generation via injected engine."""
        engine = MockEngine()
        service = GenerationService(engine=engine)
        request = GenerationRequest(prompt="a blue square", seed=42)
        result = service.generate(request)

        assert result.image.size == (512, 512)
        assert result.prompt == "a blue square"
        assert result.engine == "mock_engine"
        assert result.seed == 42

    def test_generate_rejects_empty_prompt(self) -> None:
        """Service should raise ValueError for empty prompt."""
        engine = MockEngine()
        service = GenerationService(engine=engine)
        request = GenerationRequest(prompt="")

        with pytest.raises(ValueError, match="enter a prompt"):
            service.generate(request)

    def test_generate_checks_engine_availability(self) -> None:
        """Service should raise RuntimeError if engine is unavailable."""
        engine = MockEngine()
        engine._available = False
        service = GenerationService(engine=engine)
        request = GenerationRequest(prompt="test prompt")

        with pytest.raises(RuntimeError, match="not available"):
            service.generate(request)

    def test_mock_engine_implements_contract(self) -> None:
        """MockEngine should fully implement the ImageGenerator ABC."""
        engine = MockEngine()
        assert isinstance(engine, ImageGenerator)
        assert engine.is_available() is True
        request = GenerationRequest(prompt="test")
        assert engine.estimate_time(request) > 0
