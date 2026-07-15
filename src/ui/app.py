"""Gradio UI for Image Craft AI.

This module contains ONLY presentation logic — component layout,
input parsing, and output formatting. All business logic lives in
the service and engine layers.
"""

from __future__ import annotations
import logging

import gradio as gr

from src.config.settings import get_settings
from src.engines.registry import list_engines
from src.models.generation import GenerationRequest
from src.services.generation_service import GenerationService
from src.services.image_storage_service import ImageStorageService
from src.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom CSS — Premium dark glassmorphic theme
# ---------------------------------------------------------------------------

_CUSTOM_CSS = """
/* ── Base container ─────────────────────────────────────────── */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 24px 32px !important;
    background: transparent !important;
}

/* ── Animated particle canvas (header + empty state) ────────── */
@keyframes float-particle {
    0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
    25% { transform: translateY(-20px) translateX(10px); opacity: 0.8; }
    50% { transform: translateY(-10px) translateX(-5px); opacity: 0.5; }
    75% { transform: translateY(-25px) translateX(15px); opacity: 0.7; }
}

@keyframes float-particle-2 {
    0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.2; }
    33% { transform: translateY(-15px) translateX(-12px); opacity: 0.6; }
    66% { transform: translateY(-8px) translateX(8px); opacity: 0.4; }
}

@keyframes glow-pulse {
    0%, 100% { opacity: 0.4; filter: blur(40px); }
    50% { opacity: 0.7; filter: blur(50px); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes slide-in-toast {
    0% { transform: translateX(120%); opacity: 0; }
    10% { transform: translateX(0); opacity: 1; }
    90% { transform: translateX(0); opacity: 1; }
    100% { transform: translateX(120%); opacity: 0; }
}

@keyframes spin-slow {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ── Header ─────────────────────────────────────────────────── */
#header-section {
    position: relative;
    text-align: center;
    padding: 32px 20px 24px !important;
    margin-bottom: 8px;
    overflow: hidden;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

#header-section::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 120px;
    background: radial-gradient(ellipse, rgba(147, 51, 234, 0.3) 0%, transparent 70%);
    animation: glow-pulse 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.header-particles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
}

.header-particles .particle {
    position: absolute;
    border-radius: 50%;
    background: rgba(168, 85, 247, 0.5);
}

.header-particles .particle:nth-child(1) {
    width: 4px; height: 4px; top: 30%; left: 15%;
    animation: float-particle 6s ease-in-out infinite;
}
.header-particles .particle:nth-child(2) {
    width: 3px; height: 3px; top: 60%; left: 25%;
    animation: float-particle-2 8s ease-in-out infinite 1s;
}
.header-particles .particle:nth-child(3) {
    width: 5px; height: 5px; top: 40%; left: 70%;
    animation: float-particle 7s ease-in-out infinite 2s;
}
.header-particles .particle:nth-child(4) {
    width: 3px; height: 3px; top: 55%; left: 80%;
    animation: float-particle-2 5s ease-in-out infinite 0.5s;
}
.header-particles .particle:nth-child(5) {
    width: 4px; height: 4px; top: 25%; left: 50%;
    animation: float-particle 9s ease-in-out infinite 3s;
}
.header-particles .particle:nth-child(6) {
    width: 3px; height: 3px; top: 70%; left: 40%;
    animation: float-particle-2 6s ease-in-out infinite 1.5s;
}

#header-section h1 {
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 40%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px !important;
    position: relative;
    z-index: 1;
    letter-spacing: -0.02em;
}

#header-section p {
    color: var(--body-text-color) !important; opacity: 0.8;
    font-size: 1.05rem !important;
    position: relative;
    z-index: 1;
    margin: 0 !important;
}

/* ── Glassmorphic cards ─────────────────────────────────────── */
.glass-card {
    background: var(--background-fill-primary) !important;
    backdrop-filter: blur(16px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(16px) saturate(1.4) !important;
    border: 1px solid var(--block-border-color) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

.glass-card:hover {
    border-color: var(--primary-400) !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.35),
        0 0 20px rgba(147, 51, 234, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
}

/* ── Input fields inside cards ──────────────────────────────── */
.glass-card textarea,
.glass-card input[type="text"],
.glass-card .wrap {
    background: var(--input-background-fill) !important;
    border: 1px solid var(--block-border-color) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.glass-card textarea:focus,
.glass-card input[type="text"]:focus {
    border-color: var(--primary-500) !important;
    box-shadow: 0 0 12px rgba(147, 51, 234, 0.15) !important;
    outline: none !important;
}

/* ── Section labels inside input card ───────────────────────── */
.section-label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #a78bfa !important;
    margin-bottom: 8px !important;
    margin-top: 16px !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.section-label:first-child {
    margin-top: 0 !important;
}

/* ── Generate button ────────────────────────────────────────── */
#generate-btn {
    min-height: 56px !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 50%, #6d28d9 100%) !important;
    border: 1px solid rgba(147, 51, 234, 0.3) !important;
    box-shadow:
        0 4px 14px rgba(147, 51, 234, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-top: 16px !important;
    cursor: pointer !important;
    position: relative;
    overflow: hidden;
}

#generate-btn::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s ease;
}

#generate-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 8px 25px rgba(147, 51, 234, 0.45),
        0 0 30px rgba(147, 51, 234, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(168, 85, 247, 0.5) !important;
}

#generate-btn:hover::after {
    left: 100%;
}

#generate-btn:active {
    transform: translateY(1px) scale(0.98) !important;
    box-shadow:
        0 2px 8px rgba(147, 51, 234, 0.3),
        inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.1s ease !important;
}

/* ── Output area ────────────────────────────────────────────── */
.output-card {
    background: var(--background-fill-primary) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--block-border-color) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    transition: border-color 0.3s ease !important;
    min-height: 480px;
}

.output-card:hover {
    border-color: var(--primary-400) !important;
}

#output-image {
    border-radius: 12px !important;
    overflow: hidden !important;
    min-height: 380px;
    background: var(--background-fill-secondary) !important;
}

#output-image img {
    border-radius: 12px !important;
}

/* ── Empty state ────────────────────────────────────────────── */
.empty-state-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 380px;
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background: var(--background-fill-secondary);
    border: 1px dashed var(--block-border-color);
}

.empty-state-particles {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
}

.empty-state-particles .ep {
    position: absolute;
    border-radius: 50%;
    background: rgba(147, 51, 234, 0.3);
}

.empty-state-particles .ep:nth-child(1) {
    width: 6px; height: 6px; top: 20%; left: 20%;
    animation: float-particle 7s ease-in-out infinite;
}
.empty-state-particles .ep:nth-child(2) {
    width: 4px; height: 4px; top: 60%; left: 75%;
    animation: float-particle-2 9s ease-in-out infinite 1s;
}
.empty-state-particles .ep:nth-child(3) {
    width: 5px; height: 5px; top: 40%; left: 50%;
    animation: float-particle 6s ease-in-out infinite 2s;
}
.empty-state-particles .ep:nth-child(4) {
    width: 3px; height: 3px; top: 70%; left: 30%;
    animation: float-particle-2 8s ease-in-out infinite 0.5s;
}
.empty-state-particles .ep:nth-child(5) {
    width: 4px; height: 4px; top: 30%; left: 65%;
    animation: float-particle 10s ease-in-out infinite 3s;
}

.empty-state-icon {
    position: relative;
    z-index: 1;
    width: 64px; height: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state-icon svg {
    width: 100%; height: 100%;
    stroke: #a78bfa;
    stroke-width: 1.5;
    fill: none;
}

.empty-state-text {
    position: relative;
    z-index: 1;
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 500;
    margin: 0;
}

.empty-state-sub {
    position: relative;
    z-index: 1;
    color: var(--body-text-color); opacity: 0.6;
    font-size: 0.85rem;
    margin-top: 6px;
}

/* ── Generation loading shimmer ─────────────────────────────── */
.generating-shimmer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 380px;
    border-radius: 12px;
    background: var(--background-fill-secondary);
    position: relative;
    overflow: hidden;
}

.generating-shimmer::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(147, 51, 234, 0.06) 25%,
        rgba(147, 51, 234, 0.12) 50%,
        rgba(147, 51, 234, 0.06) 75%,
        transparent 100%
    );
    background-size: 200% 100%;
    animation: shimmer 2s ease-in-out infinite;
}

.generating-spinner {
    width: 48px; height: 48px;
    border: 3px solid rgba(147, 51, 234, 0.2);
    border-top-color: #a855f7;
    border-radius: 50%;
    animation: spin-slow 1.2s linear infinite;
    margin-bottom: 16px;
    position: relative;
    z-index: 1;
}

.generating-text {
    color: #c4b5fd;
    font-size: 1rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

.generating-sub {
    color: var(--body-text-color); opacity: 0.6;
    font-size: 0.8rem;
    margin-top: 4px;
    position: relative;
    z-index: 1;
}

/* ── Toast notification ─────────────────────────────────────── */
#toast-container {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 10000;
    pointer-events: none;
}

.toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: var(--background-fill-primary);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--primary-400);
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(147, 51, 234, 0.1);
    color: #e2e8f0;
    font-size: 0.9rem;
    font-weight: 500;
    animation: slide-in-toast 4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    pointer-events: auto;
    min-width: 280px;
}

.toast-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
}

.toast-body {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.toast-title {
    font-weight: 600;
    color: #c4b5fd;
}

.toast-detail {
    font-size: 0.8rem;
    color: #94a3b8;
}

/* ── Generation info ────────────────────────────────────────── */
#gen-info {
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 0.82rem !important;
    background: var(--input-background-fill) !important;
    border: 1px solid var(--block-border-color) !important;
}

/* ── Gallery section ────────────────────────────────────────── */
.gallery-section {
    background: var(--background-fill-primary) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    border: 1px solid var(--block-border-color) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    margin-top: 16px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
    transition: border-color 0.3s ease !important;
}

.gallery-section:hover {
    border-color: var(--primary-400) !important;
}

.gallery-title {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 0 12px 0 !important;
}

.gallery-title h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #c4b5fd !important;
    letter-spacing: 0.03em;
    margin: 0 !important;
}

.gallery-title p {
    font-size: 0.8rem !important;
    color: var(--body-text-color) !important; opacity: 0.6;
    margin: 4px 0 0 0 !important;
}

#history-gallery {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}

#history-gallery .thumbnail-item,
#history-gallery .gallery-item {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid var(--block-border-color) !important;
    transition: all 0.25s ease !important;
    aspect-ratio: 1 / 1 !important;
    cursor: pointer !important;
}

#history-gallery .thumbnail-item:hover,
#history-gallery .gallery-item:hover {
    border-color: var(--primary-500) !important;
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 8px 20px rgba(147, 51, 234, 0.2) !important;
}

#history-gallery .thumbnail-item img,
#history-gallery .gallery-item img {
    object-fit: cover !important;
    aspect-ratio: 1 / 1 !important;
}

/* ── Status bar ─────────────────────────────────────────────── */
.status-bar-container {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 12px 0 0 0 !important;
}

.status-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    padding: 8px 0;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
}

.badge:hover {
    transform: translateY(-1px);
}

.badge-engine {
    background: rgba(99, 102, 241, 0.15);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.25);
}

.badge-model {
    background: rgba(147, 51, 234, 0.15);
    color: #c4b5fd;
    border: 1px solid rgba(147, 51, 234, 0.25);
}

.badge-success {
    background: rgba(34, 197, 94, 0.12);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.badge-error {
    background: rgba(239, 68, 68, 0.12);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

/* ── Accordion styling ──────────────────────────────────────── */
.glass-card .accordion {
    border: 1px solid var(--block-border-color) !important;
    border-radius: 10px !important;
    background: var(--background-fill-secondary) !important;
    margin-top: 8px !important;
}

/* ── Slider styling ─────────────────────────────────────────── */
.glass-card input[type="range"] {
    accent-color: #9333ea !important;
}

/* ── Main layout row ────────────────────────────────────────── */
#main-row {
    gap: 20px !important;
    align-items: flex-start !important;
}

/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 1024px) {
    .gradio-container {
        padding: 16px 16px !important;
    }

    #header-section h1 {
        font-size: 2rem !important;
    }

    .glass-card, .output-card {
        padding: 16px !important;
    }
}

@media (max-width: 768px) {
    .gradio-container {
        padding: 12px 8px !important;
    }

    #main-row {
        flex-direction: column !important;
    }

    #main-row > .column,
    #main-row > div {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    #header-section h1 {
        font-size: 1.7rem !important;
    }

    #header-section p {
        font-size: 0.9rem !important;
    }

    .glass-card, .output-card {
        padding: 14px !important;
        border-radius: 12px !important;
    }

    #generate-btn {
        min-height: 48px !important;
        font-size: 1rem !important;
    }

    .empty-state-container,
    .generating-shimmer {
        min-height: 260px;
    }

    .status-bar {
        gap: 6px;
    }

    .badge {
        font-size: 0.72rem;
        padding: 5px 10px;
    }

    #toast-container {
        top: 12px;
        right: 12px;
        left: 12px;
    }

    .toast {
        min-width: auto;
    }
}
"""

