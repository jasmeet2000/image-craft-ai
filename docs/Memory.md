# Memory — Image Craft AI

> This file is the single source of truth for project state. Updated at the end of every phase.

---

## Project Identity

| Field              | Value                                                  |
| ------------------ | ------------------------------------------------------ |
| Project name       | Image Craft AI                                         |
| Root directory     | `c:\Users\jasme\OneDrive\Documents\Image Craft AI`     |
| Python             | 3.10.20, conda env `imagecraft`                        |
| UI framework       | Gradio 5.33.0                                          |
| Priority engine    | HuggingFace Inference API (cloud, free tier)           |
| HF model (cloud)   | `stabilityai/stable-diffusion-xl-base-1.0`            |
| Local model        | `stabilityai/sd-turbo`                                 |
| Dev OS             | Windows 10.0.26200                                     |
| Dev GPU            | NVIDIA GeForce GTX 1650, 4.0 GB VRAM                   |

---

## Environment Setup

```bash
# Windows
start.bat

# macOS / Linux
./start.sh
```

---

## Phase Status

| Phase | Name                            | Status      | Date       |
| ----- | ------------------------------- | ----------- | ---------- |
| 0     | Clarification                   | ✅ Complete | 2026-07-13 |
| 1     | Planning (PRD, Rules, Memory)   | ✅ Complete | 2026-07-13 |
| 2     | Architecture & Structure        | ✅ Complete | 2026-07-13 |
| 3     | Config & Hardware Detection     | ✅ Complete | 2026-07-13 |
| 4     | Engine Interface + First Engine | ✅ Complete | 2026-07-13 |
| 5     | UI Skeleton                     | ✅ Complete | 2026-07-13 |
| 6     | Second Engine + Switching       | ✅ Complete | 2026-07-13 |
| 7     | UX Polish                       | ✅ Complete | 2026-07-14 |
| 8     | Error Handling Hardening        | ✅ Complete | 2026-07-14 |
| 9     | Performance Pass                | ✅ Complete | 2026-07-14 |
| 10    | Testing                         | ✅ Complete | 2026-07-14 |
| 11    | Packaging                       | ✅ Complete | 2026-07-14 |
| 12    | Final Review                    | ✅ Complete | 2026-07-14 |

---

## Architecture Summary

```
Gradio UI (src/ui/app.py)
    ├─ Engine Dropdown
    ├─ Generation History Gallery
    ↓ handle_generate(request)
GenerationService (src/services/generation_service.py)
    ├─ validate
    ├─ get_engine(request.engine_override) → generate
    └─ HistoryService.save_result
Engine Registry (src/engines/registry.py)
    ├─(if huggingface_cloud)→ HuggingFaceCloudEngine (HF Inference API)
    └─(if local_diffusion)──→ LocalDiffusionEngine (Diffusers + PyTorch)
```

---

## Final Review (Phase 12)

All Product Requirements Document (PRD) Acceptance Criteria have been met:

- [x] **AC1**: User can generate an image from a text prompt via HF Inference API.
- [x] **AC2**: User can generate an image from a text prompt via local sd-turbo.
- [x] **AC3**: Switching engine changes generation target without code edits (via UI override or `.env`).
- [x] **AC4**: UI shows loading state during generation and never freezes.
- [x] **AC5**: All error scenarios produce user-friendly messages (Timeout, OOM, Network, API limit).
- [x] **AC6**: Generated images are saved to `images/` with metadata (via `HistoryService`).
- [x] **AC7**: Gallery displays past generations and persists across restarts.
- [x] **AC8**: `python -m src.config` prints detected hardware correctly.
- [x] **AC9**: App launches on Windows/Mac/Linux natively via `start.bat` or `start.sh`.
- [x] **AC10**: Adding a mock engine requires only one new file + one config entry (verified in tests).

### Future Work (TODOs)
While v1 is complete, future iterations may consider:
1. **Persistent SQLite DB for History**: Currently, history is session-based in Gradio + file saving. A proper DB would allow searching/filtering past images.
2. **Inpainting/Image-to-Image**: Extend `ImageGenerator` ABC to support base images.
3. **Queue Generation**: Allow batch queueing for long overnight generation sessions.

---

## Key Decisions Log

| Date       | Decision                                           | Rationale                                    |
| ---------- | -------------------------------------------------- | -------------------------------------------- |
| 2026-07-13 | Cloud-first (HF Inference API)                     | Free tier, no upfront cost                   |
| 2026-07-13 | `sd-turbo` for local engine                        | Fits perfectly in 4 GB VRAM                  |
| 2026-07-14 | `engine_override` in GenerationRequest             | Allows UI to switch engines dynamically without modifying the global config singleton. |
| 2026-07-14 | `HistoryService` for auto-saving                   | Prevents memory bloat in Gradio state and permanently archives generations locally. |

---

## Test Results

```
62 passed, 6 warnings in ~3 mins (due to real GPU diffusion execution)
Project coverage: 75%
- Core logic is fully covered.
```

---

## Handoff

The project is fully complete and packaged. To start the application, simply run:
- Windows: `start.bat`
- Mac/Linux: `./start.sh`

The codebase is highly modular, with strict SRP rules governing the `services/` and `engines/` separation. Any developer looking to add a new AI engine (e.g., OpenAI DALL-E, Midjourney API, local Flux) simply needs to implement `src/engines/base.py` and register it in `registry.py`.
