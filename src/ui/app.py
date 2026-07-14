"""Gradio UI for Image Craft AI.

This module contains ONLY presentation logic — component layout,
input parsing, and output formatting. All business logic lives in
the service and engine layers.
"""

import logging

import gradio as gr

from src.config.settings import get_settings
from src.engines.registry import list_engines
from src.models.generation import GenerationRequest
from src.services.generation_service import GenerationService
from src.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom CSS for premium look
# ---------------------------------------------------------------------------

_CUSTOM_CSS = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
#header-text {
    text-align: center;
    margin-bottom: 0.5rem;
}
#header-text h1 {
    font-size: 2.2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
#header-text p {
    color: #94a3b8;
    font-size: 1rem;
}
#generate-btn {
    min-height: 48px !important;
    font-size: 1.1rem !important;
}
#output-image {
    min-height: 400px;
    border-radius: 12px;
    overflow: hidden;
}
"""


# ---------------------------------------------------------------------------
# UI construction helpers (each returns component references)
# ---------------------------------------------------------------------------


def _build_header() -> None:
    """Render the app header with title and subtitle."""
    gr.Markdown(
        "# ✨ Image Craft AI\n"
        "Generate stunning images from text descriptions — "
        "powered by HuggingFace cloud inference.",
        elem_id="header-text",
    )


def _build_prompt_inputs() -> tuple[gr.Textbox, gr.Textbox]:
    """Build the prompt and negative prompt text inputs.

    Returns:
        Tuple of (prompt, negative_prompt) Textbox components.
    """
    prompt = gr.Textbox(
        label="Prompt",
        placeholder="Describe the image you want to create...",
        lines=3,
        max_lines=6,
        elem_id="prompt-input",
    )
    negative_prompt = gr.Textbox(
        label="Negative Prompt (optional)",
        placeholder="Things to avoid in the image...",
        lines=2,
        max_lines=4,
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


def _build_output_panel() -> tuple[gr.Image, gr.Textbox]:
    """Build the output image and info panel.

    Returns:
        Tuple of (output_image, info_text) components.
    """
    output_image = gr.Image(
        label="Generated Image",
        type="pil",
        elem_id="output-image",
        show_download_button=True,
    )
    info_text = gr.Textbox(
        label="Generation Info",
        interactive=False,
        lines=4,
    )
    return output_image, info_text


def _build_gallery() -> gr.Gallery:
    """Build the generation history gallery."""
    return gr.Gallery(
        label="Generation History",
        show_label=True,
        elem_id="history-gallery",
        columns=[4],
        rows=[2],
        object_fit="contain",
        height="auto",
    )


def _build_status_bar(settings: object) -> None:
    """Render the engine status bar.

    Args:
        settings: Application settings.
    """
    token_status = "✅ Set" if settings.hf_api_token else "❌ Not set"
    gr.Markdown(
        f"**Engine:** `{settings.engine}` · "
        f"**Model:** `{settings.hf_model}` · "
        f"**HF Token:** {token_status}",
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
        Tuple of (PIL Image, info string, new_history, new_history_state).
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
    
    # Prepend new result to history (so newest is first)
    new_history = [(result.image, prompt)] + (history or [])
    
    return result.image, _format_result_info(result, request), new_history, new_history


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> gr.Blocks:
    """Create and configure the Gradio application.

    Returns:
        A configured gr.Blocks app ready to launch.
    """
    settings = get_settings()

    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="indigo",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    )

    with gr.Blocks(
        theme=theme,
        css=_CUSTOM_CSS,
        title="Image Craft AI — AI Image Generator",
    ) as app:
        _build_header()

        with gr.Row(equal_height=False):
            # Left column: inputs
            with gr.Column(scale=2):
                prompt, negative_prompt = _build_prompt_inputs()
                with gr.Accordion("Generation Settings", open=False):
                    engine_dropdown, width, height, steps, guidance, seed = (
                        _build_param_controls(settings)
                    )
                generate_btn = gr.Button(
                    "✨ Generate Image",
                    variant="primary",
                    size="lg",
                    elem_id="generate-btn",
                )

            # Right column: output
            with gr.Column(scale=3):
                output_image, info_text = _build_output_panel()
                gr.Markdown("### History")
                history_gallery = _build_gallery()
                history_state = gr.State([])

        with gr.Row():
            _build_status_bar(settings)

        # Wire the generate button
        input_components = [
            prompt, negative_prompt, engine_dropdown, width, height,
            steps, guidance, seed, history_state
        ]
        output_components = [output_image, info_text, history_gallery, history_state]
        
        generate_btn.click(
            fn=handle_generate,
            inputs=input_components,
            outputs=output_components,
        )

        # Also trigger on Enter in prompt textbox
        prompt.submit(
            fn=handle_generate,
            inputs=input_components,
            outputs=output_components,
        )

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
