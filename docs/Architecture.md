# Architecture — Image Craft AI

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Gradio UI Layer                   │
│         (src/ui/ — presentation only)               │
│    ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│    │ Generate  │  │ Gallery  │  │  Settings    │     │
│    │   Page    │  │  Page    │  │    Page      │     │
│    └─────┬─────┘  └────┬─────┘  └──────┬───────┘    │
└──────────┼──────────────┼───────────────┼────────────┘
           │              │               │
           ▼              ▼               ▼
┌─────────────────────────────────────────────────────┐
│                  Service Layer                       │
│          (src/services/ — orchestration)             │
│    ┌──────────────┐  ┌──────────────┐               │
│    │  Generation   │  │   History    │               │
│    │   Service     │  │   Service    │               │
│    └───────┬───────┘  └──────────────┘               │
└────────────┼─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│                  Engine Layer                        │
│       (src/engines/ — ImageGenerator ABC)            │
│    ┌────────────────┐    ┌────────────────────┐      │
│    │ HuggingFace    │    │  LocalDiffusion    │      │
│    │ CloudEngine    │    │  Engine            │      │
│    └────────────────┘    └────────────────────┘      │
└─────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│              Cross-Cutting Concerns                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  Config   │  │ Logging  │  │ Hardware Detect   │  │
│  │  Loader   │  │  Setup   │  │ (CPU/CUDA/MPS)    │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 2. Layer Rules

| Layer     | Directory       | May Call         | Must Not Call    |
| --------- | --------------- | ---------------- | ---------------- |
| UI        | `src/ui/`       | Services         | Engines, Config internals |
| Services  | `src/services/` | Engines, Models, Config, Utils | UI |
| Engines   | `src/engines/`  | Models, Config, Utils | UI, Services |
| Models    | `src/models/`   | Nothing          | Everything       |
| Config    | `src/config/`   | Utils            | UI, Services, Engines |
| Utils     | `src/utils/`    | Nothing          | Everything       |

**Direction of dependencies is strictly downward.** No layer may import from a layer above it.

## 3. Engine Contract

```python
from abc import ABC, abstractmethod
from src.models.generation import GenerationRequest, GenerationResult

class ImageGenerator(ABC):
    """Abstract base for all image generation engines."""

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate an image from a text prompt.

        Args:
            request: The generation parameters.

        Returns:
            A GenerationResult containing the image and metadata.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this engine can run (API key present, model loaded, etc.)."""
        ...

    @abstractmethod
    def estimate_time(self, request: GenerationRequest) -> float:
        """Estimate generation time in seconds for the given request."""
        ...
```

### Adding a New Engine (Extensibility Contract)

To add a new engine (e.g., `OpenAIEngine`), a developer must:

1. **Create one file**: `src/engines/openai_engine.py` implementing `ImageGenerator`.
2. **Add one config entry**: Register the engine name in the engine registry (config).

No changes to UI code, service code, or any other engine. This is tested explicitly in Phase 6.

## 4. Data Flow — Generate Image

```
User clicks "Generate"
       │
       ▼
   Gradio UI ──▶ GenerationService.generate(request)
       │                    │
       │                    ▼
       │            Engine Registry ──▶ get active engine from config
       │                    │
       │                    ▼
       │            engine.is_available() ──▶ check preconditions
       │                    │
       │                    ▼
       │            engine.generate(request) ──▶ [runs in background thread]
       │                    │
       │                    ▼
       │            GenerationResult (image bytes + metadata)
       │                    │
       │                    ▼
       │            HistoryService.save(result) ──▶ save to images/ + history.json
       │
       ▼
   UI displays image + metadata
```

## 5. Configuration Architecture

```
.env                          # User's actual secrets (gitignored)
.env.example                  # Template with placeholder values (committed)
src/config/settings.py        # Loads .env + validates + provides typed Settings object
src/config/hardware.py        # Auto-detects CPU / CUDA / MPS at startup
```

- All settings accessed via a single `Settings` object — no scattered `os.getenv()` calls.
- Hardware detection runs once at startup, result cached.
- Engine selection is a config value (`ENGINE=huggingface_cloud` or `ENGINE=local_diffusion`).

## 6. Models (Data Structures)

```python
# src/models/generation.py

@dataclass
class GenerationRequest:
    prompt: str
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    num_steps: int = 20
    guidance_scale: float = 7.5
    seed: int | None = None

@dataclass
class GenerationResult:
    image: Image.Image          # PIL Image
    prompt: str
    engine: str                 # "huggingface_cloud" | "local_diffusion"
    generation_time: float      # seconds
    timestamp: str              # ISO 8601
    seed: int
    parameters: dict            # full params for reproducibility
```

## 7. Project Structure

```
Image Craft AI/
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Rules.md
│   ├── Phases.md
│   ├── Design.md              # Created Phase 5
│   └── Memory.md
├── src/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py             # Gradio app entry point
│   ├── services/
│   │   ├── __init__.py
│   │   ├── generation_service.py
│   │   └── history_service.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── base.py            # ImageGenerator ABC
│   │   ├── registry.py        # Engine lookup by config name
│   │   └── huggingface_cloud.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── generation.py      # GenerationRequest, GenerationResult
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py        # Settings loader
│   │   ├── hardware.py        # Hardware auto-detection
│   │   └── __main__.py        # `python -m src.config` entry point
│   └── utils/
│       ├── __init__.py
│       ├── logging_setup.py
│       ├── image_utils.py
│       └── file_utils.py
├── assets/
├── images/                    # gitignored
├── logs/                      # gitignored
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   └── ui_smoke/
│       └── __init__.py
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```
