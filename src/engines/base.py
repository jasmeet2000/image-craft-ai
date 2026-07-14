"""Abstract base class for all image generation engines.

Every engine (cloud or local) implements this contract. The service
layer and UI interact only with this interface — they never touch
engine internals.
"""

from abc import ABC, abstractmethod

from src.models.generation import GenerationRequest, GenerationResult


class ImageGenerator(ABC):
    """Abstract base for image generation engines.

    Subclasses must implement ``generate``, ``is_available``, and
    ``estimate_time``. Adding a new engine means creating one new file
    with a class that inherits from this ABC, plus one config entry in
    the engine registry.
    """

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate an image from a text prompt.

        Args:
            request: The generation parameters (prompt, size, etc.).

        Returns:
            A GenerationResult containing the image and metadata.

        Raises:
            RuntimeError: If generation fails for any reason.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this engine is ready to generate.

        Returns:
            True if all preconditions are met (API key present,
            model loaded, etc.).
        """
        ...

    @abstractmethod
    def estimate_time(self, request: GenerationRequest) -> float:
        """Estimate generation time in seconds for the given request.

        This is a rough estimate for UI display — not a guarantee.

        Args:
            request: The generation parameters.

        Returns:
            Estimated time in seconds.
        """
        ...

    @property
    def engine_name(self) -> str:
        """Human-readable engine name for display.

        Returns:
            The engine class name by default. Override for custom names.
        """
        return self.__class__.__name__
