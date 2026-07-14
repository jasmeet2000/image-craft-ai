# Phases — Image Craft AI

> Each phase produces a working checkpoint. No phase is skipped. `Memory.md` is updated at the end of every phase. User says "Continue" before proceeding.

---

## Phase 1 — Planning ✅
**Deliverables**: `PRD.md`, `Rules.md`, `Memory.md`
**Runnable**: Documents reviewed and approved.

---

## Phase 2 — Architecture & Structure ✅
**Deliverables**: `Architecture.md`, `Phases.md`, folder scaffold with `__init__.py` files, `requirements.txt` v1, `.gitignore`, `.env.example`, `LICENSE`, conda env `imagecraft` created.
**Runnable**: `conda activate imagecraft && python -c "import src; print('scaffold OK')"` succeeds.

---

## Phase 3 — Config & Hardware Detection
**Deliverables**:
- `src/config/settings.py` — loads `.env`, validates, exposes typed `Settings` object.
- `src/config/hardware.py` — detects CPU / CUDA / MPS, caches result.
- `src/config/__main__.py` — `python -m src.config` prints detected hardware + loaded config.
- Unit tests for settings loading and hardware detection.

**Runnable**: `python -m src.config` prints detected GPU, Python version, active engine.

---

## Phase 4 — Engine Interface + First Engine (HF Cloud)
**Deliverables**:
- `src/engines/base.py` — `ImageGenerator` ABC.
- `src/engines/huggingface_cloud.py` — HF Inference API implementation.
- `src/engines/registry.py` — engine lookup by config name.
- `src/models/generation.py` — `GenerationRequest`, `GenerationResult` dataclasses.
- `src/services/generation_service.py` — orchestrates engine calls.
- Integration test: generate one image from a script (no UI).

**Runnable**: `python -m src.engines.huggingface_cloud` generates an image and saves to `images/`.

**Prerequisite**: User must have a HuggingFace API token in `.env`.

---

## Phase 5 — UI Skeleton
**Deliverables**:
- `src/ui/app.py` — Gradio app with Generate page wired to HF Cloud engine.
- `docs/Design.md` — written against the real UI, not imagined components.
- UI smoke test.

**Runnable**: `python -m src.ui.app` → browser opens → type prompt → get image.

---

## Phase 6 — Second Engine + Backend Switching
**Deliverables**:
- `src/engines/local_diffusion.py` — local `sd-turbo` engine.
- Config-based switching proven: change `ENGINE` in `.env`, restart, same UI uses different backend.
- Extensibility test: adding a mock engine requires only one file + one config entry.
- Additional requirements for `torch`, `diffusers`, etc. added to `requirements.txt`.

**Runnable**: Switch engine in `.env`, generate image with each, both work.

---

## Phase 7 — UX Polish ✅
**Deliverables**:
- Gallery page with history display.
- `src/services/history_service.py` — save/load generation history.
- Settings page (engine selection, hardware info, API token, theme).
- Progress/loading states during generation.
- Error dialogs (user-facing, not stack traces).

**Runnable**: Full user flow — generate, browse gallery, change settings, see errors handled.

---

## Phase 8 — Error Handling Hardening ✅
**Deliverables**:
- Explicit tests for all 10 error scenarios from PRD §7.
- Graceful degradation paths verified (GPU → CPU fallback).
- Network timeout handling tested.
- All error messages verified to be user-friendly.

**Runnable**: Each error scenario triggered and verified manually or by test.

---

## Phase 9 — Performance Pass ✅
**Deliverables**:
- Model caching (don't reload on every generation).
- Memory cleanup after generation (especially local engine).
- Background workers audit — confirm UI never blocks.
- Image compression options for saved output.
- Profiling results documented.

**Runnable**: Generate multiple images in sequence without memory growth or UI freezes.

---

## Phase 10 — Testing ✅
**Deliverables**:
- Unit tests: config, models, services, utils.
- Integration tests: engine calls (mocked API for cloud, real for local if GPU available).
- Config validation tests.
- UI smoke tests (Gradio test client).
- Coverage report targeting meaningful coverage on `services/` and `engines/`.

**Runnable**: `pytest tests/ -v` passes all tests.

---

## Phase 11 — Packaging ✅
**Deliverables**:
- `README.md` finalized with setup instructions for Windows, macOS, Linux.
- `requirements.txt` finalized with all pins verified.
- Cross-OS run instructions verified (at minimum Windows tested locally).
- One-command startup documented.

**Runnable**: Fresh clone → follow README → app works.

---

## Phase 12 — Final Review ✅
**Deliverables**:
- `Memory.md` closed out.
- Checklist against all PRD acceptance criteria (AC1–AC10).
- Any remaining TODOs documented as future work.
- Project handed off in a state where anyone can pick it up from `Memory.md`.

**Runnable**: All acceptance criteria met, all docs current, no stale TODOs.
