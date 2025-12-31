# Testing Guide

## Overview

This project follows [RunPod's recommended testing approach](https://docs.runpod.io/serverless/workers/development/local-testing) instead of traditional unit tests. RunPod provides built-in testing tools that better simulate the serverless environment.

## Testing Methods

### 1. Basic Testing with Test Input File

The simplest way to test your handler locally:

```bash
python handler.py
```

This will automatically use `test_input.json` if it exists in the root directory.

**Current test files:**
- ✅ `test_input.json` - Simple workflow (no models required)
- ❌ `test_input_flux.json` - FLUX workflow (requires FLUX.1 Dev model)
- ✅ `test_input_simple.json` - Another simple workflow (no models required)

### 2. Inline JSON Testing

Test with inline JSON input:

```bash
python handler.py --test_input '{"input": {"workflow": {...}}}'
```

### 3. Local API Server

Start a local API server that simulates the RunPod environment:

```bash
python handler.py --rp_serve_api
```

Then send requests to `http://localhost:8000`:

```bash
curl -X POST http://localhost:8000/runsync \
  -H "Content-Type: application/json" \
  -d @test_input.json
```

## Test Input Files

### `test_input.json` (Default)
**Model Requirements:** None

A simple workflow using `EmptyLatentImage` that doesn't require any models. Perfect for:
- CI/CD pipelines
- Basic handler validation
- Testing without downloading large model files

### `test_input_flux.json`
**Model Requirements:** FLUX.1 Dev model (`flux1-dev-fp8.safetensors`)

Complete FLUX workflow for testing actual image generation. Requires:
1. FLUX.1 Dev model downloaded to `models/checkpoints/`
2. ComfyUI running locally or in container

See [Customization Guide](docs/customization.md) for model installation instructions.

### `test_input_simple.json`
**Model Requirements:** None

Another minimal workflow for basic testing.

## Workflow Examples

The `test_resources/workflows/` directory contains example workflows for different models:

| Workflow File | Model Required | Notes |
|--------------|----------------|-------|
| `flux_dev_checkpoint_example.json` | FLUX.1 Dev | Full FLUX workflow |
| `workflow_flux1_dev.json` | FLUX.1 Dev | Alternative FLUX workflow |
| `workflow_flux1_schnell.json` | FLUX.1 Schnell | Fast FLUX variant |
| `workflow_sd3.json` | Stable Diffusion 3 | SD3 medium |
| `workflow_sdxl_turbo.json` | SDXL Turbo | Fast SDXL variant |
| `workflow_webp.json` | Various | WebP output format |

## Debugging

Enable debug logging:

```bash
export COMFY_LOG_LEVEL=DEBUG
python handler.py
```

Enable websocket tracing for connection issues:

```bash
export WEBSOCKET_TRACE=true
python handler.py
```

## CI/CD Recommendations

For automated testing without models:

1. Use `test_input.json` (no models required)
2. Test basic handler functionality
3. Validate input/output format
4. Check error handling

For full integration testing with models, use a separate pipeline with model downloads.

## Why No Unit Tests?

This project previously had traditional unit tests but they were removed because:

1. **RunPod provides better testing tools** - Their built-in testing simulates the actual serverless environment
2. **Unit tests were outdated** - They didn't keep up with handler changes
3. **Integration testing is more valuable** - Testing the actual workflow execution is more important than mocking
4. **Simpler maintenance** - Following RunPod's conventions reduces maintenance burden

For testing, use RunPod's recommended approaches documented above.