# ---------------------------------------------------------------------------
# JavaScript for toast notifications and generation animation
# ---------------------------------------------------------------------------

_CUSTOM_JS = """
function() {
    // Create toast container
    if (!document.getElementById('toast-container')) {
        const tc = document.createElement('div');
        tc.id = 'toast-container';
        document.body.appendChild(tc);
    }
}
"""

_TOAST_JS = """
function(...args) {
    const container = document.getElementById('toast-container');
    if (container) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `
            <span class="toast-icon">✨</span>
            <div class="toast-body">
                <span class="toast-title">Image Generated</span>
                <span class="toast-detail">Your creation is ready!</span>
            </div>
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4200);
    }
    return args;
}
"""


# ---------------------------------------------------------------------------
# HTML snippets
# ---------------------------------------------------------------------------

_EMPTY_STATE_HTML = """
<div class="empty-state-container">
    <div class="empty-state-particles">
        <div class="ep"></div>
        <div class="ep"></div>
        <div class="ep"></div>
        <div class="ep"></div>
        <div class="ep"></div>
    </div>
    <div class="empty-state-icon">
        <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="10" width="52" height="40" rx="4" />
            <circle cx="22" cy="26" r="5" />
            <polyline points="6,42 20,32 30,38 42,24 58,36" />
        </svg>
    </div>
    <p class="empty-state-text">Your generated image will appear here</p>
    <p class="empty-state-sub">Enter a prompt and click Generate to get started</p>
</div>
"""

