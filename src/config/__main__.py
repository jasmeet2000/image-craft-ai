"""CLI entry point: ``python -m src.config``.

Prints a human-readable summary of detected hardware and loaded
configuration. Used for quick diagnostics and setup verification.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for direct module execution
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config.hardware import detect_hardware
from src.config.settings import load_settings
from src.utils.logging_setup import setup_logging


def _mask_token(token: str) -> str:
    """Mask an API token for safe display.

    Args:
        token: The raw token string.

    Returns:
        Masked version showing first 4 and last 4 chars only.
    """
    if not token:
        return "(not set)"
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


def main() -> None:
    """Print hardware detection and configuration summary."""
    settings = load_settings()
    setup_logging(settings.log_dir, settings.log_level)
    hardware = detect_hardware()

    # NOTE: print() is used intentionally here — this is a CLI diagnostic
    # tool, not business logic. The output is structured for human reading,
    # not log ingestion.
    lines = [
        "",
        "=" * 52,
        "  Image Craft AI — System Check",
        "=" * 52,
        "",
        "  Hardware",
        f"    OS:             {hardware.os_name} {hardware.os_version}",
        f"    CPU:            {hardware.cpu_name}",
        f"    Python:         {hardware.python_version}",
        f"    Best Device:    {hardware.device} ({hardware.device_name})",
        f"    CUDA Available: {'Yes' if hardware.cuda_available else 'No'}",
    ]

    if hardware.cuda_available:
        lines.append(f"    GPU Name:       {hardware.cuda_device_name}")
        lines.append(f"    VRAM:           {hardware.cuda_vram_gb} GB")

    lines.extend([
        f"    MPS Available:  {'Yes' if hardware.mps_available else 'No'}",
        "",
        "  Configuration",
        f"    Engine:         {settings.engine}",
        f"    HF Token:       {_mask_token(settings.hf_api_token)}",
        f"    Image Size:     {settings.default_width}x{settings.default_height}",
        f"    Steps:          {settings.default_steps}",
        f"    Guidance:       {settings.default_guidance_scale}",
        f"    Output Dir:     {settings.image_output_dir}",
        f"    Log Dir:        {settings.log_dir}",
        f"    Log Level:      {settings.log_level}",
        "",
        "=" * 52,
        "",
    ])

    for line in lines:
        print(line)  # noqa: T201 — intentional CLI output


if __name__ == "__main__":
    main()
