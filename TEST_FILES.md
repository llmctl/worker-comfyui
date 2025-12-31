# Test Files

This directory contains various test files for the worker-comfyui project.

## Test Input Files

### `test_input.json`
**Model Requirements:** None (uses EmptyLatentImage only)

A simple test workflow that doesn't require any models. Use this for basic testing of the handler without needing to download large model files.

### `test_input_flux.json`
**Model Requirements:** FLUX.1 Dev model (`flux1-dev-fp8.safetensors`)

A complete FLUX workflow example. This requires the FLUX.1 Dev model to be installed. See the [Customization Guide](docs/customization.md) for instructions on adding models.

### `test_input_simple.json`
**Model Requirements:** None

Another simple test workflow for basic validation testing.

## Running Tests

### Unit Tests
The unit tests in `tests/test_handler.py` use mocks and don't require any models:

```bash
python -m unittest discover tests
```

### Integration Tests
To test with actual workflows that require models, ensure you have the necessary models installed first. See the workflow files in `test_resources/workflows/` for model requirements.

## Workflow Files

The `test_resources/workflows/` directory contains example workflows for different model types:

- `flux_dev_checkpoint_example.json` - Requires FLUX.1 Dev
- `workflow_flux1_dev.json` - Requires FLUX.1 Dev  
- `workflow_flux1_schnell.json` - Requires FLUX.1 Schnell
- `workflow_sd3.json` - Requires Stable Diffusion 3
- `workflow_sdxl_turbo.json` - Requires SDXL Turbo
- `workflow_webp.json` - WebP output example