_GENERATING_HTML = """
<div class="generating-shimmer">
    <div class="generating-spinner"></div>
    <p class="generating-text">Creating your image…</p>
    <p class="generating-sub">This may take a few moments</p>
</div>
"""


# ---------------------------------------------------------------------------
# UI construction helpers
# ---------------------------------------------------------------------------


def _build_header() -> None:
    """Render the app header with title, subtitle, and animated particles."""
    gr.HTML(
        """
        <div id="header-section">
            <div class="header-particles">
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
            </div>
            <h1>✨ Image Craft AI</h1>
            <p>Generate stunning images from text descriptions —
               powered by HuggingFace cloud inference.</p>
        </div>
        """,
    )


def _build_prompt_inputs() -> tuple[gr.Textbox, gr.Textbox]:
    """Build the prompt and negative prompt text inputs.

    Returns:
        Tuple of (prompt, negative_prompt) Textbox components.
    """
    gr.Markdown("Prompt", elem_classes=["section-label"])
    prompt = gr.Textbox(
        label="Prompt",
        placeholder="Describe the image you want to create…",
        lines=3,
        max_lines=6,
        elem_id="prompt-input",
        show_label=False,
    )
    gr.Markdown("Negative Prompt", elem_classes=["section-label"])
    negative_prompt = gr.Textbox(
        label="Negative Prompt (optional)",
        placeholder="Things to avoid in the image…",
        lines=2,
        max_lines=4,
        show_label=False,
    )
    return prompt, negative_prompt


