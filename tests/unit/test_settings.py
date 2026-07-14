"""Unit tests for the settings loader."""

import os
from unittest import mock

import pytest

from src.config.settings import (
    Settings,
    load_settings,
    reset_settings,
    validate_settings,
)


class TestSettingsDefaults:
    """Tests for Settings dataclass default values."""

    def test_default_engine(self) -> None:
        """Default engine should be huggingface_cloud."""
        settings = Settings()
        assert settings.engine == "huggingface_cloud"

    def test_default_dimensions(self) -> None:
        """Default image dimensions should be 512x512."""
        settings = Settings()
        assert settings.default_width == 512
        assert settings.default_height == 512

    def test_default_generation_params(self) -> None:
        """Default steps and guidance should have sensible values."""
        settings = Settings()
        assert settings.default_steps == 20
        assert settings.default_guidance_scale == 7.5

    def test_default_log_level(self) -> None:
        """Default log level should be INFO."""
        settings = Settings()
        assert settings.log_level == "INFO"

    def test_settings_is_frozen(self) -> None:
        """Settings should be immutable after creation."""
        settings = Settings()
        with pytest.raises(AttributeError):
            settings.engine = "local_diffusion"  # type: ignore[misc]


class TestSettingsValidation:
    """Tests for settings validation logic."""

    def test_valid_cloud_engine_with_token(self) -> None:
        """Valid cloud engine with token should produce no issues."""
        settings = Settings(engine="huggingface_cloud", hf_api_token="hf_test")
        issues = validate_settings(settings)
        assert len(issues) == 0

    def test_valid_local_engine_no_token(self) -> None:
        """Local engine without token should produce no issues."""
        settings = Settings(engine="local_diffusion", hf_api_token="")
        issues = validate_settings(settings)
        assert len(issues) == 0

    def test_invalid_engine_name(self) -> None:
        """Invalid engine name should produce a validation issue."""
        settings = Settings(engine="nonexistent")
        issues = validate_settings(settings)
        assert any("ENGINE" in i for i in issues)

    def test_missing_token_for_cloud_engine(self) -> None:
        """Cloud engine without token should warn."""
        settings = Settings(engine="huggingface_cloud", hf_api_token="")
        issues = validate_settings(settings)
        assert any("HF_API_TOKEN" in i for i in issues)

    def test_width_too_small(self) -> None:
        """Width below 64 should fail validation."""
        settings = Settings(default_width=32)
        issues = validate_settings(settings)
        assert any("DEFAULT_WIDTH" in i for i in issues)

    def test_width_too_large(self) -> None:
        """Width above 2048 should fail validation."""
        settings = Settings(default_width=4096)
        issues = validate_settings(settings)
        assert any("DEFAULT_WIDTH" in i for i in issues)

    def test_height_out_of_range(self) -> None:
        """Height outside 64–2048 should fail validation."""
        settings = Settings(default_height=10)
        issues = validate_settings(settings)
        assert any("DEFAULT_HEIGHT" in i for i in issues)

    def test_steps_out_of_range(self) -> None:
        """Steps outside 1–150 should fail validation."""
        settings = Settings(default_steps=0)
        issues = validate_settings(settings)
        assert any("DEFAULT_STEPS" in i for i in issues)

    def test_guidance_scale_out_of_range(self) -> None:
        """Guidance scale outside 0.0–30.0 should fail validation."""
        settings = Settings(default_guidance_scale=50.0)
        issues = validate_settings(settings)
        assert any("DEFAULT_GUIDANCE_SCALE" in i for i in issues)

    def test_invalid_log_level(self) -> None:
        """Invalid log level should fail validation."""
        settings = Settings(engine="local_diffusion", log_level="VERBOSE")
        issues = validate_settings(settings)
        assert any("LOG_LEVEL" in i for i in issues)


class TestLoadSettings:
    """Tests for loading settings from environment variables."""

    def setup_method(self) -> None:
        """Reset cached settings before each test."""
        reset_settings()

    def test_loads_from_env_vars(self) -> None:
        """Settings should be populated from environment variables."""
        env = {
            "ENGINE": "local_diffusion",
            "HF_API_TOKEN": "hf_test_token_12345678",
            "DEFAULT_WIDTH": "768",
            "DEFAULT_HEIGHT": "768",
            "DEFAULT_STEPS": "30",
            "DEFAULT_GUIDANCE_SCALE": "8.5",
            "LOG_LEVEL": "DEBUG",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            settings = load_settings()
            assert settings.engine == "local_diffusion"
            assert settings.hf_api_token == "hf_test_token_12345678"
            assert settings.default_width == 768
            assert settings.default_height == 768
            assert settings.default_steps == 30
            assert settings.default_guidance_scale == 8.5
            assert settings.log_level == "DEBUG"

    def test_defaults_when_no_env(self) -> None:
        """Should use defaults when env vars are not set."""
        # Clear relevant env vars
        keys_to_clear = [
            "ENGINE", "HF_API_TOKEN", "DEFAULT_WIDTH", "DEFAULT_HEIGHT",
            "DEFAULT_STEPS", "DEFAULT_GUIDANCE_SCALE", "LOG_LEVEL",
        ]
        clean_env = {k: v for k, v in os.environ.items() if k not in keys_to_clear}
        with mock.patch.dict(os.environ, clean_env, clear=True):
            settings = load_settings()
            assert settings.engine == "huggingface_cloud"
            assert settings.default_width == 512
