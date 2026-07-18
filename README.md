# ✨ Image Craft AI

> A modern, premium AI image generator built with Python and Gradio.

![Image Craft AI](https://img.shields.io/badge/Version-1.0.0-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Gradio](https://img.shields.io/badge/Gradio-5.33.0-FF7C00)
![PyTorch](https://img.shields.io/badge/PyTorch-CUDA_Enabled-EE4C2C)

**Image Craft AI** is a cross-platform, beautifully designed AI image generator that supports both cloud-based generation (HuggingFace API) and local generation (HuggingFace Diffusers + PyTorch) with seamless, dynamic switching right in the UI.

### 🎥 Demo Video

[Watch the Demo Video](https://drive.google.com/file/d/1vDiXCVipqjeALe5rdCVrpL63iqHjzd-d/view?usp=sharing)

### 🌟 Key Features

- **Dual-Engine Architecture**: Dynamically swap between `HuggingFace Cloud` (powered by FLUX.1-schnell) and `Local Diffusion` without restarting the app.
- **Hardware Auto-Detection**: Automatically detects your CPU, CUDA (NVIDIA), or MPS (Apple Silicon) hardware and optimizes PyTorch accordingly.
- **Local VRAM Optimization**: Explicit CPU offloading and VRAM cache clearing enables the local engine (`sd-turbo`) to run flawlessly on 4GB VRAM cards like the GTX 1650.
- **Premium UI & Auto-Saving**: Built with Gradio, featuring a custom CSS theme, an integrated generation history gallery, native progress indicators, and automatic background saving with configurable compression (PNG/JPG/WEBP).
- **Bomb-proof Error Handling**: Gracefully catches network timeouts and Out of Memory (OOM) errors, providing clear, actionable feedback to the user instead of hanging or crashing.
- **Extensive Test Suite & Coverage**: 60+ unit and integration tests (including real GPU execution) ensuring stability, with **75% overall code coverage** (90%+ on core logic).

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.

### 2. Setup Environment
```bash
# Create and activate conda environment
conda create -n imagecraft python=3.10.20 -y
conda activate imagecraft

# Install dependencies
pip install -r requirements.txt
```
*Note: PyTorch 2.3.1 installed from PyPI automatically supports CUDA 12.1 on Windows/Linux and MPS on macOS. No extra configuration is needed.*

### 3. Configuration
```bash
# Copy the example config
cp .env.example .env
```
Edit the `.env` file and insert your HuggingFace API token if you want to use the cloud engine.

### 4. Run the Application

We've provided one-command startup scripts that will automatically launch the app. Make sure your `imagecraft` conda environment is activated.

**Windows:**
```cmd
start.bat
```

**macOS / Linux:**
```bash
chmod +x start.sh
./start.sh
```

Alternatively, you can always run it directly via Python:
```bash
python -m src.ui.app
```

The app will launch and automatically open in your default web browser at `http://127.0.0.1:7860`.

### ☁️ Future: Cloud Deployment
*Note: Originally, this project was designed to be deployed to Hugging Face Spaces. However, as of mid-2026, Hugging Face updated their free tier policy, requiring a paid PRO subscription for Gradio spaces. For now, deployment is deferred, and the project serves as a comprehensive portfolio piece demonstrating a complete end-to-end local architecture.*

---

## 📚 Documentation

The project is thoroughly documented. Check out the `docs/` folder:
- [PRD (Product Requirements)](docs/PRD.md)
- [Architecture](docs/Architecture.md)
- [Development Phases](docs/Phases.md)
- [Project Memory & State](docs/Memory.md)
- [Profiling & Performance](docs/Profiling.md)
- [Technical Rules](docs/Rules.md)

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
