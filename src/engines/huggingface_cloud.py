"""HuggingFace Inference API engine for cloud-based image generation.

Uses ``huggingface_hub.InferenceClient`` to call the HuggingFace
serverless Inference API. Requires a valid HF_API_TOKEN in config.
"""

import logging
import time
from typing import Any

from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

from src.config.settings import get_settings
from src.engines.base import ImageGenerator
from src.models.generation import GenerationRequest, GenerationResult

logger = logging.getLogger(__name__)

# Timeout for API calls (seconds)
_API_TIMEOUT = 120


class HuggingFaceCloudEngine(ImageGenerator):
    """Image generation via HuggingFace Inference API.

    Attributes:
        _client: The HF InferenceClient instance (created lazily).
        _model: The HF model ID to use for generation.
        _token: The HF API token.
    """

    def __init__(self) -> None:
        """Initialize engine with settings from config."""
        settings = get_settings()
        self._token = settings.hf_api_token
        self._model = settings.hf_model
        self._client: InferenceClient | None = None

    def _get_client(self) -> InferenceClient:
        """Get or create the InferenceClient (lazy init).

        Returns:
            A configured InferenceClient instance.
        """
        if self._client is None:
            self._client = InferenceClient(
                token=self._token,
                timeout=_API_TIMEOUT,
            )
            logger.debug("InferenceClient created for model: %s", self._model)
        return self._client

    def is_available(self) -> bool:
        """Check if the engine can run (token is set).

        Returns:
            True if HF_API_TOKEN is configured.
        """
        available = bool(self._token)
        if not available:
            logger.warning(
                "HuggingFaceCloudEngine unavailable: HF_API_TOKEN not set."
            )
        return available

    def estimate_time(self, request: GenerationRequest) -> float:
        """Estimate generation time for a cloud API call.

        Args:
            request: The generation parameters.

        Returns:
            Estimated time in seconds (rough, network-dependent).
        """
        # Cloud API time depends mainly on model and queue, not local hardware.
        # Base estimate: ~10s, scaled by steps relative to default (20).
        base_seconds = 10.0
        step_factor = request.num_steps / 20.0
        return round(base_seconds * step_factor, 1)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate an image via the HuggingFace Inference API.

        Args:
            request: The generation parameters.

        Returns:
            A GenerationResult with the generated image.

        Raises:
            RuntimeError: If the API call fails.
        """
        if not self.is_available():
            raise RuntimeError(
                "HuggingFace API token is missing or invalid. "
                "Set HF_API_TOKEN in .env or Settings."
            )

        client = self._get_client()
        api_kwargs = self._build_api_kwargs(request)

        logger.info(
            "Generating image: model=%s, prompt='%s' (%dx%d, %d steps)",
            self._model,
            request.prompt[:50],
            request.width,
            request.height,
            request.num_steps,
        )

        start_time = time.perf_counter()
        try:
            image = client.text_to_image(
                prompt=request.prompt,
                model=self._model,
                **api_kwargs,
            )
        except HfHubHTTPError as exc:
            raise RuntimeError(
                self._format_api_error(exc)
            ) from exc
        except (TimeoutError, ConnectionError) as exc:
            raise RuntimeError(
                "Network connection timed out or failed. Please check your internet connection."
            ) from exc
        except Exception as exc:
            if "timeout" in str(exc).lower():
                raise RuntimeError("The HuggingFace API timed out. Try again later.") from exc
            raise RuntimeError(
                f"Image generation failed: {exc}"
            ) from exc

        elapsed = round(time.perf_counter() - start_time, 2)
        logger.info("Image generated in %.2fs", elapsed)

        return GenerationResult(
            image=image,
            prompt=request.prompt,
            engine="huggingface_cloud",
            generation_time=elapsed,
            seed=request.seed if request.seed is not None else -1,
            parameters=request.to_dict(),
        )

    def _build_api_kwargs(self, request: GenerationRequest) -> dict[str, Any]:
        """Build keyword arguments for the InferenceClient call.

        Args:
            request: The generation parameters.

        Returns:
            Dict of API keyword arguments.
        """
        actual_steps = request.num_steps
        actual_guidance = request.guidance_scale

        # FLUX.1-schnell is a distilled 1-4 step model.
        if "schnell" in self._model.lower():
            if actual_steps > 4:
                logger.info("FLUX.1-schnell detected. Capping steps from %d to 4.", actual_steps)
                actual_steps = 4
            # FLUX.1-schnell does not use guidance scale usually, but setting to 0.0 or leaving as is usually works.
            # We'll just pass it as is unless it causes issues, but for safety we can let the API handle it.

        kwargs: dict[str, Any] = {
            "width": request.width,
            "height": request.height,
            "num_inference_steps": actual_steps,
            "guidance_scale": actual_guidance,
        }
        if request.negative_prompt:
            kwargs["negative_prompt"] = request.negative_prompt
        if request.seed is not None:
            kwargs["seed"] = request.seed
        return kwargs

    @staticmethod
    def _format_api_error(exc: HfHubHTTPError) -> str:
        """Format an HF API error into a user-friendly message.

        Args:
            exc: The HTTP error from the HF API.

        Returns:
            A human-readable error message.
        """
        msg = str(exc)
        if "401" in msg or "403" in msg:
            return (
                "HuggingFace API token is invalid or lacks permissions. "
                "Check your token at https://huggingface.co/settings/tokens"
            )
        if "429" in msg:
            return (
                "HuggingFace API rate limit exceeded. "
                "Wait a moment and try again, or upgrade your plan."
            )
        if "503" in msg:
            return (
                "The model is currently loading on HuggingFace servers. "
                "Try again in 30-60 seconds."
            )
        return f"HuggingFace API error: {msg}"

    @property
    def engine_name(self) -> str:
        """Human-readable engine name.

        Returns:
            Display name including the model.
        """
        return f"HuggingFace Cloud ({self._model})"
