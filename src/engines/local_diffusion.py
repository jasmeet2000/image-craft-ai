"""Local Stable Diffusion engine for on-device image generation.

Uses HuggingFace Diffusers and PyTorch to generate images locally.
Auto-detects CUDA/MPS/CPU hardware and loads the model into VRAM/RAM.
The model is loaded lazily on first generation to keep startup fast.
"""

import gc
import logging
import time
from typing import Any

from src.config.hardware import get_hardware_info
from src.config.settings import get_settings
from src.engines.base import ImageGenerator
from src.models.generation import GenerationRequest, GenerationResult

logger = logging.getLogger(__name__)


class LocalDiffusionEngine(ImageGenerator):
    """Image generation via local Diffusers pipeline.

    Attributes:
        _model_id: HuggingFace model ID for local inference.
        _device: The compute device ('cuda', 'mps', 'cpu').
        _pipeline: The active Diffusers pipeline (loaded lazily).
    """

    def __init__(self) -> None:
        """Initialize engine with settings and detect hardware."""
        settings = get_settings()
        hardware = get_hardware_info()
        self._model_id = settings.local_model
        self._device = hardware.device
        self._pipeline: Any | None = None

    def _load_pipeline(self) -> Any:
        """Load the Diffusers pipeline into memory lazily.

        Returns:
            The loaded AutoPipelineForText2Image instance.
        """
        if self._pipeline is not None:
            return self._pipeline

        import torch
        from diffusers import AutoPipelineForText2Image

        logger.info(
            "Loading local model '%s' onto device '%s'. This may take a moment...",
            self._model_id,
            self._device,
        )

        dtype = torch.float16 if self._device != "cpu" else torch.float32

        self._pipeline = AutoPipelineForText2Image.from_pretrained(
            self._model_id,
            torch_dtype=dtype,
            variant="fp16" if self._device != "cpu" else None,
        )
        self._pipeline.to(self._device)

        # Basic memory optimizations for CUDA/MPS
        if self._device == "cuda":
            self._pipeline.enable_model_cpu_offload()

        logger.info("Local model loaded successfully.")
        return self._pipeline

    def is_available(self) -> bool:
        """Check if local inference is possible (torch/diffusers installed).

        Returns:
            True if required packages are installed.
        """
        try:
            import diffusers  # noqa: F401
            import torch  # noqa: F401

            return True
        except ImportError:
            logger.warning(
                "LocalDiffusionEngine unavailable: 'torch' or 'diffusers' "
                "not installed. Install Phase 6 dependencies."
            )
            return False

    def estimate_time(self, request: GenerationRequest) -> float:
        """Estimate generation time based on hardware and steps.

        Args:
            request: The generation parameters.

        Returns:
            Estimated time in seconds.
        """
        base_step_time = 0.1 if self._device == "cuda" else 0.5
        if self._device == "cpu":
            base_step_time = 2.0

        estimated = request.num_steps * base_step_time
        # Add buffer if model needs loading
        if self._pipeline is None:
            estimated += 15.0

        return round(estimated, 1)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate an image using the local model.

        Args:
            request: The generation parameters.

        Returns:
            A GenerationResult with the generated image.

        Raises:
            RuntimeError: If generation fails or dependencies missing.
        """
        if not self.is_available():
            raise RuntimeError(
                "Local generation dependencies are missing. "
                "Ensure torch and diffusers are installed."
            )

        import torch

        pipeline = self._load_pipeline()
        generator = None
        if request.seed is not None:
            generator = torch.Generator(device=self._device).manual_seed(request.seed)

        logger.info(
            "Generating locally: model=%s, device=%s, prompt='%s' (%dx%d, %d steps)",
            self._model_id,
            self._device,
            request.prompt[:50],
            request.width,
            request.height,
            request.num_steps,
        )

        start_time = time.perf_counter()

        try:
            output = pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_steps,
                guidance_scale=request.guidance_scale,
                generator=generator,
            )
            image = output.images[0]
        except torch.cuda.OutOfMemoryError as exc:
            raise RuntimeError(
                "Your GPU ran out of memory (VRAM). Try reducing the image dimensions "
                "(width/height) or close other applications."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Local generation failed: {exc}") from exc
        finally:
            self._free_memory()

        elapsed = round(time.perf_counter() - start_time, 2)
        logger.info("Local image generated in %.2fs", elapsed)

        return GenerationResult(
            image=image,
            prompt=request.prompt,
            engine="local_diffusion",
            generation_time=elapsed,
            seed=request.seed if request.seed is not None else -1,
            parameters=request.to_dict(),
        )

    def _free_memory(self) -> None:
        """Clear caches after generation to prevent OOM errors."""
        import torch

        if self._device == "cuda":
            torch.cuda.empty_cache()
        elif self._device == "mps":
            torch.mps.empty_cache()
        gc.collect()

    @property
    def engine_name(self) -> str:
        """Human-readable engine name.

        Returns:
            Display name including the model.
        """
        return f"Local Diffusion ({self._model_id})"
