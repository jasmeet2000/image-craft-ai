#!/usr/bin/env bash
echo "==================================="
echo "     Starting Image Craft AI"
echo "==================================="
echo ""
python -m src.ui.app || {
    echo ""
    echo "[ERROR] Failed to start. Make sure you have activated the conda environment:"
    echo "       conda activate imagecraft"
    echo ""
    exit 1
}
