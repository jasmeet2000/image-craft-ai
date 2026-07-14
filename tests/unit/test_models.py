"""Unit tests for GenerationRequest and GenerationResult models."""

from PIL import Image

from src.models.generation import GenerationRequest, GenerationResult


class TestGenerationRequest:
    """Tests for the GenerationRequest dataclass."""

    def test_default_values(self) -> None:
        """Should have sensible defaults for optional fields."""
        req = GenerationRequest(prompt="test")
        assert req.prompt == "test"
        assert req.negative_prompt == ""
        assert req.width == 512
        assert req.height == 512
        assert req.num_steps == 20
        assert req.guidance_scale == 7.5
        assert req.seed is None

    def test_custom_values(self) -> None:
        """Should accept custom values for all fields."""
        req = GenerationRequest(
            prompt="a cat",
            negative_prompt="blurry",
            width=768,
            height=768,
            num_steps=30,
            guidance_scale=8.5,
            seed=42,
        )
        assert req.width == 768
        assert req.seed == 42

    def test_to_dict(self) -> None:
        """to_dict should return all parameters."""
        req = GenerationRequest(prompt="test", seed=42)
        d = req.to_dict()
        assert d["prompt"] == "test"
        assert d["seed"] == 42
        assert "width" in d
        assert "num_steps" in d


class TestGenerationResult:
    """Tests for the GenerationResult dataclass."""

    def test_creation_with_image(self) -> None:
        """Should store a PIL Image and metadata."""
        img = Image.new("RGB", (64, 64), color="red")
        result = GenerationResult(
            image=img,
            prompt="test",
            engine="test_engine",
            generation_time=1.5,
        )
        assert result.image.size == (64, 64)
        assert result.prompt == "test"
        assert result.engine == "test_engine"
        assert result.generation_time == 1.5

    def test_default_seed_is_unknown(self) -> None:
        """Default seed should be -1 (unknown)."""
        img = Image.new("RGB", (64, 64))
        result = GenerationResult(
            image=img, prompt="test", engine="e", generation_time=1.0
        )
        assert result.seed == -1

    def test_timestamp_auto_generated(self) -> None:
        """Timestamp should be auto-populated on creation."""
        img = Image.new("RGB", (64, 64))
        result = GenerationResult(
            image=img, prompt="test", engine="e", generation_time=1.0
        )
        assert result.timestamp  # Not empty
        assert "T" in result.timestamp  # ISO 8601 format
