# SatQuery AI: Remote Sensing Adaptation & Fine-Tuning Guide

This directory contains the remote-sensing instruction adaptation and fine-tuning architecture for SatQuery AI.

## Supported Architectures & Adapters
- **GeoChat** (Vision-Language Foundation Model for Earth Observation)
- **GeoGround** (Referring Expression Grounding)
- **Change-Agent & ChangeChat** (Bi-Temporal Siamese Reasoning)
- **Clay & Prithvi-EO-2.0** (Self-Supervised EO Embeddings)

## Fine-Tuning Methods
- **Parameter-Efficient Fine-Tuning (PEFT)**
- **Low-Rank Adaptation (LoRA)**: Rank $r=16$, $\alpha=32$, targeting linear projection attention layers (`q_proj`, `v_proj`, `k_proj`, `o_proj`).
- **Quantized LoRA (QLoRA)**: 4-bit NormalFloat (NF4) with double quantization, enabling instruction tuning of 7B parameter models on a single consumer GPU (>=16GB VRAM).

## Datasets Supported
1. **BigEarthNet**: 590,326 Sentinel-2 & Sentinel-1 patches across 19 CORINE land-cover classes.
2. **VRSBench**: 29,614 high-resolution aerial images with dense captions, VQA questions, and object grounding annotations.
3. **RSVQA**: Sentinel-2 (Low-Res) and aerial (High-Res) questions covering object presence, comparison, and rural/urban areas.
4. **CDVQA**: Dual-temporal change VQA pairs.
5. **LEVIR-CC & LEVIR-MCI**: Dual-temporal change captioning and pixel-level building change masks.

## Execution

### 1. Validate Training Configuration
```bash
python training/train_lora.py --config training/configs/lora_config.yaml --dry_run
```

### 2. Initiate QLoRA Training
```bash
python training/train_lora.py --config training/configs/lora_config.yaml --output_dir ./checkpoints/geochat_lora
```

### 3. Run Benchmark Evaluation
```bash
python training/evaluate.py --benchmark all
```
