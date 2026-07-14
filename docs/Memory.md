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
# Run the app
& "$env:USERPROFILE\anaconda3\envs\imagecraft\python.exe" -m src.ui.app

# Run all tests with coverage
& "$env:USERPROFILE\anaconda3\envs\imagecraft\python.exe" -m pytest tests/ --cov=src --cov-report=term-missing

# System check (shows hardware & active engine)
& "$env:USERPROFILE\anaconda3\envs\imagecraft\python.exe" -m src.config
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
| 11    | Packaging                       | ⬜ Pending  |            |
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

### New in Phase 10 (Testing & Coverage)
- **Integration Tests**: Added `tests/integration/test_cloud_engine.py` (mocked) and `tests/integration/test_local_engine_integration.py` (real GPU execution).
- **Unit Tests**: Added `tests/unit/test_history_service.py` to cover new Phase 9 code.
- **Coverage**: Project coverage is now 75% overall, with core services (`registry`, `settings`, `history_service`, `generation_service`, `app.py`) sitting at 90-100%.

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
| 10    | `tests/integration/test_cloud_engine.py` | Created  |
| 10    | `tests/integration/test_local_engine_integration.py` | Created |
| 10    | `tests/unit/test_history_service.py`   | Created  |
| 10    | `requirements.txt`                     | Modified (added pytest-cov) |

---

## Known Issues / Blockers

- First time generating an image with `local_diffusion` takes several minutes as it downloads the ~2-4GB model weights from HuggingFace to your `~/.cache/huggingface` folder. Subsequent runs will be fast.

---

## Next Phase Preview

**Phase 11 — Packaging**: Finalize `README.md` setup instructions for cross-platform usage and prepare the app for end-users.
