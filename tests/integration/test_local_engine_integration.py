"""Integration tests for the Local Diffusion engine.

These tests run the actual local engine if a GPU is available.
If no GPU is available, the tests are skipped to avoid long CI times.
"""

import pytest

from src.config.hardware import detect_hardware
from src.engines.local_diffusion import LocalDiffusionEngine
from src.models.generation import GenerationRequest

hardware = detect_hardware()


@pytest.mark.skipif(
    not hardware.cuda_available,
    reason="Local integration tests require a CUDA GPU."
)
class TestLocalEngineIntegration:
    """Real integration tests for the local engine."""

    def test_local_engine_generate_real(self) -> None:
        """Test generating an image using the real local model."""
        engine = LocalDiffusionEngine()
        assert engine.is_available() is True

        # Use a very small step count for the test to keep it fast
        request = GenerationRequest(
            prompt="A tiny test image",
            width=256,
            height=256,
            num_steps=1,
            seed=42
        )

        result = engine.generate(request)

        assert result.engine == "local_diffusion"
        assert result.image.size == (256, 256)
        assert result.seed == 42
        assert result.generation_time > 0
