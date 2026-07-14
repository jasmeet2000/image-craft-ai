"""Application settings loaded from environment variables and .env file.

Settings are loaded once via ``get_settings()`` and cached for the process
lifetime. Environment variables override ``.env`` values, which override
defaults.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Project root: two levels up from src/config/settings.py
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_VALID_ENGINES = frozenset({"huggingface_cloud", "local_diffusion"})
_VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})


@dataclass(frozen=True)
class Settings:
    """Typed, validated application settings.

    Attributes:
        engine: Active engine identifier (huggingface_cloud | local_diffusion).
        hf_api_token: HuggingFace API token for cloud engine.
        hf_model: HuggingFace model ID for cloud inference.
        local_model: HuggingFace model ID for local inference.
        default_width: Default image width in pixels.
        default_height: Default image height in pixels.
        default_steps: Default number of inference steps.
        default_guidance_scale: Default CFG guidance scale.
        image_output_dir: Directory to save generated images.
        log_dir: Directory to save log files.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        project_root: Resolved project root path.
    """

    engine: str = "huggingface_cloud"
    hf_api_token: str = ""
    hf_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    local_model: str = "stabilityai/sd-turbo"
    default_width: int = 512
    default_height: int = 512
    default_steps: int = 20
    default_guidance_scale: float = 7.5
    image_output_dir: Path = field(default_factory=lambda: _PROJECT_ROOT / "images")
    log_dir: Path = field(default_factory=lambda: _PROJECT_ROOT / "logs")
    log_level: str = "INFO"
    project_root: Path = field(default_factory=lambda: _PROJECT_ROOT)


def validate_settings(settings: Settings) -> list[str]:
    """Validate settings and return a list of issues found.

    Args:
        settings: The Settings instance to validate.

    Returns:
        List of issue descriptions (empty if all valid).
    """
    issues: list[str] = []

    if settings.engine not in _VALID_ENGINES:
        issues.append(
            f"ENGINE '{settings.engine}' is not valid. "
            f"Options: {', '.join(sorted(_VALID_ENGINES))}"
        )

    if settings.log_level.upper() not in _VALID_LOG_LEVELS:
        issues.append(
            f"LOG_LEVEL '{settings.log_level}' is not valid. "
            f"Options: {', '.join(sorted(_VALID_LOG_LEVELS))}"
        )

    if not 64 <= settings.default_width <= 2048:
        issues.append(
            f"DEFAULT_WIDTH {settings.default_width} out of range (64–2048)."
        )

    if not 64 <= settings.default_height <= 2048:
        issues.append(
            f"DEFAULT_HEIGHT {settings.default_height} out of range (64–2048)."
        )

    if not 1 <= settings.default_steps <= 150:
        issues.append(
            f"DEFAULT_STEPS {settings.default_steps} out of range (1–150)."
        )

    if not 0.0 <= settings.default_guidance_scale <= 30.0:
        issues.append(
            f"DEFAULT_GUIDANCE_SCALE {settings.default_guidance_scale} "
            f"out of range (0.0–30.0)."
        )

    if settings.engine == "huggingface_cloud" and not settings.hf_api_token:
        issues.append(
            "HF_API_TOKEN is not set. Required for huggingface_cloud engine. "
            "Set it in .env or environment variables."
        )

    return issues


def load_settings() -> Settings:
    """Load settings from .env file and environment variables.

    Environment variables take precedence over .env values, which take
    precedence over defaults.

    Returns:
        A validated Settings instance.
    """
    dotenv_path = _PROJECT_ROOT / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)
        logger.debug("Loaded .env from %s", dotenv_path)
    else:
        logger.info(
            "No .env file found at %s — using defaults and environment.",
            dotenv_path,
        )

    settings = Settings(
        engine=os.getenv("ENGINE", "huggingface_cloud"),
        hf_api_token=os.getenv("HF_API_TOKEN", ""),
        hf_model=os.getenv(
            "HF_MODEL", "stabilityai/stable-diffusion-xl-base-1.0"
        ),
        local_model=os.getenv(
            "LOCAL_MODEL", "stabilityai/sd-turbo"
        ),
        default_width=int(os.getenv("DEFAULT_WIDTH", "512")),
        default_height=int(os.getenv("DEFAULT_HEIGHT", "512")),
        default_steps=int(os.getenv("DEFAULT_STEPS", "20")),
        default_guidance_scale=float(os.getenv("DEFAULT_GUIDANCE_SCALE", "7.5")),
        image_output_dir=Path(
            os.getenv("IMAGE_OUTPUT_DIR", str(_PROJECT_ROOT / "images"))
        ),
        log_dir=Path(os.getenv("LOG_DIR", str(_PROJECT_ROOT / "logs"))),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        project_root=_PROJECT_ROOT,
    )

    for issue in validate_settings(settings):
        logger.warning("Config: %s", issue)

    return settings


# Module-level cached singleton
_cached_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached application settings (loads on first call).

    Returns:
        The cached Settings instance.
    """
    global _cached_settings
    if _cached_settings is None:
        _cached_settings = load_settings()
    return _cached_settings


def reset_settings() -> None:
    """Clear the cached settings. Used by tests."""
    global _cached_settings
    _cached_settings = None
