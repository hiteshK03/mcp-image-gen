# 🎨 MCP Image Gen

### Generate images with AI — locally, privately, no API keys.

> "Generate a cyberpunk city background for my video."
>
> Your AI assistant runs a model on your machine, saves the image, and can even import it straight into DaVinci Resolve.

[![Local AI](https://img.shields.io/badge/Runs-100%25%20Local-00b359.svg)](#-why-this)
[![No API Keys](https://img.shields.io/badge/API%20Keys-None%20Required-brightgreen.svg)](#-why-this)
[![Models](https://img.shields.io/badge/Models-3%20Tiers-blue.svg)](#-three-models-pick-your-speed)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🤔 What Is This?

An MCP server that lets AI assistants (Cursor, Claude, Windsurf) generate images using AI models running **entirely on your machine**. No cloud. No API keys. No subscriptions. No data leaves your computer.

Tell your AI assistant what you need, and it generates the image right there.

---

## ⚡ Why This?

Most image generation MCP servers are wrappers around cloud APIs — DALL-E, Midjourney, Gemini. You need API keys, you pay per image, and your prompts go to someone else's server.

**This one is different:**

- **Zero API keys** — nothing to sign up for, nothing to pay
- **Zero cloud** — models run locally via [OpenVINO](https://docs.openvino.ai/), optimized for CPU
- **Three quality tiers** — pick fast-and-rough or slow-and-detailed, depending on what you need
- **Pipeline-ready** — generated images work directly with DaVinci Resolve MCP and Video Editor MCP

Models download automatically from HuggingFace on first use and stay cached on your machine.

---

## 🎯 Three Models, Pick Your Speed

| | Model | Time | RAM | Resolution | Best for |
|---|-------|------|-----|-----------|----------|
| 🟢 **Fast** | SDXS-512 | ~20 sec | ~2 GB | 512×512 | Quick backgrounds, textures, gradients |
| 🔵 **Quality** | SDXL Turbo | ~30 sec | ~11 GB | 512×512 | Detailed assets, good prompt adherence |
| 🟣 **Premium** | SANA Sprint | ~2.5 min | ~13 GB | 1024×1024 | Highest quality — shines on GPU/NPU hardware |

All times are on CPU. If you have a GPU or NPU, the Premium tier gets dramatically faster.

---

## 🚀 Getting Started

### Step 1 — Set it up

```bash
git clone https://github.com/hiteshK03/mcp-image-gen.git
cd mcp-image-gen
bash setup.sh
```

### Step 2 — Tell your AI assistant about it

Add to `.cursor/mcp.json` (or equivalent):

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

### Step 3 — Ask for images

That's it. Your AI assistant can now generate images. Just ask:

```
"Generate a sunset gradient background and save it as bg.png"
"Create a dark tech UI mockup for my intro"
"Make a thank-you card with gold on black for my outro"
```

---

## 🔁 Part of a Video Production Pipeline

This server is designed to work alongside other MCP tools for a fully automated workflow:

```
You: "I need a cyberpunk background for the intro"

  1. mcp-image-gen  →  generates the image locally
  2. DaVinci Resolve MCP  →  imports it into the media pool
  3. DaVinci Resolve MCP  →  places it on the timeline, scales to fit

All automatic. One conversation.
```

| Server | Role |
|--------|------|
| **This (mcp-image-gen)** | Generate images locally — backgrounds, textures, overlays, graphics |
| [**DaVinci Resolve MCP**](https://github.com/hiteshK03/davinci-resolve-mcp) | Control Resolve — import media, edit timelines, render, local AI |
| **Video Editor MCP** | File-based video processing — overlays, transitions, compositing |

The generated images are regular files. They work with `import_media` (Resolve), `add_image_overlay` (Video Editor), or anything else that accepts an image path.

---

## 🛠️ Tools

### `generate_image`

Generate an image from a text prompt.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `prompt` | ✅ | What you want the image to look like |
| `output` | ✅ | Where to save it (PNG recommended) |
| `model` | | `sdxs-512`, `sdxl-turbo` (default), or `sana-sprint` |
| `width` | | Custom width in pixels |
| `height` | | Custom height in pixels |
| `seed` | | Fix the random seed for reproducible results |

### `list_image_models`

Returns all available models with specs, estimated times, and whether each is currently loaded in memory.

---

## 📋 Requirements

- Python 3.10+
- 2–13 GB RAM depending on which model you use
- No GPU required (but Premium tier benefits from one)

---

## 📄 License

MIT — use it however you want.
