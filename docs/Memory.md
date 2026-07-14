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

# Run all tests
& "$env:USERPROFILE\anaconda3\envs\imagecraft\python.exe" -m pytest tests/ -v

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
| 9     | Performance Pass                | ⬜ Pending  |            |
| 10    | Testing                         | ⬜ Pending  |            |
| 11    | Packaging                       | ⬜ Pending  |            |
| 12    | Final Review                    | ⬜ Pending  |            |

---

## Architecture Summary

```
Gradio UI (src/ui/app.py)
    ├─ Engine Dropdown (Phase 7)
    ├─ Generation History Gallery (Phase 7)
    ↓ handle_generate(request)
GenerationService (src/services/generation_service.py)
    ↓ validate → get_engine(request.engine_override) → generate
Engine Registry (src/engines/registry.py)
    ├─(if huggingface_cloud)→ HuggingFaceCloudEngine (HF Inference API)
    └─(if local_diffusion)──→ LocalDiffusionEngine (Diffusers + PyTorch)
```

### UI Features Added in Phase 7
- **Engine Switching Dropdown**: Added directly into the UI (Generation Settings accordion). It dynamically lists all registered engines and passes the selected engine as an override via `GenerationRequest`.
- **Generation History Gallery**: A dedicated `gr.Gallery` component maintains a visual history of all generations in the current session.
- **Progress Tracking**: Hooked into `gr.Progress()` to provide visual feedback during generation.

### Error Handling (Phase 8)
- **HuggingFaceCloudEngine**: Added explicit handling for network `TimeoutError` and `ConnectionError` to prevent the UI from freezing silently during a network outage.
- **LocalDiffusionEngine**: Added explicit handling for `torch.cuda.OutOfMemoryError` to provide a user-friendly suggestion to reduce image dimensions instead of throwing a generic traceback.

---

## Key Decisions Log

| Date       | Decision                                           | Rationale                                    |
| ---------- | -------------------------------------------------- | -------------------------------------------- |
| 2026-07-13 | Cloud-first (HF Inference API)                     | Free tier, no upfront cost                   |
| 2026-07-13 | `sd-turbo` for local engine                        | Fits perfectly in 4 GB VRAM                  |
| 2026-07-14 | `engine_override` in GenerationRequest             | Allows UI to switch engines dynamically without modifying the global config singleton. |

---

## Test Results

```
57 passed, 1 warning in ~12s
- All existing tests passing.
```

---

## Files Created / Modified This Session

| Phase | File                                   | Action   |
| ----- | -------------------------------------- | -------- |
| ...   | (Previous phases omitted for brevity)  |          |
| 7     | `src/models/generation.py`             | Modified (added engine_override) |
| 7     | `src/services/generation_service.py`   | Modified (respect engine_override) |
| 7     | `src/ui/app.py`                        | Modified (Gallery, Dropdown, Progress) |
| 7     | `tests/ui_smoke/test_app.py`           | Modified (updated test signatures) |
| 8     | `src/engines/huggingface_cloud.py`     | Modified (error catching) |
| 8     | `src/engines/local_diffusion.py`       | Modified (error catching) |

---

## Known Issues / Blockers

- First time generating an image with `local_diffusion` will take several minutes as it downloads the ~2-4GB model weights from HuggingFace to your `~/.cache/huggingface` folder. Subsequent runs will be fast.
- HF API token still required if using the cloud engine.

---

## Next Phase Preview

**Phase 9 — Performance Pass**: Profile and optimize. Specifically, ensure the local engine lazily loads perfectly and clears memory completely. Ensure the cloud engine timeout settings are optimal.
