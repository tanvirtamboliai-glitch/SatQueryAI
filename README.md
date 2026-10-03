# SatQuery AI — Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.14-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.14-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)
![React](https://img.shields.io/badge/React-19-cyan.svg)

**SatQuery AI** is an agentic, multimodal Earth Observation (EO) vision-language intelligence platform. It processes single optical images, co-registered Optical + SAR pairs, and bi-temporal remote sensing pairs. By leveraging a 3-layer hybrid routing controller, SatQuery AI automatically classifies query intent, orchestrates specialist foundation models (GeoChat, GeoGround, Change-Agent, ChangeChat, Clay, Prithvi-EO-2.0, and RemoteCLIP), extracts spatial evidence (bounding boxes, Otsu/CVA change masks, region contours), computes calibrated multi-factor confidence scores, logs observable execution traces, and generates comprehensive scientific HTML/PDF dossiers.

---

## 🌟 Five Mandatory Demonstrated Capabilities

1. **Single-Image VQA**: Inquire in natural language about land use, infrastructure, water bodies, or terrain composition. Powered by **GeoChat-7B**.
2. **Single-Image Dense Captioning & Grounding**: Generate structured scene summaries or localize entities into bounding boxes and segmentation masks. Powered by **GeoChat** and **GeoGround**.
3. **Bi-Temporal Change Understanding & Change VQA**: Detect surface modifications across acquisition dates, compute change percentage distributions, extract change polygons, and answer temporal questions (*"What changed?"*, *"Has the built-up area increased?"*). Powered by **Change-Agent** and **ChangeChat**.
4. **Optical + SAR Cross-Modal Feature Fusion**: Fuse optical reflectance and SAR microwave backscatter to resolve surface double-bounce and penetrate optical clouds/shadows. Powered by **Clay** and **Prithvi-EO-2.0**.
5. **Agentic Model / Tool Orchestration**: 3-layer hybrid routing (Input Modality → Intent Classification → Specialist Execution) with observable execution traces and auditable confidence.

---

## 🏗️ Technical Architecture

```
                                [ USER WEB UI ]
            (React 19 + Vite + Tailwind CSS + Interactive Canvas Overlays)
                                       │
                         HTTP REST / SSE EventStream
                                       │
                                       ▼
                               [ FASTAPI BACKEND ]
 ┌─────────────────────────────────────┴─────────────────────────────────────┐
 │                                                                           │
 │  1. Input Validator                                                       │
 │     • GeoTIFF / TIFF / PNG / JPEG inspection                              │
 │     • Rasterio/tifffile CRS, dimensions, bands, extent, resolution         │
 │     • Bi-temporal / Optical-SAR spatial alignment & registration check   │
 │                                                                           │
 │  2. Agentic Controller & 3-Layer Query Router                             │
 │     • Layer 1: Input Modality & Count Router (Single, Bi-temporal, Opt+SAR│
 │     • Layer 2: Natural Language Intent Classifier (VQA, Grounding, Change)│
 │     • Layer 3: Controlled Specialist Tool Orchestration                   │
 │                                                                           │
 │  3. Model Registry & Specialists Adapter Layer                            │
 │     ├── GeoChat Service        (VQA, Captioning, Scene Analysis)          │
 │     ├── GeoGround Service      (Text-guided Grounding, BBoxes, Masks)     │
 │     ├── Change-Agent Service   (Bi-temporal Change Detection & Masks)     │
 │     ├── Change-VQA Service     (ChangeChat-compatible Change Understanding│
 │     ├── Prithvi-EO-2.0 Service (EO Foundation Feature Extraction)         │
 │     ├── Clay Service           (Multisensor Optical+SAR Representation)   │
 │     └── RemoteCLIP Service     (Zero-shot Retrieval & Semantic Similarity)│
 │                                                                           │
 │  4. Processing & Evidence Engine                                          │
 │     • GeoTIFF Windowing / Tiling (512x512) for large scenes               │
 │     • Optical + SAR Feature Fusion (Intermediate/Late Concatenation+MLP)  │
 │     • Visual Evidence Extraction (Polygon regions, change %, heatmap)     │
 │                                                                           │
 │  5. Confidence & Observable Execution Trace                               │
 │     • Multi-factor confidence (Model conf, segmentation, compatibility)   │
 │     • Structured step-by-step observable trace log                        │
 │                                                                           │
 │  6. Export & Dossier Generation                                           │
 │     • Standalone HTML & Printable PDF Analysis Report                     │
 └───────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested up to Python 3.14 on Windows)
- Node.js 18+ and npm

### 1. Backend Setup & Startup
```powershell
# In project root:
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup & Startup
```powershell
# In a second terminal inside frontend/:
cd frontend
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🎯 Five Pre-Configured Hackathon Demo Scenarios

In the UI, navigate to the **Evaluation Demo Scenarios** card on the left panel to trigger any test case with a single click:

| Demo | Task | Input Imagery | Canonical Query | Specialist Models |
| :--- | :--- | :--- | :--- | :--- |
| **Demo 1** | Single Scene VQA | `demo1_optical_landcover.tif` | *"Describe the land cover and major objects visible in this image."* | GeoChat |
| **Demo 2** | Text-Guided Grounding | `demo2_grounding_water.tif` | *"Highlight the water body."* | GeoGround |
| **Demo 3** | Change Detection | `demo3_bitemporal_2022.tif` + `demo3_bitemporal_2025.tif` | *"What changed between these two dates?"* | Change-Agent |
| **Demo 4** | Built-up Change VQA | `demo3_bitemporal_2022.tif` + `demo3_bitemporal_2025.tif` | *"Has the built-up area increased?"* | Change-Agent + ChangeChat |
| **Demo 5** | Optical + SAR Fusion | `demo5_optical.tif` + `demo5_sar.tif` | *"Use the optical and SAR images together to identify built-up and water-covered regions."* | Clay + Prithvi-EO-2.0 |

---

## 📊 Benchmark Evaluation Suite

SatQuery AI includes modular adapters for 6 standardized Earth observation datasets:
- **VRSBench**: High-resolution captioning, VQA, and bounding box grounding.
- **RSVQA**: Sentinel-2 (Low-Res) and aerial (High-Res) questions covering presence and counts.
- **CDVQA**: Dual-temporal change VQA pairs.
- **LEVIR-CC**: Dual-temporal change captioning.
- **LEVIR-MCI**: Dual-temporal pixel change masks and category classification.
- **BigEarthNet**: 590k Sentinel-2 & Sentinel-1 multisensor patches across 19 CORINE classes.

Run benchmark evaluation:
```powershell
.\venv\Scripts\python.exe training/evaluate.py --benchmark all
```

---

## 🛠️ Remote Sensing Adaptation (LoRA / QLoRA)

Instruction fine-tuning can be launched with parameter-efficient fine-tuning (PEFT):
```powershell
.\venv\Scripts\python.exe training/train_lora.py --config training/configs/lora_config.yaml --dry_run
```

---

## 🐳 Docker Deployment
```bash
docker-compose up --build
```
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
