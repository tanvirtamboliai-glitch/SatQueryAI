import sqlite3
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "satquery.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        file_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        preview_path TEXT,
        format TEXT NOT NULL,
        width INTEGER NOT NULL,
        height INTEGER NOT NULL,
        bands INTEGER NOT NULL,
        crs TEXT,
        geotransform TEXT,
        bounds TEXT,
        resolution TEXT,
        modality TEXT NOT NULL,
        acquisition_date TEXT,
        sensor TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_jobs (
        job_id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        detected_task TEXT NOT NULL,
        workflow TEXT NOT NULL,
        selected_models TEXT NOT NULL,
        answer TEXT NOT NULL,
        evidence_json TEXT NOT NULL,
        confidence_json TEXT NOT NULL,
        trace_json TEXT NOT NULL,
        report_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def save_image_record(record: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    width = record.get("width") or (record["dimensions"][0] if "dimensions" in record else 512)
    height = record.get("height") or (record["dimensions"][1] if "dimensions" in record else 512)
    cursor.execute("""
    INSERT OR REPLACE INTO images (
        file_id, filename, file_path, preview_path, format, width, height, bands,
        crs, geotransform, bounds, resolution, modality, acquisition_date, sensor
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["file_id"],
        record["filename"],
        record["file_path"],
        record.get("preview_path"),
        record["format"],
        width,
        height,
        record["bands"],
        record.get("crs"),
        json.dumps(record.get("geotransform")),
        json.dumps(record.get("bounds")),
        json.dumps(record.get("resolution")),
        record.get("modality", "optical"),
        record.get("acquisition_date"),
        record.get("sensor")
    ))
    conn.commit()
    conn.close()

def get_image_record(file_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE file_id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["dimensions"] = [data["width"], data["height"]]
    if data["geotransform"]:
        data["geotransform"] = json.loads(data["geotransform"])
    if data["bounds"]:
        data["bounds"] = json.loads(data["bounds"])
    if data["resolution"]:
        data["resolution"] = json.loads(data["resolution"])
    return data

def save_analysis_job(job: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO analysis_jobs (
        job_id, query, detected_task, workflow, selected_models, answer,
        evidence_json, confidence_json, trace_json, report_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job["job_id"],
        job["query"],
        job["detected_task"],
        job["workflow"],
        json.dumps(job["selected_models"]),
        job["answer"],
        json.dumps(job["evidence"]),
        json.dumps(job["confidence"]),
        json.dumps(job["execution_trace"]),
        job.get("report_path")
    ))
    conn.commit()
    conn.close()

def get_analysis_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["selected_models"] = json.loads(data["selected_models"])
    data["evidence"] = json.loads(data["evidence_json"])
    data["confidence"] = json.loads(data["confidence_json"])
    data["execution_trace"] = json.loads(data["trace_json"])
    return data

# Initialize tables on import
init_db()