def _build_param_controls(
    settings: object,
) -> tuple[gr.Dropdown, gr.Slider, gr.Slider, gr.Slider, gr.Slider, gr.Textbox]:
    """Build the generation parameter controls.

    Args:
        settings: Application settings for default values.

    Returns:
        Tuple of (engine, width, height, steps, guidance, seed) components.
    """
    with gr.Row():
        engine_dropdown = gr.Dropdown(
            choices=list_engines(),
            value=settings.engine,
            label="Engine",
            interactive=True,
        )
    with gr.Row():
        width = gr.Slider(
            minimum=256, maximum=1024, value=settings.default_width,
            step=64, label="Width",
        )
        height = gr.Slider(
            minimum=256, maximum=1024, value=settings.default_height,
            step=64, label="Height",
        )
    with gr.Row():
        steps = gr.Slider(
            minimum=1, maximum=50, value=settings.default_steps,
            step=1, label="Inference Steps",
        )
        guidance = gr.Slider(
            minimum=1.0, maximum=20.0, value=settings.default_guidance_scale,
            step=0.5, label="Guidance Scale",
        )
    seed = gr.Textbox(
        label="Seed (optional)",
        placeholder="Leave empty for random",
        value="",
    )
    return engine_dropdown, width, height, steps, guidance, seed


