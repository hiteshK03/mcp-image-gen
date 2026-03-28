"""
Core image generation logic using OpenVINO pipelines.

Supports three model tiers:
  - sdxs-512:     OVStableDiffusionPipeline   (rupeshs/sdxs-512-0.9-openvino)
  - sdxl-turbo:   OVStableDiffusionXLPipeline (rupeshs/sdxl-turbo-openvino-int8)
  - sana-sprint:  OVDiffusionPipeline         (rupeshs/sana-sprint-0.6b-openvino-int4)

Models are downloaded from HuggingFace on first use and cached locally by the
HuggingFace Hub library (~/.cache/huggingface/).
"""

import logging
import os
import time

log = logging.getLogger("mcp-image-gen")

MODELS = {
    "sdxs-512": {
        "hf_id": "rupeshs/sdxs-512-0.9-openvino",
        "pipeline_class": "OVStableDiffusionPipeline",
        "default_width": 512,
        "default_height": 512,
        "default_steps": 1,
        "guidance_scale": 1.0,
    },
    "sdxl-turbo": {
        "hf_id": "rupeshs/sdxl-turbo-openvino-int8",
        "pipeline_class": "OVStableDiffusionXLPipeline",
        "default_width": 512,
        "default_height": 512,
        "default_steps": 1,
        "guidance_scale": 0.0,
    },
    "sana-sprint": {
        "hf_id": "rupeshs/sana-sprint-0.6b-openvino-int4",
        "pipeline_class": "OVDiffusionPipeline",
        "default_width": 1024,
        "default_height": 1024,
        "default_steps": 2,
        "guidance_scale": None,
    },
}


def load_pipeline(model_key: str, model_dir: str | None = None):
    """Load an OpenVINO pipeline for the given model tier.

    Args:
        model_key: One of 'sdxs-512', 'sdxl-turbo', 'sana-sprint'.
        model_dir: Optional local directory with pre-downloaded model files.

    Returns:
        An OpenVINO diffusion pipeline ready for inference.
    """
    cfg = MODELS[model_key]
    cls_name = cfg["pipeline_class"]
    source = model_dir if (model_dir and os.path.isdir(model_dir)) else cfg["hf_id"]

    log.info("Loading %s from %s...", cls_name, source)

    if cls_name == "OVStableDiffusionPipeline":
        from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionPipeline
        return OVStableDiffusionPipeline.from_pretrained(source, ov_config={"CACHE_DIR": ""})

    if cls_name == "OVStableDiffusionXLPipeline":
        from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionXLPipeline
        return OVStableDiffusionXLPipeline.from_pretrained(source, ov_config={"CACHE_DIR": ""})

    if cls_name == "OVDiffusionPipeline":
        from optimum.intel.openvino import OVDiffusionPipeline
        return OVDiffusionPipeline.from_pretrained(source, device="CPU")

    raise ValueError(f"Unknown pipeline class: {cls_name}")


def generate(
    pipeline,
    model_key: str,
    prompt: str,
    output_path: str,
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run inference and save the resulting image.

    Args:
        pipeline: A loaded OpenVINO diffusion pipeline.
        model_key: Which model tier this pipeline is for (used for defaults).
        prompt: Text prompt describing the desired image.
        output_path: Where to save the generated PNG/JPG.
        width: Output width (defaults to model's native resolution).
        height: Output height (defaults to model's native resolution).
        steps: Number of inference steps (defaults to model's optimal value).
        seed: Random seed for reproducibility.

    Returns:
        Dict with model, output path, dimensions, steps, seed, and time_seconds.
    """
    import torch

    cfg = MODELS[model_key]
    width = width or cfg["default_width"]
    height = height or cfg["default_height"]
    steps = steps or cfg["default_steps"]

    generator = torch.Generator().manual_seed(seed) if seed is not None else None

    kwargs = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": steps,
    }
    if cfg["guidance_scale"] is not None:
        kwargs["guidance_scale"] = cfg["guidance_scale"]
    if generator is not None:
        kwargs["generator"] = generator

    log.info("Generating %dx%d image with %d steps (model=%s)...", width, height, steps, model_key)
    t0 = time.perf_counter()
    result = pipeline(**kwargs)
    gen_time = time.perf_counter() - t0

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    result.images[0].save(output_path)
    log.info("Generated in %.1fs -> %s", gen_time, output_path)

    return {
        "model": model_key,
        "output": os.path.abspath(output_path),
        "width": width,
        "height": height,
        "steps": steps,
        "seed": seed,
        "time_seconds": round(gen_time, 2),
    }
