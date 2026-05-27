from __future__ import annotations

import json
import os
import secrets
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from generator import BRAND_PROFILES, generate_events, write_fixture

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="SW Events Web Generator", version="1.0.0")


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def safe_int(value: Optional[str], lo: int, hi: int) -> Optional[int]:
    value = clean_text(value)
    if value is None:
        return None
    try:
        n = int(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid number: {value}")
    if not lo <= n <= hi:
        raise HTTPException(status_code=400, detail=f"Value must be {lo}..{hi}")
    return n


def safe_float(value: Optional[str], lo: float, hi: float) -> Optional[float]:
    value = clean_text(value)
    if value is None:
        return None
    try:
        n = float(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid number: {value}")
    if not lo <= n <= hi:
        raise HTTPException(status_code=400, detail=f"Value must be {lo}..{hi}")
    return n


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/profiles")
def profiles() -> dict:
    return {
        "brands": {
            brand: {
                "models": profile["models"],
                "android_versions": profile["android_versions"],
                "event_count_range": profile["event_count"],
            }
            for brand, profile in BRAND_PROFILES.items()
        }
    }


@app.post("/api/generate")
def generate(
    brand: str = Form("xiaomi"),
    model: Optional[str] = Form(None),
    android: Optional[str] = Form(None),
    count: Optional[str] = Form(None),
    days: Optional[str] = Form(None),
    seed: Optional[str] = Form(None),
) -> JSONResponse:
    brand = brand.lower().strip()
    if brand not in BRAND_PROFILES:
        raise HTTPException(status_code=400, detail="Unknown brand")

    event_count = safe_int(count, 1_000, 150_000)
    days_value = safe_float(days, 1.0, 14.0)
    seed_value = safe_int(seed, 0, 999_999_999)

    job_id = secrets.token_hex(8)
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        rows, manifest, meta = generate_events(
            brand=brand,
            model=clean_text(model),
            android_version=clean_text(android),
            count=event_count,
            seed=seed_value,
            days=days_value,
        )
        zip_path, report_path, report = write_fixture(rows, manifest, meta, job_dir)
    except Exception as exc:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = {
        "job_id": job_id,
        "zip_file": zip_path.name,
        "report_file": report_path.name,
        "download_zip": f"/download/{job_id}/zip",
        "download_report": f"/download/{job_id}/report",
        "summary": {
            "device_model": manifest["device_model"],
            "android_version": manifest["android_version"],
            "event_count": manifest["event_count"],
            "window_start": manifest["window_start"],
            "window_end": manifest["window_end"],
            "score": report["quality"]["score"],
            "sha256": report["zip_sha256"],
            "zip_size": report["zip_size"],
            "top_packages": report["metrics"]["top_packages"][:10],
            "event_types": report["metrics"]["event_types"][:10],
        },
        "notice": "Synthetic QA fixture only — not real user export.",
    }
    (job_dir / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return JSONResponse(payload)


@app.get("/download/{job_id}/{kind}")
def download(job_id: str, kind: str):
    if not job_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid job id")
    job_dir = OUTPUT_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    files = list(job_dir.glob("*.zip")) if kind == "zip" else list(job_dir.glob("*_report.json")) if kind == "report" else []
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    path = files[0]
    return FileResponse(path, filename=path.name, media_type="application/zip" if kind == "zip" else "application/json")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "output_dir": str(OUTPUT_DIR)}
