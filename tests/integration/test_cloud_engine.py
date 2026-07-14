"""Integration tests for the HuggingFace cloud engine."""

from unittest import mock

import pytest
from PIL import Image

from src.engines.huggingface_cloud import HuggingFaceCloudEngine
from src.models.generation import GenerationRequest


@pytest.fixture
def mock_inference_client():
    """Mock the HuggingFace InferenceClient to prevent real API calls."""
    with mock.patch("src.engines.huggingface_cloud.InferenceClient") as MockClient:
        client_instance = MockClient.return_value
        # Create a dummy image for the text_to_image method to return
        dummy_img = Image.new("RGB", (512, 512), color="green")
        client_instance.text_to_image.return_value = dummy_img
        yield MockClient


class TestCloudEngineIntegration:
    """Tests for HuggingFaceCloudEngine."""

    @mock.patch("src.engines.huggingface_cloud.get_settings")
    def test_cloud_engine_generate(self, mock_get_settings, mock_inference_client) -> None:
        """Test the full generation flow with a mocked client."""
        mock_settings = mock.Mock()
        mock_settings.hf_api_token = "fake_token"
        mock_settings.hf_model = "test/model"
        mock_get_settings.return_value = mock_settings

        engine = HuggingFaceCloudEngine()
        assert engine.is_available() is True

        request = GenerationRequest(prompt="A test prompt", width=512, height=512)
        result = engine.generate(request)

        assert result.engine == "huggingface_cloud"
        assert result.prompt == "A test prompt"
        assert result.image.size == (512, 512)
        
        # Verify the client was called correctly
        client_instance = mock_inference_client.return_value
        client_instance.text_to_image.assert_called_once()
        _, kwargs = client_instance.text_to_image.call_args
        assert kwargs["prompt"] == "A test prompt"
        assert kwargs["model"] == "test/model"
