import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database.db import init_db
from .api.endpoints import router as api_router
from .services.sample_generator import generate_samples_if_needed

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
RESULTS_DIR = BASE_DIR / "data" / "results"
SAMPLES_DIR = BASE_DIR / "data" / "samples"
REPORTS_DIR = BASE_DIR / "reports"

for d in [UPLOADS_DIR, RESULTS_DIR, SAMPLES_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="SatQuery AI API",
    description="Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static media directories
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")
app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")

# Register API Router
app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    init_db()
    try:
        generate_samples_if_needed()
    except Exception as e:
        print(f"Warning: Failed to generate sample datasets on startup: {e}")

@app.get("/")
def root():
    return {
        "service": "SatQuery AI Backend",
        "status": "online",
        "documentation": "/docs"
    }
