#!/usr/bin/env python3
"""
Standalone MCP server for local AI image generation.

Three model tiers via OpenVINO (no API keys required):
  - sdxs-512:     Fast tier   (~20s CPU, ~2GB RAM, 512x512)
  - sdxl-turbo:   Quality tier (~30s CPU, ~11GB RAM, 512x512)
  - sana-sprint:  Premium tier (~2.5min CPU, ~13GB RAM, 1024x1024)

Models download automatically from HuggingFace on first use.
Pipelines are cached in-process after first load for faster subsequent calls.

Usage:
  python server.py                     # stdio transport (default)
  python server.py --transport sse     # SSE transport for remote access
"""

import logging
import os
import sys
import time
from typing import Optional

from mcp.server.fastmcp import FastMCP

from generate import MODELS, load_pipeline, generate as run_generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("mcp-image-gen")

mcp = FastMCP(
    "mcp-image-gen",
    instructions="Local AI image generation using OpenVINO. Three tiers: sdxs-512 (fast), sdxl-turbo (quality), sana-sprint (premium). No API keys required.",
)

_pipeline_cache: dict[str, object] = {}


def _get_pipeline(model_key: str):
    if model_key not in _pipeline_cache:
        log.info("Loading model %s (first use, this may take a moment)...", model_key)
        t0 = time.perf_counter()
        _pipeline_cache[model_key] = load_pipeline(model_key)
        log.info("Model %s loaded in %.1fs", model_key, time.perf_counter() - t0)
    return _pipeline_cache[model_key]


@mcp.tool()
def generate_image(
    prompt: str,
    output: str,
    model: str = "sdxl-turbo",
    width: Optional[int] = None,
    height: Optional[int] = None,
    seed: Optional[int] = None,
) -> str:
    """Generate an image from a text prompt using local AI models (no API key required).

    Three model tiers available:
      - sdxs-512:    Fast, ~20s on CPU, 512x512. Best for backgrounds, textures, gradients.
      - sdxl-turbo:  Quality, ~30s on CPU, 512x512. Good prompt adherence and detail.
      - sana-sprint: Premium, ~2.5min on CPU, 1024x1024. Best quality, ideal with GPU/NPU.

    The output image can be used directly with other MCP tools:
      - DaVinci Resolve: import_media(path) to add to media pool
      - Video Editor: add_image_overlay(image) or create_video_from_images

    Args:
        prompt: Text description of the image to generate.
        output: Output file path (PNG recommended). Parent directories are created automatically.
        model: Model tier - 'sdxs-512', 'sdxl-turbo' (default), or 'sana-sprint'.
        width: Image width in pixels. Default depends on model (512 or 1024).
        height: Image height in pixels. Default depends on model (512 or 1024).
        seed: Random seed for reproducible generation.

    Returns:
        JSON string with generation details: model, output path, dimensions, time.
    """
    if model not in MODELS:
        available = ", ".join(MODELS.keys())
        raise ValueError(f"Unknown model '{model}'. Available: {available}")

    output = os.path.abspath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)

    pipeline = _get_pipeline(model)
    result = run_generate(pipeline, model, prompt, output, width, height, None, seed)

    import json
    return json.dumps(result, indent=2)


@mcp.tool()
def list_image_models() -> str:
    """List available local AI image generation models with capabilities, speed, and resource requirements.

    Returns details about each model tier including resolution, estimated generation time,
    RAM usage, and recommended use cases. Also reports which models are currently loaded in memory.
    """
    import json

    models = []
    for key, cfg in MODELS.items():
        models.append({
            "id": key,
            "resolution": f"{cfg['default_width']}x{cfg['default_height']}",
            "steps": cfg["default_steps"],
            "loaded": key in _pipeline_cache,
        })

    info = [
        {
            "id": "sdxs-512",
            "name": "SDXS-512 (Fast)",
            "tier": "fast",
            "description": "Ultra-fast generation via OpenVINO. Best for backgrounds, textures, gradients.",
            "resolution": "512x512",
            "cpu_time": "~20 seconds",
            "ram": "~2 GB",
            "loaded": "sdxs-512" in _pipeline_cache,
        },
        {
            "id": "sdxl-turbo",
            "name": "SDXL Turbo (Quality)",
            "tier": "quality",
            "description": "High-quality generation via OpenVINO INT8. Good prompt adherence and detail.",
            "resolution": "512x512",
            "cpu_time": "~30 seconds",
            "ram": "~11 GB",
            "loaded": "sdxl-turbo" in _pipeline_cache,
        },
        {
            "id": "sana-sprint",
            "name": "SANA Sprint (Premium)",
            "tier": "premium",
            "description": "Best quality via OpenVINO INT4. Excellent for detailed assets. Best with GPU/NPU hardware.",
            "resolution": "1024x1024",
            "cpu_time": "~2.5 minutes",
            "ram": "~13 GB",
            "loaded": "sana-sprint" in _pipeline_cache,
        },
    ]

    return json.dumps(info, indent=2)


if __name__ == "__main__":
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    mcp.run(transport=transport)
