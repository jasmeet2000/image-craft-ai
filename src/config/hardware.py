"""Hardware auto-detection for Image Craft AI.

Detects available compute devices (CUDA, MPS, CPU) and caches the result.
Handles the case where PyTorch is not yet installed by falling back to CPU
gracefully.
"""

from __future__ import annotations
import logging
import platform
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HardwareInfo:
    """Detected hardware capabilities.

    Attributes:
        device: Best available compute device ('cuda', 'mps', or 'cpu').
        device_name: Human-readable name of the active device.
        cuda_available: Whether CUDA is available.
        cuda_device_name: CUDA GPU name (empty if unavailable).
        cuda_vram_gb: CUDA GPU VRAM in GB (0.0 if unavailable).
        mps_available: Whether MPS (Apple Silicon) is available.
        cpu_name: CPU model name.
        python_version: Python version string.
        os_name: Operating system name.
        os_version: Operating system version.
    """

    device: str
    device_name: str
    cuda_available: bool
    cuda_device_name: str
    cuda_vram_gb: float
    mps_available: bool
    cpu_name: str
    python_version: str
    os_name: str
    os_version: str


def _detect_cuda() -> tuple[bool, str, float]:
    """Detect CUDA GPU availability and specs.

    Returns:
        Tuple of (is_available, device_name, vram_in_gb).
    """
    try:
        import torch

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = round(vram_bytes / (1024**3), 1)
            logger.debug("CUDA detected: %s (%.1f GB)", name, vram_gb)
            return True, name, vram_gb
    except ImportError:
        logger.debug("PyTorch not installed — CUDA detection skipped.")
    except Exception as exc:
        logger.warning("CUDA detection failed: %s", exc)
    return False, "", 0.0


def _detect_mps() -> bool:
    """Detect Apple Silicon MPS backend availability.

    Returns:
        True if MPS backend is available and functional.
    """
    try:
        import torch

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            logger.debug("MPS (Apple Silicon) detected.")
            return True
    except ImportError:
        pass
    except Exception as exc:
        logger.warning("MPS detection failed: %s", exc)
    return False


def detect_hardware() -> HardwareInfo:
    """Detect and return current hardware capabilities.

    Priority: CUDA > MPS > CPU.

    Returns:
        A HardwareInfo instance with all detected capabilities.
    """
    cuda_available, cuda_name, cuda_vram = _detect_cuda()
    mps_available = _detect_mps()

    if cuda_available:
        device = "cuda"
        device_name = cuda_name
    elif mps_available:
        device = "mps"
        device_name = "Apple Silicon (MPS)"
    else:
        device = "cpu"
        device_name = platform.processor() or "Unknown CPU"

    cpu_name = platform.processor() or "Unknown CPU"

    info = HardwareInfo(
        device=device,
        device_name=device_name,
        cuda_available=cuda_available,
        cuda_device_name=cuda_name,
        cuda_vram_gb=cuda_vram,
        mps_available=mps_available,
        cpu_name=cpu_name,
        python_version=platform.python_version(),
        os_name=platform.system(),
        os_version=platform.version(),
    )

    logger.info("Hardware: device=%s (%s)", info.device, info.device_name)
    return info


# Module-level cached singleton
_cached_hardware: HardwareInfo | None = None


def get_hardware_info() -> HardwareInfo:
    """Get cached hardware info (detects on first call).

    Returns:
        The cached HardwareInfo instance.
    """
    global _cached_hardware
    if _cached_hardware is None:
        _cached_hardware = detect_hardware()
    return _cached_hardware


def reset_hardware_info() -> None:
    """Clear the cached hardware info. Used by tests."""
    global _cached_hardware
    _cached_hardware = None
