from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

# Add parent to path for generator import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generator import BRAND_PROFILES, generate_full

app = FastAPI(title="SW Events Generator", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = Path(__file__).resolve().parent.parent / "public" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


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
):
    brand = brand.lower().strip()
    if brand not in BRAND_PROFILES:
        raise HTTPException(status_code=400, detail="Unknown brand")

    def parse_int(v, lo, hi):
        if not v or not v.strip():
            return None
        try:
            n = int(v.strip())
        except ValueError:
            raise HTTPException(400, f"Invalid number: {v}")
        if not lo <= n <= hi:
            raise HTTPException(400, f"Value must be {lo}..{hi}")
        return n

    def parse_float(v, lo, hi):
        if not v or not v.strip():
            return None
        try:
            n = float(v.strip())
        except ValueError:
            raise HTTPException(400, f"Invalid number: {v}")
        if not lo <= n <= hi:
            raise HTTPException(400, f"Value must be {lo}..{hi}")
        return n

    event_count = parse_int(count, 1000, 150000)
    days_value = parse_float(days, 1.0, 14.0)
    seed_value = parse_int(seed, 0, 999999999)
    model_value = model.strip() if model and model.strip() else None
    android_value = android.strip() if android and android.strip() else None

    try:
        result = generate_full(brand, model_value, android_value, event_count, seed_value, days_value)
    except Exception as exc:
        raise HTTPException(500, str(exc))

    manifest = result["manifest"]
    return JSONResponse({
        "filename": result["filename"],
        "zip_size": result["zip_size"],
        "zip_sha256": result["zip_sha256"],
        "zip_base64": base64.b64encode(result["zip_bytes"]).decode("ascii"),
        "summary": {
            "device_model": manifest["device_model"],
            "android_version": manifest["android_version"],
            "event_count": manifest["event_count"],
            "window_start": manifest["window_start"],
            "window_end": manifest["window_end"],
            "score": result["quality"]["score"],
            "sha256": result["zip_sha256"],
            "zip_size": result["zip_size"],
            "top_packages": result["metrics"]["top_packages"][:10],
            "event_types": result["metrics"]["event_types"][:10],
        },
        "notice": "Synthetic QA fixture only — not real user export.",
    })


@app.get("/health")
def health():
    return {"ok": True}
