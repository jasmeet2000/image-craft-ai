# Design Document — Image Craft AI

> Written against the real UI skeleton (Phase 5). Updated after the UI overhaul for premium dark glassmorphic design.

---

## 1. Layout Overview

The app uses a **two-column glassmorphic layout** inside a `fill_width` container capped at 1400px:

```
┌────────────────────────── 1400px max ──────────────────────────┐
│                                                                 │
│            ✨ Image Craft AI  (glow + particles)                │
│     Generate stunning images from text descriptions             │
│                                                                 │
├──────────────────────────┬──────────────────────────────────────┤
│   INPUT CARD (scale=5)   │     OUTPUT CARD (scale=6)           │
│   ┌────────────────────┐ │   ┌────────────────────────────────┐│
│   │ PROMPT             │ │   │                                ││
│   │ Describe the image │ │   │   ○ ○ ○  (animated particles)  ││
│   ├────────────────────┤ │   │                                ││
│   │ NEGATIVE PROMPT    │ │   │  🖼 Your generated image       ││
│   │ Things to avoid... │ │   │     will appear here           ││
│   ├────────────────────┤ │   │                                ││
│   │ ▸ ⚙ Settings       │ │   │  Enter a prompt and click     ││
│   │   Engine | W | H   │ │   │  Generate to get started      ││
│   │   Steps | Guidance │ │   │                                ││
│   │   Seed             │ │   └────────────────────────────────┘│
│   ├────────────────────┤ │   ┌────────────────────────────────┐│
│   │ ✨ Generate Image   │ │   │ Generation Info (monospace)    ││
│   │ (glow hover/press) │ │   │ Engine / Time / Seed / etc.   ││
│   └────────────────────┘ │   └────────────────────────────────┘│
├──────────────────────────┴──────────────────────────────────────┤
│  📸 Generation History — Click a thumbnail to load its prompt   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ 1:1  │ │ 1:1  │ │ 1:1  │ │ 1:1  │ │ 1:1  │ │ 1:1  │       │
│  │cover │ │cover │ │cover │ │cover │ │cover │ │cover │        │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────────────────────────────────┤
│       [⚡ HF Cloud]  [🧠 FLUX.1-schnell]  [Token ✅]           │
└─────────────────────────────────────────────────────────────────┘
```

### Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| > 1024px   | Side-by-side columns, full gallery row |
| 768–1024px | Reduced padding, 3-column gallery |
| < 768px    | Columns stack vertically, 2-column gallery, compact badges |

## 2. Theme & Styling

| Property                  | Value                                                           |
| ------------------------- | --------------------------------------------------------------- |
| Theme base                | `gr.themes.Soft`                                                |
| Primary hue               | Custom violet palette (`#a855f7` → `#3b0764`)                  |
| Secondary hue             | Indigo                                                          |
| Neutral hue               | Slate                                                           |
| Font                      | Inter (Google Fonts)                                            |
| Container                 | `fill_width=True`, CSS `max-width: 1400px`, centered           |
| Page background           | `#0c0a1a` (deep navy-black)                                    |
| Card background (primary) | `#151228` (elevated dark indigo)                                |
| Card background (secondary)| `#1e1b2e` (lighter panel)                                     |
| Input fields              | `#0f0e1c` (recessed dark)                                      |
| Card style                | **Glassmorphism** — `backdrop-filter: blur(16px)`, semi-transparent bg, inset top highlight, purple-tinted border |
| Border radius             | 16px cards, 12px buttons/images, 10px inputs — consistent      |
| Hover effects             | Cards glow on hover, buttons lift + shadow, gallery items scale |

### Header Treatment

- Gradient text: `linear-gradient(135deg, #a855f7, #7c3aed, #6366f1)`
- Radial glow behind title with `glow-pulse` animation
- 6 animated floating particles with staggered timing

## 3. Components

### Input Column (Glassmorphic Card)

| Component        | Type       | ID / Label            | Notes                           |
| ---------------- | ---------- | --------------------- | ------------------------------- |
| Prompt           | Textbox    | `prompt-input`        | 3 lines, required, label hidden (CSS section label) |
| Negative Prompt  | Textbox    | —                     | 2 lines, optional, label hidden |
| Width            | Slider     | —                     | 256–1024, step 64, default 1024 |
| Height           | Slider     | —                     | 256–1024, step 64, default 1024 |
| Inference Steps  | Slider     | —                     | 1–50, step 1, default 20       |
| Guidance Scale   | Slider     | —                     | 1.0–20.0, step 0.5, default 7.5|
| Seed             | Textbox    | —                     | Empty = random                  |
| Generate Button  | Button     | `generate-btn`        | Primary, large, gradient glow, hover lift + shimmer sweep, active press-down |

