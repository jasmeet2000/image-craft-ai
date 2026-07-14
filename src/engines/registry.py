"""Engine registry — maps config names to engine instances.

Adding a new engine requires:
1. Creating a new file in ``src/engines/`` that implements ``ImageGenerator``.
2. Adding one entry to ``_ENGINE_CLASSES`` in this file.

No changes to UI, services, or other engines.
"""

import logging
from typing import Type

from src.engines.base import ImageGenerator

logger = logging.getLogger(__name__)

# Maps config engine names to their implementation classes.
# Import inside the function to avoid circular imports and to defer
# heavy imports (e.g., torch) until actually needed.
_ENGINE_CLASSES: dict[str, str] = {
    "huggingface_cloud": "src.engines.huggingface_cloud.HuggingFaceCloudEngine",
    "local_diffusion": "src.engines.local_diffusion.LocalDiffusionEngine",
}

# Cache instantiated engines (one instance per engine name)
_engine_cache: dict[str, ImageGenerator] = {}


def _import_engine_class(dotted_path: str) -> Type[ImageGenerator]:
    """Import an engine class from its dotted module path.

    Args:
        dotted_path: Fully qualified class path
            (e.g., 'src.engines.huggingface_cloud.HuggingFaceCloudEngine').

    Returns:
        The engine class.

    Raises:
        ImportError: If the module or class cannot be found.
    """
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib

    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls


def get_engine(engine_name: str) -> ImageGenerator:
    """Get an engine instance by its config name.

    Engines are instantiated once and cached for the process lifetime.

    Args:
        engine_name: Engine identifier from config
            (e.g., 'huggingface_cloud').

    Returns:
        An ImageGenerator instance.

    Raises:
        ValueError: If the engine name is not registered.
    """
    if engine_name in _engine_cache:
        return _engine_cache[engine_name]

    if engine_name not in _ENGINE_CLASSES:
        available = ", ".join(sorted(_ENGINE_CLASSES.keys()))
        raise ValueError(
            f"Unknown engine '{engine_name}'. "
            f"Available engines: {available}"
        )

    dotted_path = _ENGINE_CLASSES[engine_name]
    logger.info("Loading engine: %s (%s)", engine_name, dotted_path)

    cls = _import_engine_class(dotted_path)
    instance = cls()
    _engine_cache[engine_name] = instance
    return instance


def list_engines() -> list[str]:
    """List all registered engine names.

    Returns:
        Sorted list of available engine names.
    """
    return sorted(_ENGINE_CLASSES.keys())


def register_engine(name: str, dotted_path: str) -> None:
    """Register a new engine (for plugins or testing).

    Args:
        name: Config name for the engine.
        dotted_path: Fully qualified class path.
    """
    _ENGINE_CLASSES[name] = dotted_path
    logger.info("Registered engine: %s -> %s", name, dotted_path)


def reset_registry() -> None:
    """Clear the engine cache. Used by tests."""
    _engine_cache.clear()
