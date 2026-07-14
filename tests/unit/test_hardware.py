"""Unit tests for hardware detection."""

from unittest import mock

import pytest

from src.config.hardware import (
    HardwareInfo,
    detect_hardware,
    reset_hardware_info,
)


class TestHardwareInfo:
    """Tests for the HardwareInfo dataclass."""

    def test_hardware_info_is_frozen(self) -> None:
        """HardwareInfo should be immutable after creation."""
        info = HardwareInfo(
            device="cpu",
            device_name="Test CPU",
            cuda_available=False,
            cuda_device_name="",
            cuda_vram_gb=0.0,
            mps_available=False,
            cpu_name="Test CPU",
            python_version="3.10.20",
            os_name="Windows",
            os_version="10.0",
        )
        with pytest.raises(AttributeError):
            info.device = "cuda"  # type: ignore[misc]


class TestHardwareDetection:
    """Tests for hardware auto-detection logic."""

    def setup_method(self) -> None:
        """Reset cached hardware info before each test."""
        reset_hardware_info()

    def test_returns_hardware_info_instance(self) -> None:
        """detect_hardware should return a HardwareInfo."""
        info = detect_hardware()
        assert isinstance(info, HardwareInfo)

    def test_device_is_valid(self) -> None:
        """Detected device should be one of cuda, mps, or cpu."""
        info = detect_hardware()
        assert info.device in ("cuda", "mps", "cpu")

    def test_python_version_populated(self) -> None:
        """Python version should be a non-empty string."""
        info = detect_hardware()
        assert info.python_version
        assert "." in info.python_version

    def test_os_name_populated(self) -> None:
        """OS name should be detected."""
        info = detect_hardware()
        assert info.os_name in ("Windows", "Linux", "Darwin")

    def test_cpu_fallback_when_no_gpu(self) -> None:
        """Should fall back to CPU when CUDA and MPS are unavailable."""
        with mock.patch(
            "src.config.hardware._detect_cuda", return_value=(False, "", 0.0)
        ):
            with mock.patch(
                "src.config.hardware._detect_mps", return_value=False
            ):
                info = detect_hardware()
                assert info.device == "cpu"
                assert info.cuda_available is False
                assert info.mps_available is False

    def test_cuda_selected_when_available(self) -> None:
        """Should select CUDA when it's available."""
        with mock.patch(
            "src.config.hardware._detect_cuda",
            return_value=(True, "NVIDIA GTX 1650", 4.0),
        ):
            with mock.patch(
                "src.config.hardware._detect_mps", return_value=False
            ):
                info = detect_hardware()
                assert info.device == "cuda"
                assert info.cuda_available is True
                assert info.cuda_device_name == "NVIDIA GTX 1650"
                assert info.cuda_vram_gb == 4.0

    def test_mps_selected_when_cuda_unavailable(self) -> None:
        """Should select MPS when CUDA is unavailable but MPS is."""
        with mock.patch(
            "src.config.hardware._detect_cuda", return_value=(False, "", 0.0)
        ):
            with mock.patch(
                "src.config.hardware._detect_mps", return_value=True
            ):
                info = detect_hardware()
                assert info.device == "mps"
                assert info.mps_available is True

    def test_cuda_takes_priority_over_mps(self) -> None:
        """CUDA should be preferred over MPS when both are available."""
        with mock.patch(
            "src.config.hardware._detect_cuda",
            return_value=(True, "NVIDIA RTX 3090", 24.0),
        ):
            with mock.patch(
                "src.config.hardware._detect_mps", return_value=True
            ):
                info = detect_hardware()
                assert info.device == "cuda"
