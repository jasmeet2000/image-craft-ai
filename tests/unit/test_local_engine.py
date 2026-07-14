"""Unit tests for the LocalDiffusionEngine.

Since we don't want to actually load a 2GB model and run inference during
standard unit testing, we mock the diffusers pipeline and torch.
"""

from unittest import mock

import pytest

from src.engines.local_diffusion import LocalDiffusionEngine
from src.models.generation import GenerationRequest


@pytest.fixture
def mock_hardware():
    """Mock the hardware detection to return a controlled state."""
    with mock.patch("src.engines.local_diffusion.get_hardware_info") as mock_hw:
        # Mock it as CUDA available for these tests
        mock_hw.return_value.device = "cuda"
        yield mock_hw


@pytest.fixture
def mock_settings():
    """Mock the settings to return test defaults."""
    with mock.patch("src.engines.local_diffusion.get_settings") as mock_set:
        mock_set.return_value.local_model = "test/model"
        yield mock_set


class TestLocalDiffusionEngine:
    """Tests for the local diffusion engine."""

    def test_initialization(self, mock_hardware, mock_settings):
        """Engine should initialize with correct model and device."""
        engine = LocalDiffusionEngine()
        assert engine._model_id == "test/model"
        assert engine._device == "cuda"
        assert engine._pipeline is None  # Lazy loading

    def test_estimate_time_cuda(self, mock_hardware, mock_settings):
        """Estimation should reflect CUDA speeds and lazy loading penalty."""
        engine = LocalDiffusionEngine()
        request = GenerationRequest(prompt="test", num_steps=20)
        
        # Initial estimate (includes 15s loading penalty)
        est = engine.estimate_time(request)
        assert est == 17.0  # 20 * 0.1 + 15.0

        # Estimate after loading (no penalty)
        engine._pipeline = mock.Mock()
        est_loaded = engine.estimate_time(request)
        assert est_loaded == 2.0  # 20 * 0.1

    def test_estimate_time_cpu(self, mock_hardware, mock_settings):
        """Estimation should reflect slower CPU speeds."""
        mock_hardware.return_value.device = "cpu"
        engine = LocalDiffusionEngine()
        request = GenerationRequest(prompt="test", num_steps=10)
        
        est = engine.estimate_time(request)
        assert est == 35.0  # 10 * 2.0 + 15.0
