# Video Output Support

This fork extends the [upstream worker-comfyui](https://github.com/runpod-workers/worker-comfyui) to handle video outputs from ComfyUI workflows.

## What Changed

### `handler.py`

Added video output handling that mirrors the existing image output logic:

1. **New data structure** (line 525):
   ```python
   videos_output_data = []
   ```

2. **Video detection and processing** (lines 738-825):
   - Detects `videos` key in node outputs
   - Skips temporary videos (`type == "temp"`)
   - Fetches video bytes via `/view` endpoint
   - Uploads to S3 if `BUCKET_ENDPOINT_URL` is set, otherwise returns base64

3. **Updated output logic** (lines 865-888):
   - Adds `videos` array to response
   - Includes video count in completion log
   - Handles edge cases (no images, no videos, errors)

### `src/extra_model_paths.yaml`

Added paths for video model discovery:
```yaml
diffusion_models: models/diffusion_models/
text_encoders: models/text_encoders/
```

### `Dockerfile`

Commented out model download commands to keep image size small (models loaded from network volume instead).

### `examples/runpod-wan-video.json`

Sample WAN 2.2 text-to-video workflow for testing.

---

## API Response Format

### With S3 bucket configured:
```json
{
  "images": [...],
  "videos": [
    {
      "filename": "ComfyUI_00001.mp4",
      "type": "s3_url",
      "data": "https://bucket.s3.amazonaws.com/..."
    }
  ]
}
```

### Without S3 (base64):
```json
{
  "videos": [
    {
      "filename": "ComfyUI_00001.mp4",
      "type": "base64",
      "data": "AAAAIGZ0eXBpc29tAAACAGl..."
    }
  ]
}
```

---

## Supported Video Nodes

Any ComfyUI node that outputs to the `videos` key will be captured, including:
- `SaveVideo`
- `CreateVideo` → `SaveVideo`
- VHS video combine nodes
- Any custom video output nodes

Temp videos (previews) are automatically skipped.
