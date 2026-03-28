# mcp-image-gen

A standalone [MCP](https://modelcontextprotocol.io/) server for local AI image generation using OpenVINO. No API keys required — runs entirely on your hardware.

## Models

| Tier | Model | Resolution | CPU Time | RAM | Best For |
|------|-------|-----------|----------|-----|----------|
| **Fast** | SDXS-512 | 512x512 | ~20s | ~2 GB | Backgrounds, textures, gradients |
| **Quality** | SDXL Turbo | 512x512 | ~30s | ~11 GB | Detailed images, good prompt adherence |
| **Premium** | SANA Sprint | 1024x1024 | ~2.5 min | ~13 GB | Highest quality assets (best with GPU/NPU) |

All models use [OpenVINO](https://docs.openvino.ai/) for optimized CPU inference. Models download automatically from HuggingFace on first use.

## Setup

```bash
git clone https://github.com/<your-username>/mcp-image-gen.git
cd mcp-image-gen
bash setup.sh
```

## Cursor Configuration

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-image-gen": {
      "command": "/path/to/mcp-image-gen/venv/bin/python",
      "args": ["/path/to/mcp-image-gen/server.py"]
    }
  }
}
```

## Tools

### `generate_image`

Generate an image from a text prompt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | yes | Text description of the image |
| `output` | string | yes | Output file path (PNG recommended) |
| `model` | string | no | `sdxs-512`, `sdxl-turbo` (default), or `sana-sprint` |
| `width` | int | no | Image width (default: model native) |
| `height` | int | no | Image height (default: model native) |
| `seed` | int | no | Random seed for reproducibility |

### `list_image_models`

Returns available models with specs, estimated times, and whether each is currently loaded in memory.

## Usage with Other MCP Servers

The generated images are regular files that work with any MCP tool:

- **DaVinci Resolve MCP**: `import_media(path)` to add to the media pool
- **Video Editor MCP**: `add_image_overlay(image)` or `create_video_from_images`

The Cursor agent orchestrates across servers automatically.

## Requirements

- Python 3.10+
- ~2–13 GB RAM depending on model tier
- x86_64 CPU with AVX2 (Intel or AMD)

## License

MIT
