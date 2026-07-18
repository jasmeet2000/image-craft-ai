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
| HF model (cloud)   | `black-forest-labs/FLUX.1-schnell`            |
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

## Known Bugs & Fixes

### Black Images from Local Diffusion on GTX 16-Series GPUs
- **Discovered**: 2026-07-14
- **Symptom**: `local_diffusion` engine produces solid black PNG images. `huggingface_cloud` with the same prompt works correctly.
- **Root Cause**: GTX 16-series GPUs (1650, 1660) do not properly support `float16` precision for certain operations (scaled dot-product attention, VAE decoding) in Stable Diffusion pipelines. When values overflow fp16 limits, the output tensor fills with `NaN`, which PIL renders as solid black pixels.
- **Fix applied in** [`local_diffusion.py`](file:///c:/Users/jasme/OneDrive/Documents/Image Craft AI/src/engines/local_diffusion.py):
  1. **FP32 Fallback** (line 60–65): Detects GTX 16-series by name and forces `torch.float32` + `variant=None` instead of `float16`/`fp16`.
  2. **VAE Upcasting** (line 77): Calls `pipeline.upcast_vae()` on CUDA to force VAE into FP32 (helps other edge cases).
  3. **NaN Guard** (line 185–189): After generation, checks `torch.isnan(tensor).any()` and raises a clear `RuntimeError` instead of silently saving a black image.
- **Scope**: Only affects GPUs with incomplete fp16 support. Modern GPUs (RTX 20-series and newer) are unaffected. If a new local model is added and black images reappear on other hardware, check this NaN guard first.

---

## Key Decisions Log

| Date       | Decision                                           | Rationale                                    |
| ---------- | -------------------------------------------------- | -------------------------------------------- |
| 2026-07-13 | Cloud-first (HF Inference API)                     | Free tier, no upfront cost                   |
| 2026-07-13 | `sd-turbo` for local engine                        | Fits perfectly in 4 GB VRAM                  |
| 2026-07-14 | `engine_override` in GenerationRequest             | Allows UI to switch engines dynamically without modifying the global config singleton. |
| 2026-07-14 | `HistoryService` for auto-saving                   | Prevents memory bloat in Gradio state and permanently archives generations locally. |
| 2026-07-14 | Switch default cloud model to FLUX.1-schnell       | Upgraded from SDXL to FLUX.1-schnell for superior free-tier output quality. Default UI resolution bumped to 1024x1024 to match native FLUX resolution. |
| 2026-07-14 | UI Overhaul — Premium Glassmorphic Dark Theme      | Complete UI rework: glassmorphic cards with `backdrop-filter: blur`, layered dark backgrounds (`#0c0a1a`→`#151228`→`#1e1b2e`), animated particles in header/empty state, shimmer generation animation, slide-in toast notifications, hover micro-interactions on all interactive elements, full-width responsive layout (1400px max, stacks at 768px), gallery moved to full-width section with click-to-reload-prompt, status bar restyled as pill badges. Theme uses `gr.themes.Soft` with custom violet `gr.themes.Color` palette. |
| 2026-07-14 | Explicit Light/Dark Themes via `gr.themes.Base`    | Replaced custom CSS background hardcoding with proper Gradio CSS variables (`var(--background-fill-primary)`) and an explicit `gr.themes.Base()` definition with pure Light (#FAFAFA/#FFFFFF) and true Dark (#0F0F14/#1A1A22) `neutral_hue` palettes to fix washed-out gray artifacts. |
| 2026-07-15 | FP32 fallback for GTX 16-series in local engine    | GTX 1650/1660 GPUs produce NaN tensors (black images) with fp16. Auto-detect by GPU name and force fp32. SD-Turbo fits in 4GB VRAM even at fp32. |
| 2026-07-18 | Demo Video & Marketing Scripts                     | Added demo video link to `README.md` and generated LinkedIn product showcase narration scripts for project promotion. |

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