Settings (Width through Seed) are inside a collapsible **Accordion** labeled "⚙️ Generation Settings" — collapsed by default.

### Output Column

| Component       | Type      | ID / Label          | Notes                            |
| --------------- | --------- | ------------------- | -------------------------------- |
| Empty State     | HTML      | `empty-state`       | Animated particles + friendly text, hidden after first generation |
| Generated Image | Image     | `output-image`      | PIL type, download button, hidden until first generation |
| Generation Info | Textbox   | `gen-info`          | Read-only, monospace font, hidden until first generation |

### Empty State
Before any generation, the output area shows:
- 5 animated floating particles
- Image icon (SVG)
- "Your generated image will appear here"
- "Enter a prompt and click Generate to get started"

### Generation Animation
While generating, a **shimmer overlay** replaces the empty state:
- Full-width gradient sweep animation
- Purple spinner ring
- "Creating your image…" text

### Gallery Section (Full Width)

| Component       | Type      | ID / Label          | Notes                        |
| --------------- | --------- | ------------------- | ---------------------------- |
| Gallery         | Gallery   | `history-gallery`   | 6 columns, `object-fit: cover`, 1:1 aspect ratio, rounded thumbnails |

Gallery thumbnails have:
- Hover: lift + scale + purple border glow
- Click: loads prompt into input + shows image in output

### Status Bar (Pill Badges)

Styled as centered flex row of badge pills:
- `⚡ Engine` — indigo badge
- `🧠 Model` — violet badge
- `Token ✅/❌` — green/red badge
- Hover: subtle lift

## 4. Interactions

| Trigger                  | Action                                             |
| ------------------------ | -------------------------------------------------- |
| Click "Generate"         | Shimmer animation → `handle_generate()` → toast    |
| Press Enter in Prompt    | Same as clicking Generate                          |
| Generation completes     | Toast notification slides in (top-right), auto-fades after 4s |
| Click gallery thumbnail  | Loads prompt into input + shows image in output    |
| Generation in progress   | Shimmer overlay with spinner, no "Loading..." text |
| Error during generation  | `gr.Error()` popup with user-friendly message      |

### Toast Notifications
On successful generation:
- Slides in from right (top-right corner)
- Shows "✨ Image Generated — Your creation is ready!"
- Auto-fades out after 4 seconds
- Glassmorphic card style matching theme

## 5. Non-Blocking Behavior

Gradio's `.queue()` is enabled, which means:
- Generate requests run in a worker thread, not the main UI thread.
- The UI remains interactive while generation is in progress.
- Multiple users (in theory) are queued and served sequentially.

## 6. Micro-Interactions

| Element           | Hover Effect                                         | Active Effect         |
| ----------------- | ---------------------------------------------------- | --------------------- |
| Glass cards       | Border glows purple, shadow deepens                  | —                     |
| Generate button   | Lifts 2px, shadow expands, shimmer sweep across      | Press down + shrink   |
| Gallery thumbnails| Lift 3px, scale 1.03, purple border glow             | —                     |
| Status badges     | Lift 1px                                             | —                     |
| Input fields      | Border glows purple, subtle shadow                   | —                     |

## 7. Design Tokens

```
Theme Engine:   gr.themes.Base with explicit Color objects for Light/Dark

Light Theme Neutrals:
  Page Bg:      #FAFAFA
  Card Bg:      #FFFFFF
  Secondary:    #F5F5F7
  Borders:      #E5E5E5
  Text:         #1A1A1A (primary) → #525252 (secondary)

Dark Theme Neutrals:
  Page Bg:      #0F0F14
  Card Bg:      #1A1A22
  Secondary:    #1E1E26
  Borders:      #2A2A33
  Text:         #F5F5F5 (primary) → #A3A3A3 (secondary)

Purple palette: #3b0764 → #5b21b6 → #7c3aed → #9333ea → #a855f7 → #c084fc
Success:        #86efac / rgba(34, 197, 94, 0.12)
Error:          #fca5a5 / rgba(239, 68, 68, 0.12)
Radius:         16px (cards) → 12px (buttons/images) → 10px (inputs) → 20px (badges)
Glass:          backdrop-filter: blur(16px) saturate(1.4)
```
