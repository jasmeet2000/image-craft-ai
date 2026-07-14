# Design Document — Image Craft AI

> Written against the real UI skeleton (Phase 5). Updated as the UI evolves.

---

## 1. Layout Overview

The app uses a **two-column layout** inside a centered 1200px container:

```
┌──────────────────────────────────────────────────────────┐
│                  ✨ Image Craft AI                        │
│    Generate stunning images from text descriptions       │
├────────────────────┬─────────────────────────────────────┤
│   INPUT COLUMN     │        OUTPUT COLUMN                │
│   (scale=2)        │        (scale=3)                    │
│                    │                                     │
│  ┌──────────────┐  │  ┌──────────────────────────────┐   │
│  │ Prompt       │  │  │                              │   │
│  │ (3 lines)    │  │  │                              │   │
│  └──────────────┘  │  │     Generated Image          │   │
│  ┌──────────────┐  │  │     (min 400px height)       │   │
│  │ Neg. Prompt  │  │  │                              │   │
│  │ (2 lines)    │  │  │                              │   │
│  └──────────────┘  │  └──────────────────────────────┘   │
│                    │  ┌──────────────────────────────┐   │
│  ▸ Settings ──────┐│  │ Generation Info (readonly)   │   │
│  │ Width  Height ││  │ Engine / Time / Seed / etc.  │   │
│  │ Steps  Guidance│  └──────────────────────────────┘   │
│  │ Seed          ││                                     │
│  └───────────────┘│                                     │
│                    │                                     │
│  ┌──────────────┐  │                                     │
│  │ ✨ Generate   │  │                                     │
│  │   (primary)   │  │                                     │
│  └──────────────┘  │                                     │
├────────────────────┴─────────────────────────────────────┤
│  Engine: huggingface_cloud · Model: sdxl-base-1.0 · ✅   │
└──────────────────────────────────────────────────────────┘
```

## 2. Theme & Styling

| Property       | Value                                        |
| -------------- | -------------------------------------------- |
| Theme base     | `gr.themes.Soft`                             |
| Primary hue    | Violet                                       |
| Secondary hue  | Indigo                                       |
| Neutral hue    | Slate                                        |
| Font           | Inter (Google Fonts)                         |
| Max width      | 1200px, centered                             |
| Header         | Gradient text (violet → purple)              |

## 3. Components

### Input Column

| Component        | Type       | ID / Label            | Notes                           |
| ---------------- | ---------- | --------------------- | ------------------------------- |
| Prompt           | Textbox    | `prompt-input`        | 3 lines, required               |
| Negative Prompt  | Textbox    | —                     | 2 lines, optional               |
| Width            | Slider     | —                     | 256–1024, step 64, default 512  |
| Height           | Slider     | —                     | 256–1024, step 64, default 512  |
| Inference Steps  | Slider     | —                     | 1–50, step 1, default 20        |
| Guidance Scale   | Slider     | —                     | 1.0–20.0, step 0.5, default 7.5|
| Seed             | Textbox    | —                     | Empty = random                  |
| Generate Button  | Button     | `generate-btn`        | Primary variant, large          |

Settings (Width through Seed) are inside a collapsible **Accordion** labeled "Generation Settings" — collapsed by default to keep the UI clean for casual users.

### Output Column

| Component       | Type      | ID / Label          | Notes                        |
| --------------- | --------- | ------------------- | ---------------------------- |
| Generated Image | Image     | `output-image`      | PIL type, download button    |
| Generation Info | Textbox   | —                   | Read-only, 4 lines          |

### Status Bar

A single-line Markdown bar at the bottom showing:
- Active engine name
- Active model name
- HF token status (✅ Set / ❌ Not set)

## 4. Interactions

| Trigger                  | Action                                     |
| ------------------------ | ------------------------------------------ |
| Click "Generate"         | `handle_generate()` → service → engine     |
| Press Enter in Prompt    | Same as clicking Generate                  |
| Generation in progress   | Gradio queue handles async; UI stays live  |
| Error during generation  | `gr.Error()` popup with user-friendly msg  |
| Invalid seed             | `gr.Error("Seed must be a whole number")` |
| Empty prompt             | `gr.Error("Please enter a prompt")`       |

## 5. Non-Blocking Behavior

Gradio's `.queue()` is enabled, which means:
- Generate requests run in a worker thread, not the main UI thread.
- The UI remains interactive while generation is in progress.
- Multiple users (in theory) are queued and served sequentially.

## 6. Future Enhancements (Phase 7)

- Gallery tab with generation history
- Settings page (engine switching, token management)
- Theme toggle (light/dark)
- Progress bar during generation
- Image comparison view
