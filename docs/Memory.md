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
| 12    | Final Review                    | ⬜ Pending  |            |

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

### New in Phase 11 (Packaging)
- **Cross-Platform Support**: Simplified `requirements.txt` by removing hardcoded Windows-specific CUDA indices. PyTorch 2.3.1 naturally installs the correct CUDA binaries on Windows/Linux and MPS binaries on macOS natively from PyPI.
- **Startup Scripts**: Created `start.bat` and `start.sh` for one-click startup across all OS environments.
- **README Update**: Added explicit setup and start instructions for multiple operating systems.

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

## Files Created / Modified This Session

| Phase | File                                   | Action   |
| ----- | -------------------------------------- | -------- |
| ...   | (Previous phases omitted for brevity)  |          |
| 11    | `start.bat`                            | Created  |
| 11    | `start.sh`                             | Created  |
| 11    | `requirements.txt`                     | Modified (generalized PyTorch) |
| 11    | `README.md`                            | Modified (cross-OS setup) |

---

## Known Issues / Blockers

- First time generating an image with `local_diffusion` takes several minutes as it downloads the ~2-4GB model weights from HuggingFace to your `~/.cache/huggingface` folder. Subsequent runs will be fast.

---

## Next Phase Preview

**Phase 12 — Final Review**: Review PRD acceptance criteria, finalize any remaining documentation, and mark the project as fully delivered!
