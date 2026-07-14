"""Data models for image generation requests and results.

These dataclasses flow between the UI, service, and engine layers.
They carry no logic — just structured data with sensible defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from PIL import Image


@dataclass
class GenerationRequest:
    """Parameters for an image generation request.

    Attributes:
        prompt: Text description of the desired image (required).
        negative_prompt: Things to exclude from the image.
        width: Image width in pixels.
        height: Image height in pixels.
        num_steps: Number of inference / denoising steps.
        guidance_scale: Classifier-free guidance scale (CFG).
        seed: Random seed for reproducibility (None = random).
        engine_override: Optional engine name to override the default.
    """

    prompt: str
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    num_steps: int = 20
    guidance_scale: float = 7.5
    seed: int | None = None
    engine_override: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dictionary for serialization.

        Returns:
            Dictionary of all parameters.
        """
        return {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "width": self.width,
            "height": self.height,
            "num_steps": self.num_steps,
            "guidance_scale": self.guidance_scale,
            "seed": self.seed,
            "engine_override": self.engine_override,
        }


@dataclass
class GenerationResult:
    """Result of a completed image generation.

    Attributes:
        image: The generated PIL Image.
        prompt: The prompt that was used.
        engine: Engine identifier that produced this image.
        generation_time: Wall-clock generation time in seconds.
        timestamp: ISO 8601 timestamp of when generation completed.
        seed: The seed that was used (or -1 if unknown).
        parameters: Full parameter dict for reproducibility.
    """

    image: Image.Image
    prompt: str
    engine: str
    generation_time: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    seed: int = -1
    parameters: dict[str, Any] = field(default_factory=dict)
