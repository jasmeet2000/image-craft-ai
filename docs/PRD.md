# Product Requirements Document — Image Craft AI

## 1. Vision

A cross-platform, desktop-in-browser AI image generator that runs on an average laptop. Users type a text prompt, pick an engine (cloud or local), and get an image — no enterprise GPU required, no DevOps ceremony, no silent failures.

## 2. Target Users

- **Primary**: Developers and hobbyists who want to experiment with AI image generation without complex setup.
- **Secondary**: Creators who need quick visual prototyping from text descriptions.

## 3. Platform & Environment

| Constraint        | Value                                                    |
| ----------------- | -------------------------------------------------------- |
| Primary OS        | Windows 10/11                                            |
| Secondary OS      | macOS, Linux (must work, tested after Windows)           |
| Python            | 3.10.x (dedicated conda env: `imagecraft`)               |
| GPU (dev machine) | NVIDIA GTX 1650, 4 GB VRAM                               |
| UI                | Gradio (browser-based, single framework)                 |
| Priority engine   | Cloud-first (HuggingFace Inference API, free tier)       |
| Local model       | `stabilityai/sd-turbo` (512×512, fits 4 GB VRAM)         |

## 4. Core Features (MVP)

### F1 — Text-to-Image Generation (Cloud)
- User enters a text prompt in the Gradio UI.
- Request is sent to HuggingFace Inference API.
- Generated image is displayed in the UI and saved to `images/`.
- Progress/loading state is visible; UI never blocks.

### F2 — Text-to-Image Generation (Local)
- Same flow as F1, but inference runs locally via HuggingFace Diffusers.
- Hardware is auto-detected: CUDA → MPS → CPU fallback.
- If VRAM is insufficient, user sees a clear message before generation starts.

### F3 — Engine Switching
- Active engine is set in `.env` or a settings file — not in code.
- Switching engines requires zero code changes.
- UI reflects which engine is active.
- Adding a new engine later requires only one new file + one config entry.

### F4 — Generation Parameters
- Prompt (required).
- Negative prompt (optional).
- Image size (dropdown: 512×512, 768×768 — constrained by model and VRAM).
- Number of inference steps (slider, sensible defaults per engine).
- Guidance scale / CFG (slider).
- Seed (optional, for reproducibility).

### F5 — Gallery & History
- Generated images are displayed in a scrollable gallery.
- Each entry shows: thumbnail, prompt used, engine, timestamp, generation time.
- History persists across sessions (file-based, not database).

### F6 — Settings Page
- View/change active engine.
- View detected hardware.
- Set/update HuggingFace API token.
- Theme toggle (light/dark).

### F7 — Error Handling
- Every failure mode produces a user-facing message explaining what happened and what to do.
- Never a raw stack trace. Never a silent crash.
- Covered failure modes (see §7).

## 5. Acceptance Criteria

| #   | Criterion                                                                 | Verification        |
| --- | ------------------------------------------------------------------------- | -------------------- |
| AC1 | User can generate an image from a text prompt via HF Inference API        | Manual + integration |
| AC2 | User can generate an image from a text prompt via local sd-turbo          | Manual + integration |
| AC3 | Switching `ENGINE=huggingface_cloud` ↔ `ENGINE=local_diffusion` in config changes engine without code edits | Config test          |
| AC4 | UI shows loading state during generation and never freezes                | UI smoke test        |
| AC5 | All 10 error scenarios (§7) produce user-friendly messages               | Unit + manual        |
| AC6 | Generated images are saved to `images/` with metadata                    | Unit test            |
| AC7 | Gallery displays past generations and persists across restarts            | Manual               |
| AC8 | `python -m src.config.check` prints detected hardware correctly          | Smoke test           |
| AC9 | App launches on Windows via `python -m src.ui.app` or equivalent         | Manual               |
| AC10| Adding a mock engine requires only one new file + one config entry        | Extensibility test   |

## 6. Out of Scope (v1)

- Image-to-image, inpainting, outpainting.
- Multiple cloud providers (only HF Inference API).
- User accounts, authentication, multi-tenancy.
- Batch/queue generation.
- Model fine-tuning or training.
- Mobile-native UI.
- Deployment to cloud hosting (this is a local tool).

## 7. Error Scenarios (Must Be Explicitly Tested)

| #  | Scenario                        | Expected Behavior                                              |
| -- | ------------------------------- | -------------------------------------------------------------- |
| E1 | No internet connection          | "No internet connection. Check your network and try again."    |
| E2 | Missing / invalid API key       | "HuggingFace API token is missing or invalid. Set it in Settings or .env." |
| E3 | GPU unavailable                 | Falls back to CPU with a warning: "No GPU detected, using CPU. Generation will be slower." |
| E4 | CUDA error                      | "GPU error encountered. Falling back to CPU." + log full trace |
| E5 | Out of memory (VRAM/RAM)        | "Not enough memory for this configuration. Try a smaller image size or switch to cloud engine." |
| E6 | Model download failure          | "Failed to download model. Check internet and disk space."     |
| E7 | Corrupted model cache           | "Model cache appears corrupted. Delete `~/.cache/huggingface/...` and retry." |
| E8 | Invalid / empty prompt          | "Please enter a prompt before generating."                     |
| E9 | Timeout / interrupted generation| "Generation timed out or was interrupted. Try again."          |
| E10| Permission error on image save  | "Cannot save image to `images/`. Check folder permissions."    |

## 8. Non-Functional Requirements

- **Startup time**: < 5 seconds to UI ready (model loading is deferred).
- **Generation feedback**: progress bar or spinner visible within 1 second of clicking Generate.
- **Memory**: idle RAM < 500 MB; local engine loaded only when selected.
- **Logging**: all operations logged via `logging` module to `logs/` + console.
- **Security**: no secrets in code, `.env` gitignored, API tokens never logged.
