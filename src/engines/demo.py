"""Demo script: generate one image from the command line (no UI).

Usage:
    python -m src.engines.demo "a cat in space"

Requires HF_API_TOKEN to be set in .env or environment.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config.settings import get_settings
from src.models.generation import GenerationRequest
from src.services.generation_service import GenerationService
from src.utils.logging_setup import setup_logging


def main() -> None:
    """Generate a single image and save it to images/."""
    settings = get_settings()
    setup_logging(settings.log_dir, settings.log_level)

    # Get prompt from CLI args or use a default
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "a cat in space"

    print(f"\n  Prompt:  {prompt}")  # noqa: T201
    print(f"  Engine:  {settings.engine}")  # noqa: T201
    print(f"  Model:   {settings.hf_model}")  # noqa: T201
    print(f"  Size:    {settings.default_width}x{settings.default_height}")  # noqa: T201
    print()  # noqa: T201

    request = GenerationRequest(
        prompt=prompt,
        width=settings.default_width,
        height=settings.default_height,
        num_steps=settings.default_steps,
        guidance_scale=settings.default_guidance_scale,
    )

    service = GenerationService()

    try:
        print("  Generating... (this may take 10-30 seconds)")  # noqa: T201
        result = service.generate(request)
    except (ValueError, RuntimeError) as exc:
        print(f"\n  ERROR: {exc}")  # noqa: T201
        sys.exit(1)

    # Save the image
    output_dir = settings.image_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"demo_{int(result.generation_time * 100)}.png"
    output_path = output_dir / filename
    result.image.save(output_path)

    print(f"\n  ✓ Image saved to: {output_path}")  # noqa: T201
    print(f"  ✓ Generation time: {result.generation_time:.2f}s")  # noqa: T201
    print(f"  ✓ Engine: {result.engine}")  # noqa: T201
    print()  # noqa: T201


if __name__ == "__main__":
    main()
