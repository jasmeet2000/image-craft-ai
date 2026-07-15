import logging
import sys
from pathlib import Path
from src.config.settings import get_settings
from src.engines.huggingface_cloud import HuggingFaceCloudEngine
from src.models.generation import GenerationRequest
from src.utils.logging_setup import setup_logging

settings = get_settings()
setup_logging(settings.log_dir, settings.log_level)
logger = logging.getLogger(__name__)

engine = HuggingFaceCloudEngine()
req = GenerationRequest(
    prompt="a golden retriever sitting in a sunny park, photorealistic",
    width=1024,
    height=1024,
    num_steps=20, # UI default, should be capped to 4 by our logic
    guidance_scale=7.5
)

import time

for i in range(3):
    print(f"\nGenerating image {i+1}/3...")
    result = engine.generate(req)
    
    # Save using the StorageService, since generation_service is bypassed when calling engine.generate directly
    from src.services.image_storage_service import ImageStorageService
    svc = ImageStorageService()
    saved_path = svc.save_result(result)
    print(f"Successfully generated and saved image: {saved_path}")
    time.sleep(1) # Ensure timestamp diff if needed, but our collision logic should handle it even without sleep

