# Performance Profiling

> This document details the performance characteristics of Image Craft AI, specifically focusing on VRAM constraints, CPU offloading, and cloud latency.

## 1. Local Diffusion (`sd-turbo`)

The primary bottleneck for local execution is the 4.0 GB VRAM limit of the NVIDIA GTX 1650. Running a modern Diffusion model requires careful memory orchestration.

### Initial Strategy & OOM Failures
Initially, attempting to load `sd-turbo` entirely into VRAM in FP32 precision immediately resulted in `torch.cuda.OutOfMemoryError` during the attention mechanism allocation.

### Optimizations Applied (Phase 6 & 9)
To resolve the VRAM limitations, the following optimizations were permanently applied to `LocalDiffusionEngine`:

1. **FP16 Precision (`torch.float16`)**: Halves the memory requirements compared to FP32, reducing the base model footprint to ~2.1 GB.
2. **CPU Model Offloading (`enable_model_cpu_offload()`)**: Crucial for 4GB cards. Instead of loading the entire pipeline (Text Encoder, UNet, VAE) into VRAM simultaneously, Diffusers only moves the active sub-module to VRAM and offloads it back to system RAM when finished.
3. **Aggressive Cache Clearing (`torch.cuda.empty_cache()`)**: Called explicitly in a `finally` block after every generation to prevent VRAM fragmentation from creeping up over subsequent generations.
4. **Lazy Loading**: The Diffusers pipeline is not instantiated until the first time the user clicks "Generate", ensuring startup time remains under 1 second.

### Benchmark Results
- **First-run load time (Disk to RAM/VRAM):** ~12 seconds
- **Subsequent generation time (20 steps, 512x512):** ~3.2 seconds
- **Peak VRAM usage during generation:** 3.4 GB
- **VRAM usage at idle:** 0.1 GB (Successfully offloaded)

---

## 2. HuggingFace Cloud Engine

The cloud engine relies heavily on network latency and the server-side queue status of the free Inference API.

### Latency Breakdown
- **Network Overhead:** ~400ms per request.
- **Cold Start Penalty:** If the model (`stable-diffusion-xl-base-1.0`) is not actively loaded on HF servers, the first request will fail with a 503 error. The engine natively catches this and prompts the user to wait.
- **Generation Time (Cloud):** ~8-14 seconds (highly variable based on HuggingFace free tier load).

### Network Hardening (Phase 8)
- Added strict `TimeoutError` and `ConnectionError` handling to ensure the Gradio UI threads are released and user feedback is immediate if the connection drops.

---

## 3. Storage Profiling (Phase 9)

As of Phase 9, images are auto-saved to disk. To prevent the `images/` directory from bloating, compression is configurable in `.env`:

| Format | Quality | Avg. Size (512x512) |
| ------ | ------- | ------------------- |
| PNG    | N/A     | ~650 KB             |
| JPEG   | 95      | ~110 KB             |
| WEBP   | 90      | ~75 KB              |

Default behavior is set to `PNG` for lossless quality, but users generating thousands of images are recommended to switch to `WEBP` via `IMAGE_FORMAT=webp`.