def _build_output_panel() -> tuple[gr.HTML, gr.Image, gr.Textbox]:
    """Build the output panel with empty state, image display, and info.

    Returns:
        Tuple of (empty_state_html, output_image, info_text) components.
    """
    empty_state = gr.HTML(
        value=_EMPTY_STATE_HTML,
        elem_id="empty-state",
    )
    output_image = gr.Image(
        label="Generated Image",
        type="pil",
        elem_id="output-image",
        show_download_button=True,
        visible=False,
    )
    info_text = gr.Textbox(
        label="Generation Info",
        interactive=False,
        lines=4,
        visible=False,
        elem_id="gen-info",
    )
    return empty_state, output_image, info_text


def _build_gallery() -> gr.Gallery:
    """Build the generation history gallery."""
    return gr.Gallery(
        label="Generation History",
        show_label=False,
        elem_id="history-gallery",
        columns=6,
        rows=2,
        object_fit="cover",
        height="auto",
    )


def _build_status_bar(settings: object) -> None:
    """Render the styled status bar with pill badges.

    Args:
        settings: Application settings.
    """
    engine_label = settings.engine.replace("_", " ").title()
    model_label = settings.hf_model.split("/")[-1]
    token_cls = "badge-success" if settings.hf_api_token else "badge-error"
    token_icon = "✅" if settings.hf_api_token else "❌"
    token_text = f"Token {token_icon}"

    gr.HTML(
        f"""
        <div class="status-bar">
            <span class="badge badge-engine">⚡ {engine_label}</span>
            <span class="badge badge-model">🧠 {model_label}</span>
            <span class="badge {token_cls}">{token_text}</span>
        </div>
        """,
        elem_classes=["status-bar-container"],
    )


# ---------------------------------------------------------------------------
# Event handlers (parse UI inputs → call services → format output)
# ---------------------------------------------------------------------------


def _parse_seed(seed_text: str) -> int | None:
    """Parse the seed input from the UI.

    Args:
        seed_text: Raw seed text from the textbox.

    Returns:
        Parsed integer seed or None for random.

    Raises:
        gr.Error: If the seed text is not a valid integer.
    """
    stripped = seed_text.strip() if seed_text else ""
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError:
        raise gr.Error("Seed must be a whole number or leave empty for random.")


def _format_result_info(result: object, request: object) -> str:
    """Format generation result metadata for display.

    Args:
        result: The GenerationResult.
        request: The original GenerationRequest.

    Returns:
        Formatted multi-line info string.
    """
    return (
        f"Engine:    {result.engine}\n"
        f"Time:      {result.generation_time:.2f}s\n"
        f"Size:      {request.width}×{request.height}\n"
        f"Steps:     {request.num_steps}\n"
        f"Guidance:  {request.guidance_scale}\n"
        f"Seed:      {result.seed}"
    )


