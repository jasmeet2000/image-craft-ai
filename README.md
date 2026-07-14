# ✨ Image Craft AI

> A modern, premium AI image generator built with Python and Gradio.

![Image Craft AI](https://img.shields.io/badge/Status-Under_Development-orange)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Gradio](https://img.shields.io/badge/Gradio-5.33.0-FF7C00)
![PyTorch](https://img.shields.io/badge/PyTorch-CUDA_Enabled-EE4C2C)

**Image Craft AI** is a cross-platform, beautifully designed AI image generator that supports both cloud-based generation (HuggingFace API) and local generation (HuggingFace Diffusers + PyTorch) with seamless, dynamic switching right in the UI.

### 🌟 Features Completed (Up to Phase 8)

- **Dual-Engine Architecture**: Dynamically swap between `HuggingFace Cloud` and `Local Diffusion` without restarting the app.
- **Hardware Auto-Detection**: Automatically detects your CPU, CUDA (NVIDIA), or MPS (Apple Silicon) hardware and optimizes PyTorch accordingly.
- **Local VRAM Optimization**: Explicit CPU offloading and VRAM cache clearing enables the local engine (`sd-turbo`) to run flawlessly on 4GB VRAM cards like the GTX 1650.
- **Premium UI**: Built with Gradio, featuring a custom CSS theme, an integrated generation history gallery, and native progress indicators.
- **Bomb-proof Error Handling**: Gracefully catches network timeouts and Out of Memory (OOM) errors, providing clear, actionable feedback to the user instead of hanging or crashing.
- **Extensive Test Suite**: 50+ unit and UI smoke tests ensuring the application remains stable as new features are added.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.

### 2. Setup Environment
```bash
# Create and activate conda environment
conda create -n imagecraft python=3.10.20 -y
conda activate imagecraft

# Install dependencies (includes PyTorch with CUDA 12.1 and Diffusers)
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy the example config
cp .env.example .env
```
Edit the `.env` file and insert your HuggingFace API token if you want to use the cloud engine.

### 4. Run the Application
```bash
python -m src.ui.app
```
The app will launch and automatically open in your default web browser at `http://127.0.0.1:7860`.

---

## 📚 Documentation

The project is thoroughly documented. Check out the `docs/` folder:
- [PRD (Product Requirements)](docs/PRD.md)
- [Architecture](docs/Architecture.md)
- [Development Phases](docs/Phases.md)
- [Project Memory & State](docs/Memory.md)
- [Technical Rules](docs/Rules.md)

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
