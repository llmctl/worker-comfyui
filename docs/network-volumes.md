# Network Volumes & Model Paths

This document explains where to place model files when using a RunPod **Network Volume** with your ComfyUI serverless endpoint.

## Key Difference: Pods vs Serverless

| Context               | Network Volume Mount Point |
|-----------------------|---------------------------|
| **Pods**              | `/workspace`              |
| **Serverless Endpoints** | `/runpod-volume`       |

Since you're adding a network volume to a **serverless endpoint**, your models must be placed under `/runpod-volume`. However, when populating the volume via a **Pod**, you'll work with `/workspace` — they point to the same physical storage.

---

## Model Path Configuration

The `src/extra_model_paths.yaml` defines the expected paths:

```yaml
runpod_worker_comfy:
  base_path: /runpod-volume
  checkpoints: models/checkpoints/
  clip: models/clip/
  clip_vision: models/clip_vision/
  configs: models/configs/
  controlnet: models/controlnet/
  embeddings: models/embeddings/
  loras: models/loras/
  upscale_models: models/upscale_models/
  vae: models/vae/
  unet: models/unet/
  diffusion_models: models/diffusion_models/
  text_encoders: models/text_encoders/
```

---

## Expected Directory Structure

When you create a **Pod** with the same network storage attached and upload your models, place them in this structure:

```text
/workspace/                              # ← Pod view (same physical volume)
└── models/
    ├── checkpoints/      # e.g., your_model.safetensors
    ├── clip/             # CLIP text encoder models
    ├── clip_vision/      # CLIP vision models
    ├── configs/          # Model configs (.yaml, .json)
    ├── controlnet/       # ControlNet models
    ├── diffusion_models/ # Diffusion models (FLUX, etc.)
    ├── embeddings/       # Textual inversion embeddings
    ├── loras/            # LoRA files
    ├── text_encoders/    # Text encoder models (T5, etc.)
    ├── unet/             # UNet models
    ├── upscale_models/   # Upscaling models
    └── vae/              # VAE models
```

When the **serverless endpoint** runs with the same network volume attached, it sees:

```text
/runpod-volume/models/checkpoints/your_model.safetensors  → ✅ Recognized
/runpod-volume/models/loras/your_lora.safetensors         → ✅ Recognized
```

> **Note:** Only create the subdirectories you actually need; empty or missing folders are fine.

---

## Workflow to Populate Models

1. **Create a Pod** in the **same region** as your network volume
2. Attach the network volume to the Pod (it mounts at `/workspace`)
3. Download/upload your models to `/workspace/models/<model_type>/`
4. Stop the Pod
5. Attach the **same network volume** to your serverless endpoint

---

## Supported File Extensions

ComfyUI only recognizes files with specific extensions when scanning model directories.

| Model Type       | Supported Extensions                           |
|------------------|------------------------------------------------|
| Checkpoints      | `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin` |
| LoRAs            | `.safetensors`, `.pt`                          |
| VAE              | `.safetensors`, `.pt`, `.bin`                  |
| CLIP             | `.safetensors`, `.pt`, `.bin`                  |
| ControlNet       | `.safetensors`, `.pt`, `.pth`, `.bin`          |
| Embeddings       | `.safetensors`, `.pt`, `.bin`                  |
| Upscale Models   | `.safetensors`, `.pt`, `.pth`                  |

Files with other extensions (e.g., `.txt`, `.zip`) are **ignored** by ComfyUI's model discovery.

---

## Common Mistakes to Avoid

| ❌ Wrong                                          | ✅ Correct                                         |
|--------------------------------------------------|---------------------------------------------------|
| `/runpod-volume/checkpoints/model.safetensors`   | `/runpod-volume/models/checkpoints/model.safetensors` |
| `/runpod-volume/models/model.safetensors`        | `/runpod-volume/models/checkpoints/model.safetensors` |
| `/workspace/checkpoints/model.safetensors`       | `/workspace/models/checkpoints/model.safetensors` |

**Key points:**
- Always include the `models/` directory in the path
- Models must be in the appropriate subdirectory for their type

---

## Debugging

If models aren't detected, set the environment variable on your serverless endpoint:

```bash
NETWORK_VOLUME_DEBUG=true
```

This will log diagnostic information about what the worker finds in the network volume paths, including:
- Whether the volume is mounted
- What directories exist
- What files are discovered

### Common Issues

- **Wrong root directory**: Models placed directly under `/runpod-volume/checkpoints/...` instead of `/runpod-volume/models/checkpoints/...`
- **Incorrect extensions**: Files without one of the supported extensions are skipped
- **Empty directories**: No actual model files present in the expected folders
- **Volume not attached**: Endpoint created without selecting a network volume under **Advanced → Select Network Volume**
