# SatQuery AI: Model Weights & Foundation Registry

This directory contains instructions and checkpoint mounts for the specialist foundation models integrated into SatQuery AI.

## Specialist Model Checkpoints

| Specialist | Upstream Model / HF Repo | Input Modality | Capabilities | Recommended Precision |
| :--- | :--- | :--- | :--- | :--- |
| **GeoChat** | `MBZUAI/geochat-7b` | Single Optical / Multispectral | VQA, Scene Captioning, Description | 4-bit (NF4) / BF16 |
| **GeoGround** | Custom RS Grounding / `OpenDataLab/GeoGround` | Single Optical / Aerial | Text-Guided Bounding Box & Mask Localization | FP16 / FP32 |
| **Change-Agent** | `Change-Agent/change-diff-v2` | Bi-temporal Image Pairs | Siamese Change Probability & Otsu Masks | FP16 |
| **ChangeChat** | `ChangeChat/ChangeChat-Adapter` | Bi-temporal Image Pairs | Temporal Reasoned VQA & Dynamics | 4-bit / FP16 |
| **Clay** | `made-with-clay/Clay` | Optical + SAR Pairs | Multi-Sensor Self-Supervised Embeddings | FP16 |
| **Prithvi-EO-2.0** | `ibm-nasa-geospatial/Prithvi-EO-2.0-300M` | Multispectral HLS | Foundation EO Representation | FP16 / BF16 |
| **RemoteCLIP** | `chendelong/RemoteCLIP` | Aerial RGB + Text | Contrastive Alignment & Zero-Shot Retrieval | FP16 |

## Hardware Modes
The backend dynamically adapts based on the `MODEL_MODE` environment variable:
- `local`: Loads checkpoints directly onto CUDA GPUs.
- `api`: Dispatches requests to remote vLLM or Triton model serving endpoints.
- `calibrated_fallback`: Uses high-fidelity remote-sensing computer vision algorithms (CVA, Otsu morphological segmentation, spectral index proxies, and PyTorch tensor operations) ensuring the full application remains 100% operational on any standard machine.
