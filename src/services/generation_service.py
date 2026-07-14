"""Generation service — orchestrates image generation across engines.

The UI calls this service; this service calls engines. The UI never
touches engines directly. This is the single point of orchestration
for prompt validation, engine selection, and result handling.
"""

import logging

from src.config.settings import get_settings
from src.engines.base import ImageGenerator
from src.engines.registry import get_engine
from src.models.generation import GenerationRequest, GenerationResult
from src.services.history_service import HistoryService

logger = logging.getLogger(__name__)

# Minimum prompt length to accept
_MIN_PROMPT_LENGTH = 2


class GenerationService:
    """Orchestrates image generation requests.

    Handles prompt validation, engine lookup, availability checks,
    and delegates actual generation to the active engine.
    """

    def __init__(self, engine: ImageGenerator | None = None) -> None:
        """Initialize the generation service.

        Args:
            engine: Optional engine override. If None, the active
                engine is loaded from config via the registry.
        """
        self._engine_override = engine
        self._history_service = HistoryService()

    def _get_engine(self, request: GenerationRequest | None = None) -> ImageGenerator:
        """Get the active engine from config or override.

        Args:
            request: The generation request (may contain engine override).

        Returns:
            The ImageGenerator instance to use.
        """
        if self._engine_override is not None:
            return self._engine_override
        
        engine_name = get_settings().engine
        if request and request.engine_override:
            engine_name = request.engine_override
            
        return get_engine(engine_name)

    def validate_prompt(self, prompt: str) -> str | None:
        """Validate a user prompt before generation.

        Args:
            prompt: The raw user prompt.

        Returns:
            Error message string if invalid, None if valid.
        """
        stripped = prompt.strip()
        if not stripped:
            return "Please enter a prompt before generating."
        if len(stripped) < _MIN_PROMPT_LENGTH:
            return (
                f"Prompt is too short (minimum {_MIN_PROMPT_LENGTH} "
                f"characters). Please describe what you'd like to see."
            )
        return None

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Validate and generate an image.

        Args:
            request: The generation parameters.

        Returns:
            A GenerationResult with the generated image.

        Raises:
            ValueError: If the prompt is invalid.
            RuntimeError: If the engine is unavailable or generation fails.
        """
        validation_error = self.validate_prompt(request.prompt)
        if validation_error:
            raise ValueError(validation_error)

        engine = self._get_engine(request)

        if not engine.is_available():
            raise RuntimeError(
                f"Engine '{engine.engine_name}' is not available. "
                f"Check your configuration and API keys."
            )

        estimated = engine.estimate_time(request)
        logger.info(
            "Starting generation (engine=%s, est. %.1fs)",
            engine.engine_name,
            estimated,
        )

        result = engine.generate(request)

        # Save the result to disk
        self._history_service.save_result(result)

        logger.info(
            "Generation complete: %.2fs (engine=%s)",
            result.generation_time,
            result.engine,
        )

        return result