def _show_generating_state() -> tuple:
    """Show the shimmer animation while generating.

    Returns:
        Updates for (empty_state, output_image, info_text).
    """
    return (
        gr.update(value=_GENERATING_HTML, visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def handle_generate(
    prompt: str,
    negative_prompt: str,
    engine_name: str,
    width: float,
    height: float,
    steps: float,
    guidance: float,
    seed_text: str,
    history: list,
    progress: gr.Progress = gr.Progress(track_tqdm=True),
) -> tuple:
    """Handle the Generate button click.

    Parses UI inputs, delegates to GenerationService, and formats
    the result for display. This is the only bridge between Gradio
    components and the service layer.

    Args:
        prompt: User's text prompt.
        negative_prompt: Things to avoid.
        engine_name: Selected engine from dropdown.
        width: Image width (from slider, comes as float).
        height: Image height (from slider, comes as float).
        steps: Inference steps (from slider).
        guidance: Guidance scale (from slider).
        seed_text: Seed text (empty string = random).
        history: Current history state list.
        progress: Gradio progress tracker.

    Returns:
        Tuple of (empty_state, image, info, gallery, state) updates.
    """
    seed = _parse_seed(seed_text)

    request = GenerationRequest(
        prompt=prompt,
        negative_prompt=negative_prompt or "",
        width=int(width),
        height=int(height),
        num_steps=int(steps),
        guidance_scale=float(guidance),
        seed=seed,
        engine_override=engine_name,
    )

    service = GenerationService()

    progress(0, desc="Starting generation...")
    try:
        result = service.generate(request)
    except ValueError as exc:
        raise gr.Error(str(exc))
    except RuntimeError as exc:
        raise gr.Error(str(exc))

    logger.info("UI: image generated for prompt '%s'", prompt[:50])

    # Prepend new result to history (newest first)
    new_history = [(result.image_path, prompt)] + (history or [])

    return (
        gr.update(visible=False),                       # hide empty state
        gr.update(value=result.image, visible=True),    # show image
        gr.update(
            value=_format_result_info(result, request),
            visible=True,
        ),                                              # show info
        new_history,                                    # gallery
        new_history,                                    # state
    )


def _handle_gallery_select(
    evt: gr.SelectData,
    history: list,
) -> tuple:
    """Handle clicking a gallery thumbnail to reload its prompt.

    Args:
        evt: Gradio select event with index.
        history: Current history state.

    Returns:
        Tuple of (prompt, empty_state, output_image) updates.
    """
    if history and evt.index is not None and evt.index < len(history):
        path, prompt_text = history[evt.index]
        try:
            from PIL import Image
            img = Image.open(path)
            return (
                prompt_text,
                gr.update(visible=False),
                gr.update(value=img, visible=True),
            )
        except Exception:
            logger.warning("Could not load gallery image: %s", path)
            return prompt_text, gr.update(), gr.update()
    return gr.update(), gr.update(), gr.update()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> gr.Blocks:
    """Create and configure the Gradio application.

    Returns:
        A configured gr.Blocks app ready to launch.
    """
    settings = get_settings()

    # Custom violet palette for the primary accent
    violet = gr.themes.Color(
        c50="#faf5ff", c100="#f3e8ff", c200="#e9d5ff", c300="#d8b4fe",
        c400="#c084fc", c500="#a855f7", c600="#9333ea", c700="#7c3aed",
        c800="#6d28d9", c900="#5b21b6", c950="#3b0764",
    )
    
    # Custom neutral palette spanning true white to near-black
    neutral = gr.themes.Color(
        c50="#FAFAFA", c100="#F5F5F7", c200="#E5E5E5", c300="#D4D4D4",
        c400="#A3A3A3", c500="#737373", c600="#525252", c700="#404040",
        c800="#2A2A33", c900="#1A1A22", c950="#0F0F14",
    )

    theme = gr.themes.Base(
        primary_hue=violet,
        secondary_hue=violet,
        neutral_hue=neutral,
        font=gr.themes.GoogleFont("Inter"),
    ).set(
        # --- Light Theme ---
        body_background_fill="#FAFAFA",
        background_fill_primary="#FFFFFF",
        background_fill_secondary="#F5F5F7",
        block_background_fill="#FFFFFF",
        block_border_width="1px",
        block_border_color="#E5E5E5",
        body_text_color="#1A1A1A",
        block_label_text_color="#525252",
        input_background_fill="#F5F5F7",
        
        # --- Dark Theme ---
        body_background_fill_dark="#0F0F14",
        background_fill_primary_dark="#1A1A22",
        background_fill_secondary_dark="#1E1E26",
        block_background_fill_dark="#1A1A22",
        block_border_color_dark="#2A2A33",
        body_text_color_dark="#F5F5F5",
        block_label_text_color_dark="#A3A3A3",
        input_background_fill_dark="#1E1E26",

        # --- Shared Buttons ---
        button_primary_background_fill="linear-gradient(135deg, *primary_600, *primary_700)",
        button_primary_background_fill_hover="linear-gradient(135deg, *primary_500, *primary_600)",
        button_primary_text_color="white",
    )

    with gr.Blocks(
        theme=theme,
        css=_CUSTOM_CSS,
        js=_CUSTOM_JS,
        title="Image Craft AI — AI Image Generator",
        fill_width=True,
    ) as app:
        # Header
        _build_header()

        # Main two-column layout
        with gr.Row(elem_id="main-row", equal_height=False):
            # Left: Input card
            with gr.Column(scale=5, elem_classes=["glass-card"]):
                prompt, negative_prompt = _build_prompt_inputs()

                with gr.Accordion(
                    "⚙️  Generation Settings",
                    open=False,
                ):
                    engine_dropdown, width, height, steps, guidance, seed = (
                        _build_param_controls(settings)
                    )

                generate_btn = gr.Button(
                    "✨  Generate Image",
                    variant="primary",
                    size="lg",
                    elem_id="generate-btn",
                )

            # Right: Output area
            with gr.Column(scale=6, elem_classes=["output-card"]):
                empty_state, output_image, info_text = _build_output_panel()

        # Full-width gallery section
        with gr.Column(elem_classes=["gallery-section"]):
            gr.Markdown(
                "### 📸 Generation History\n"
                "Click a thumbnail to load its prompt",
                elem_classes=["gallery-title"],
            )
            history_gallery = _build_gallery()
            history_state = gr.State([])

        # Status bar
        _build_status_bar(settings)

        # ── Event wiring ──────────────────────────────────────
        input_components = [
            prompt, negative_prompt, engine_dropdown, width, height,
            steps, guidance, seed, history_state,
        ]
        output_components = [
            empty_state, output_image, info_text,
            history_gallery, history_state,
        ]

        # Show shimmer animation, then generate
        generate_btn.click(
            fn=_show_generating_state,
            inputs=None,
            outputs=[empty_state, output_image, info_text],
        ).then(
            fn=handle_generate,
            inputs=input_components,
            outputs=output_components,
        ).then(
            fn=None,
            inputs=None,
            outputs=None,
            js=_TOAST_JS,
        )

        # Enter in prompt triggers the same chain
        prompt.submit(
            fn=_show_generating_state,
            inputs=None,
            outputs=[empty_state, output_image, info_text],
        ).then(
            fn=handle_generate,
            inputs=input_components,
            outputs=output_components,
        ).then(
            fn=None,
            inputs=None,
            outputs=None,
            js=_TOAST_JS,
        )

        # Gallery click → load prompt + show image
        history_gallery.select(
            fn=_handle_gallery_select,
            inputs=[history_state],
            outputs=[prompt, empty_state, output_image],
        )

        # Load persisted history on startup
        def init_history():
            """Load saved generation history from disk."""
            svc = ImageStorageService()
            hist = svc.load_history()
            return hist, hist

        app.load(fn=init_history, outputs=[history_gallery, history_state])

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Initialize logging and launch the Gradio app."""
    settings = get_settings()
    setup_logging(settings.log_dir, settings.log_level)

    logger.info("Starting Image Craft AI...")
    app = create_app()
    app.queue()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
