"""SW Events Generator — Vercel serverless handler.
Self-contained: all generator logic inline, HTML embedded.
No external file reads, no sys.path hacks.
"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import hashlib
import json
import math
import random
import urllib.parse
import zipfile
from io import BytesIO
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

# ─── BRAND PROFILES ──────────────────────────────────────────────────────────

EVENT_WEIGHTS = [
    ("ACTIVITY_RESUMED", 28.0), ("ACTIVITY_PAUSED", 27.5), ("EVENT_23", 22.0),
    ("NOTIFICATION_INTERRUPTION", 6.0), ("NOTIFICATION_SEEN", 4.5),
    ("FOREGROUND_SERVICE_START", 3.2), ("FOREGROUND_SERVICE_STOP", 3.2),
    ("STANDBY_BUCKET_CHANGED", 2.8), ("USER_INTERACTION", 1.6),
    ("SCREEN_INTERACTIVE", 0.9), ("SCREEN_NON_INTERACTIVE", 0.8),
    ("KEYGUARD_HIDDEN", 0.3), ("KEYGUARD_SHOWN", 0.2), ("CONFIGURATION_CHANGE", 0.1),
]

BASE_HOUR = [
    0.012, 0.008, 0.007, 0.006, 0.006, 0.009, 0.018, 0.036,
    0.052, 0.068, 0.072, 0.065, 0.070, 0.064, 0.060, 0.062,
    0.068, 0.075, 0.080, 0.078, 0.052, 0.042, 0.028, 0.018,
]

BRAND_PROFILES: Dict[str, Dict[str, Any]] = {
    "samsung": {
        "models": ["samsung SM-A057F", "samsung SM-A155F", "samsung SM-A226B", "samsung SM-A035F", "samsung SM-A105G"],
        "android_versions": ["13", "14"], "event_count": (18000, 76000), "class_presence": (0.60, 0.82),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.205), ("com.sec.android.app.launcher", "com.android.quickstep.RecentsActivity", 0.150),
            ("android", "", 0.058), ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.044),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.043), ("com.facebook.katana", "com.facebook.katana.LoginActivity", 0.038),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.037), ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.035),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.034), ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.030),
            ("com.samsung.android.dialer", "com.samsung.android.dialer.DialtactsActivity", 0.024), ("com.samsung.android.messaging", "com.samsung.android.messaging.ui.view.main.WithActivity", 0.022),
            ("com.sec.android.gallery3d", "com.samsung.android.gallery.app.activity.GalleryActivity", 0.021), ("com.sec.android.app.camera", "com.sec.android.app.camera.Camera", 0.018),
            ("com.android.settings", "com.android.settings.Settings", 0.018), ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.015),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.014), ("com.gojek.app", "com.gojek.app.HomeActivity", 0.014),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.013), ("com.tokopedia.tkpd", "com.tokopedia.tkpd.ConsumerMainActivity", 0.012),
            ("com.spotify.music", "com.spotify.music.MainActivity", 0.011), ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011),
            ("com.samsung.android.calendar", "com.samsung.android.calendar.MainActivity", 0.008),
        ],
    },
    "xiaomi": {
        "models": ["Xiaomi 2201117PG", "Xiaomi M2006C3MG", "Xiaomi M2010J19SG", "Xiaomi 24075RP89G", "Redmi Note 13"],
        "android_versions": ["12", "13", "14"], "event_count": (18000, 105000), "class_presence": (0.58, 0.80),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.170), ("com.mi.android.globallauncher", "com.miui.home.launcher.Launcher", 0.120),
            ("com.miui.home", "com.miui.home.launcher.Launcher", 0.072), ("android", "", 0.058),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.048), ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.044),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.040), ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.038),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.034), ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.032),
            ("com.xiaomi.mipicks", "com.xiaomi.mipicks.ui.MainActivity", 0.026), ("com.miui.securitycenter", "com.miui.securityscan.MainActivity", 0.024),
            ("com.miui.gallery", "com.miui.gallery.activity.HomePageActivity", 0.022), ("com.android.settings", "com.android.settings.Settings", 0.020),
            ("com.google.android.apps.photos", "com.google.android.apps.photos.home.HomeActivity", 0.018), ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015), ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014),
            ("com.mobile.legends", "com.moba.unityplugin.MobaGameMainActivity", 0.013), ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.012),
            ("com.miui.weather2", "com.miui.weather2.ActivityWeatherMain", 0.010),
        ],
    },
    "oppo": {
        "models": ["OPPO CPH2577", "OPPO CPH2387", "OPPO CPH1909", "OPPO CPH2591"],
        "android_versions": ["11", "12", "13", "14"], "event_count": (19000, 76000), "class_presence": (0.60, 0.84),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.165), ("com.whatsapp.w4b", "com.whatsapp.HomeActivity", 0.100),
            ("com.android.launcher", "com.android.launcher3.Launcher", 0.140), ("com.oppo.launcher", "com.oppo.launcher.Launcher", 0.052),
            ("android", "", 0.060), ("com.facebook.lite", "com.facebook.lite.MainActivity", 0.055),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.045), ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.040),
            ("com.coloros.recents", "com.coloros.recents.RecentsActivity", 0.038), ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.034),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.030), ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.026),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.024), ("com.android.settings", "com.android.settings.Settings", 0.022),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.019), ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015), ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014),
            ("com.spotify.music", "com.spotify.music.MainActivity", 0.012), ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.012),
            ("com.panjoy.android", "", 0.010),
        ],
    },
    "infinix": {
        "models": ["Infinix X6833B", "Infinix X669C", "Infinix X6728B", "Infinix X6886"],
        "android_versions": ["12", "13", "14"], "event_count": (20000, 65000), "class_presence": (0.62, 0.83),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.170), ("com.transsion.XOSLauncher", "com.transsion.launcher.Launcher", 0.130),
            ("android", "", 0.055), ("tw.nekomimi.nekogram", "org.telegram.ui.LaunchActivity", 0.060),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.045), ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.040),
            ("com.twitter.android", "com.twitter.app.main.MainActivity", 0.035), ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.032),
            ("com.authy.authy", "com.authy.authy.activities.MainActivity", 0.030), ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.028),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.025), ("com.openai.chatgpt", "com.openai.chatgpt.MainActivity", 0.022),
            ("com.android.settings", "com.android.settings.Settings", 0.020), ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015), ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.014),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.012), ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011),
            ("com.binance.dev", "com.binance.dev.SplashActivity", 0.010), ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.010),
        ],
    },
    "advan": {
        "models": ["Advan G5", "Advan G9 Pro", "Advan i6C"],
        "android_versions": ["11", "12", "13"], "event_count": (15000, 55000), "class_presence": (0.56, 0.78),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.180), ("com.advan.launcher", "", 0.110),
            ("android", "", 0.060), ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.050),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.042), ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.036),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.030), ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.028),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.024), ("com.android.settings", "com.android.settings.Settings", 0.022),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.018), ("com.gojek.app", "com.gojek.app.HomeActivity", 0.016),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014), ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.012),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011), ("com.spotify.music", "com.spotify.music.MainActivity", 0.010),
            ("com.facebook.katana", "com.facebook.katana.LoginActivity", 0.010),
        ],
    },
}

# ─── GENERATOR LOGIC ─────────────────────────────────────────────────────────

def _norm(items):
    s = sum(w for _, _, w in items)
    return [(p, c, w / s) for p, c, w in items]

def _iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _entropy(counter):
    total = sum(counter.values())
    return -sum((v / total) * math.log2(v / total) for v in counter.values() if v and total) if total else 0.0

def _quantile(values, q):
    if not values: return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * q))]

def _allocate_days(start, end, total, rng):
    days = []
    d = start.date()
    while d <= end.date():
        days.append(d)
        d += dt.timedelta(days=1)
    weights = []
    for day in days:
        w = 1.0
        if day.weekday() in (5, 6): w *= rng.uniform(1.05, 1.35)
        if day.weekday() == 0: w *= rng.uniform(0.72, 1.05)
        if day == start.date(): w *= rng.uniform(0.32, 0.65)
        if day == end.date(): w *= rng.uniform(0.35, 0.75)
        w *= rng.uniform(0.68, 1.42)
        weights.append(w)
    s = sum(weights)
    counts = {d: int(round(total * w / s)) for d, w in zip(days, weights)}
    while sum(counts.values()) < total: counts[rng.choice(days)] += 1
    while sum(counts.values()) > total:
        k = rng.choice([d for d in days if counts[d] > 20])
        counts[k] -= 1
    return counts

def _generate(brand, model, android_version, count, seed, days):
    rng = random.Random(seed)
    brand = brand.lower()
    prof = BRAND_PROFILES[brand]
    model = model or rng.choice(prof["models"])
    android_version = android_version or rng.choice(prof["android_versions"])
    if count is None:
        lo, hi = prof["event_count"]
        count = rng.randint(lo, hi)
    count = min(count, 80000)  # Vercel timeout safety
    if days is None: days = rng.uniform(7.1, 9.8)
    end = dt.datetime(2026, 5, 26, rng.randint(5, 20), rng.randint(0, 59), rng.randint(0, 59), tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days, minutes=rng.randint(0, 180), seconds=rng.randint(0, 59))
    apps = _norm(prof["apps"])
    packages = [p for p, _, _ in apps]
    classes = {p: c for p, c, _ in apps}
    pkg_weights = [w for _, _, w in apps]
    class_target = rng.uniform(*prof["class_presence"])
    day_counts = _allocate_days(start, end, count, rng)
    rows = []
    type_names = [t for t, _ in EVENT_WEIGHTS]
    type_weights = [w * rng.uniform(0.82, 1.18) for _, w in EVENT_WEIGHTS]
    for day, nday in sorted(day_counts.items()):
        hw = [max(0.0004, w * rng.uniform(0.70, 1.35)) for w in BASE_HOUR]
        if day.weekday() in (5, 6):
            for h in range(12, 23): hw[h] *= rng.uniform(1.02, 1.32)
            for h in range(7, 11): hw[h] *= rng.uniform(0.75, 1.05)
        hs = sum(hw); hw = [x / hs for x in hw]
        per_hour = [int(round(nday * w)) for w in hw]
        while sum(per_hour) < nday: per_hour[rng.randrange(24)] += 1
        while sum(per_hour) > nday:
            h = rng.choice([i for i, v in enumerate(per_hour) if v > 0]); per_hour[h] -= 1
        for hour, nh in enumerate(per_hour):
            remaining = nh
            while remaining > 0:
                burst = min(remaining, max(1, int(rng.lognormvariate(2.12, 0.80))))
                remaining -= burst
                current = dt.datetime(day.year, day.month, day.day, hour, rng.randrange(60), rng.randrange(60), rng.randrange(1000) * 1000, tzinfo=dt.timezone.utc)
                if current < start: current = start + dt.timedelta(seconds=rng.randint(0, 2400), milliseconds=rng.randint(0, 999))
                if current > end: current = end - dt.timedelta(seconds=rng.randint(0, 2400), milliseconds=rng.randint(0, 999))
                session_pkg = rng.choices(packages, weights=pkg_weights, k=1)[0]
                for i in range(burst):
                    if i:
                        r = rng.random()
                        if r < 0.62: delta = rng.uniform(0.04, 0.95)
                        elif r < 0.91: delta = rng.uniform(1, 20)
                        elif r < 0.985: delta = rng.uniform(20, 210)
                        else: delta = rng.uniform(210, 950)
                        current = current + dt.timedelta(seconds=delta, milliseconds=rng.randint(0, 25))
                    if not (start <= current <= end): continue
                    ppkg = session_pkg
                    if rng.random() < 0.13:
                        vl = packages[1] if len(packages) > 1 else packages[0]
                        ppkg = rng.choices([vl, "android", "com.google.android.gms", "com.android.settings"], weights=[0.46, 0.30, 0.17, 0.07], k=1)[0]
                    if i == 0 and rng.random() < 0.70: typ = "ACTIVITY_RESUMED"
                    elif i == burst - 1 and rng.random() < 0.63: typ = "ACTIVITY_PAUSED"
                    else: typ = rng.choices(type_names, weights=type_weights, k=1)[0]
                    rec = {"ts": int(current.timestamp() * 1000) + rng.randint(0, 12), "package": ppkg, "type": typ}
                    cls = classes.get(ppkg, "")
                    if cls:
                        if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION", "CONFIGURATION_CHANGE"):
                            has = rng.random() < min(0.94, class_target + 0.18)
                        elif typ.startswith("FOREGROUND_SERVICE"):
                            has = rng.random() < max(0.25, class_target - 0.30)
                        elif typ.startswith("SCREEN") or typ.startswith("KEYGUARD") or typ == "STANDBY_BUCKET_CHANGED":
                            has = rng.random() < max(0.04, class_target - 0.58)
                        else:
                            has = rng.random() < max(0.08, class_target - 0.48)
                        if has: rec["class"] = cls
                    rows.append(rec)
    rows.sort(key=lambda r: r["ts"])
    while len(rows) > count: rows.pop(rng.randrange(len(rows)))
    while len(rows) < count:
        current = start + dt.timedelta(seconds=rng.randint(0, max(1, int((end - start).total_seconds()))), milliseconds=rng.randint(0, 999))
        ppkg = rng.choices(packages, weights=pkg_weights, k=1)[0]
        typ = rng.choices(type_names, weights=type_weights, k=1)[0]
        rec = {"ts": int(current.timestamp() * 1000), "package": ppkg, "type": typ}
        if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23") and rng.random() < 0.86 and classes.get(ppkg):
            rec["class"] = classes[ppkg]
        rows.append(rec)
    rows.sort(key=lambda r: r["ts"])
    min_t = dt.datetime.fromtimestamp(rows[0]["ts"] / 1000, dt.timezone.utc)
    max_t = dt.datetime.fromtimestamp(rows[-1]["ts"] / 1000, dt.timezone.utc)
    manifest = {
        "schema_version": 1, "app_version": "1.0.0", "android_version": android_version,
        "device_model": model, "export_generated_at": _iso(max_t),
        "window_start": _iso(min_t), "window_end": _iso(max_t),
        "event_count": len(rows),
        "notes": "Event-level data subject to Android system retention; older periods may be summarised only.",
    }
    meta = {"brand": brand, "seed": seed, "class_target": class_target, "requested_count": count, "requested_days": days}
    return rows, manifest, meta

def _analyze(rows):
    pkg = collections.Counter(r["package"] for r in rows)
    typ = collections.Counter(r["type"] for r in rows)
    gaps = [(b["ts"] - a["ts"]) / 1000 for a, b in zip(rows, rows[1:])]
    class_pct = sum(1 for r in rows if "class" in r) / len(rows) * 100 if rows else 0
    return {
        "event_count": len(rows), "unique_packages": len(pkg),
        "package_entropy": round(_entropy(pkg), 3), "event_type_entropy": round(_entropy(typ), 3),
        "class_presence_pct": round(class_pct, 2),
        "gap_p50_sec": round(_quantile(gaps, 0.50), 3), "gap_p90_sec": round(_quantile(gaps, 0.90), 3), "gap_p99_sec": round(_quantile(gaps, 0.99), 3),
        "gap_lte_1s_pct": round(sum(g <= 1 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "gap_gt_10m_pct": round(sum(g > 600 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "top_packages": pkg.most_common(30), "event_types": typ.most_common(),
        "first_record": rows[0] if rows else None, "last_record": rows[-1] if rows else None,
    }

def _score(m):
    score = 100; reasons = []
    n = m["event_count"]
    if not (5000 <= n <= 110000): score -= 15; reasons.append("event_count outside range")
    cp = m["class_presence_pct"]
    if not (55 <= cp <= 86): score -= 18; reasons.append("class presence outside range")
    p50, p90, p99 = m["gap_p50_sec"], m["gap_p90_sec"], m["gap_p99_sec"]
    if not (0.25 <= p50 <= 1.2): score -= 18; reasons.append("gap p50 not bursty")
    if not (8 <= p90 <= 60): score -= 12; reasons.append("gap p90 outside range")
    if not (80 <= p99 <= 900): score -= 8; reasons.append("gap p99 outside range")
    le1 = m["gap_lte_1s_pct"]
    if not (50 <= le1 <= 73): score -= 14; reasons.append("<=1s burst outside range")
    lg = m["gap_gt_10m_pct"]
    if not (0.05 <= lg <= 3.0): score -= 8; reasons.append(">10m idle outside range")
    pe = m["package_entropy"]
    if not (2.5 <= pe <= 5.4): score -= 6; reasons.append("pkg entropy outside range")
    te = m["event_type_entropy"]
    if not (1.5 <= te <= 3.5): score -= 6; reasons.append("type entropy outside range")
    return {"score": max(0, score), "reasons": reasons or ["all checks inside QA range"]}

def _build_zip(rows, manifest):
    ndjson = "\n".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in rows) + "\n"
    mstr = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("events.ndjson", ndjson)
        z.writestr("manifest.json", mstr)
    data = buf.getvalue()
    return data, hashlib.sha256(data).hexdigest()

# ─── HANDLER ─────────────────────────────────────────────────────────────────

def handler(request, response):
    """Vercel Python serverless handler."""
    method = request.method
    path = request.path or "/"

    # CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    if method == "OPTIONS":
        response.status_code = 204
        return ""

    # GET / → serve HTML
    if method == "GET" and path == "/":
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.status_code = 200
        return HTML

    # GET /health
    if method == "GET" and path == "/health":
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return json.dumps({"ok": True})

    # GET /api/profiles
    if method == "GET" and path == "/api/profiles":
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return json.dumps({
            "brands": {
                b: {"models": p["models"], "android_versions": p["android_versions"], "event_count_range": list(p["event_count"])}
                for b, p in BRAND_PROFILES.items()
            }
        })

    # POST /api/generate
    if method == "POST" and path == "/api/generate":
        response.headers["Content-Type"] = "application/json"
        try:
            body = request.body
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            if isinstance(body, str):
                # Parse form data
                params = dict(urllib.parse.parse_qsl(body))
            else:
                params = body if isinstance(body, dict) else {}

            brand = (params.get("brand") or "xiaomi").strip().lower()
            if brand not in BRAND_PROFILES:
                response.status_code = 400
                return json.dumps({"detail": f"Unknown brand: {brand}"})

            def pi(v, lo, hi):
                if not v or not str(v).strip(): return None
                n = int(str(v).strip())
                if not lo <= n <= hi: raise ValueError(f"out of range {lo}-{hi}")
                return n

            def pf(v, lo, hi):
                if not v or not str(v).strip(): return None
                n = float(str(v).strip())
                if not lo <= n <= hi: raise ValueError(f"out of range {lo}-{hi}")
                return n

            count = pi(params.get("count"), 1000, 150000)
            days_v = pf(params.get("days"), 1.0, 14.0)
            seed_v = pi(params.get("seed"), 0, 999999999)
            model_v = (params.get("model") or "").strip() or None
            android_v = (params.get("android") or "").strip() or None

            rows, manifest, meta = _generate(brand, model_v, android_v, count, seed_v, days_v)
            metrics = _analyze(rows)
            quality = _score(metrics)
            zip_bytes, sha = _build_zip(rows, manifest)
            safe_model = manifest["device_model"].lower().replace(" ", "_").replace("/", "-")
            seed_part = meta.get("seed") if meta.get("seed") is not None else "auto"
            filename = f"sw_events_{safe_model}_{seed_part}.zip"

            response.status_code = 200
            return json.dumps({
                "filename": filename, "zip_size": len(zip_bytes), "zip_sha256": sha,
                "zip_base64": base64.b64encode(zip_bytes).decode("ascii"),
                "summary": {
                    "device_model": manifest["device_model"], "android_version": manifest["android_version"],
                    "event_count": manifest["event_count"], "window_start": manifest["window_start"],
                    "window_end": manifest["window_end"], "score": quality["score"],
                    "sha256": sha, "zip_size": len(zip_bytes),
                    "top_packages": metrics["top_packages"][:10], "event_types": metrics["event_types"][:10],
                },
                "notice": "Synthetic QA fixture only — not real user export.",
            })
        except Exception as e:
            response.status_code = 500
            return json.dumps({"detail": str(e)})

    # 404
    response.status_code = 404
    response.headers["Content-Type"] = "application/json"
    return json.dumps({"detail": "Not found"})


# ─── EMBEDDED HTML ───────────────────────────────────────────────────────────

HTML = r"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SW Events Generator</title>
  <meta name="description" content="Generate synthetic Android sw_events ZIP fixtures for QA/staging parser tests." />
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚙️</text></svg>" />
  <style>
    body{background:radial-gradient(circle at top left,#1e293b 0,#020617 40%,#000 100%)}
    .glass{background:rgba(15,23,42,.72);backdrop-filter:blur(18px);border:1px solid rgba(148,163,184,.22)}
    @keyframes pulse-ring{0%{transform:scale(.8);opacity:1}100%{transform:scale(1.4);opacity:0}}
    .pulse-ring{animation:pulse-ring 1.2s ease-out infinite}
  </style>
</head>
<body class="min-h-screen text-slate-100 antialiased">
  <main class="mx-auto max-w-6xl px-4 py-8 md:py-12">
    <section class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <div class="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
          <span class="relative flex h-2 w-2"><span class="pulse-ring absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-400"></span></span>
          Synthetic QA Fixture Generator
        </div>
        <h1 class="text-3xl font-black tracking-tight md:text-5xl">SW Events Generator</h1>
        <p class="mt-3 max-w-2xl text-slate-300">Generate <code class="rounded bg-slate-800 px-1">sw_events.zip</code> Android fixture files langsung dari browser.</p>
      </div>
    </section>
    <section class="grid gap-6 lg:grid-cols-[420px,1fr]">
      <form id="f" class="glass rounded-3xl p-5 shadow-2xl md:p-6">
        <h2 class="mb-5 flex items-center gap-2 text-xl font-bold">⚡ Config</h2>
        <label class="mb-4 block"><span class="mb-2 block text-sm font-medium text-slate-300">Brand</span>
          <select name="brand" id="brand" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2">
            <option value="xiaomi">Xiaomi / Redmi</option><option value="samsung">Samsung</option><option value="oppo">OPPO</option><option value="infinix">Infinix</option><option value="advan">Advan</option>
          </select></label>
        <label class="mb-4 block"><span class="mb-2 block text-sm font-medium text-slate-300">Model <span class="text-slate-500">(optional)</span></span>
          <input name="model" placeholder="Kosongkan = random" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2" />
          <p id="hint" class="mt-2 text-xs text-slate-500"></p></label>
        <div class="mb-4 grid grid-cols-2 gap-3">
          <label class="block"><span class="mb-2 block text-sm font-medium text-slate-300">Android</span><input name="android" placeholder="auto" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2" /></label>
          <label class="block"><span class="mb-2 block text-sm font-medium text-slate-300">Seed</span><input name="seed" type="number" min="0" max="999999999" placeholder="random" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2" /></label>
        </div>
        <div class="mb-5 grid grid-cols-2 gap-3">
          <label class="block"><span class="mb-2 block text-sm font-medium text-slate-300">Event count</span><input name="count" type="number" min="1000" max="80000" placeholder="auto" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2" /></label>
          <label class="block"><span class="mb-2 block text-sm font-medium text-slate-300">Days</span><input name="days" type="number" min="1" max="14" step="0.1" placeholder="auto" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none ring-emerald-400 focus:ring-2" /></label>
        </div>
        <button id="btn" type="submit" class="w-full rounded-xl bg-emerald-400 px-5 py-3 font-black text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400">🚀 Generate ZIP</button>
        <p class="mt-4 rounded-xl bg-amber-400/10 p-3 text-xs leading-relaxed text-amber-200">⚠️ Output = <b>synthetic QA fixture</b>, bukan export asli.</p>
      </form>
      <section class="glass rounded-3xl p-5 shadow-2xl md:p-6">
        <div class="mb-4 flex items-center justify-between"><h2 class="text-xl font-bold">Result</h2><span id="st" class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">Idle</span></div>
        <div id="empty" class="flex min-h-[420px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-700 p-8 text-center text-slate-400">
          <div class="mb-4 text-5xl">📦</div><p class="font-semibold text-slate-300">Belum ada file.</p><p class="mt-1 text-sm">Isi config, klik Generate.</p></div>
        <div id="res" class="hidden space-y-5">
          <div class="grid gap-3 md:grid-cols-3">
            <div class="rounded-2xl bg-slate-950/70 p-4"><p class="text-xs text-slate-500">Device</p><p id="d" class="mt-1 truncate font-bold"></p></div>
            <div class="rounded-2xl bg-slate-950/70 p-4"><p class="text-xs text-slate-500">Events</p><p id="e" class="mt-1 font-bold"></p></div>
            <div class="rounded-2xl bg-slate-950/70 p-4"><p class="text-xs text-slate-500">Score</p><p id="sc" class="mt-1 font-bold text-emerald-300"></p></div>
          </div>
          <div class="rounded-2xl bg-slate-950/70 p-4 text-sm">
            <p><span class="text-slate-500">Window:</span> <span id="w"></span></p>
            <p class="mt-2 break-all"><span class="text-slate-500">SHA256:</span> <code id="sh" class="text-xs"></code></p>
            <p class="mt-2"><span class="text-slate-500">Size:</span> <span id="sz"></span></p>
          </div>
          <button id="dl" class="w-full rounded-xl bg-emerald-400 px-4 py-3 font-black text-slate-950 hover:bg-emerald-300">⬇️ Download ZIP</button>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl bg-slate-950/70 p-4"><h3 class="mb-3 font-bold text-emerald-300">Top Packages</h3><ol id="tp" class="space-y-1.5 text-sm text-slate-300"></ol></div>
            <div class="rounded-2xl bg-slate-950/70 p-4"><h3 class="mb-3 font-bold text-emerald-300">Event Types</h3><ol id="et" class="space-y-1.5 text-sm text-slate-300"></ol></div>
          </div>
        </div>
      </section>
    </section>
    <footer class="mt-12 text-center text-xs text-slate-600">Synthetic QA fixture generator — not real user data.</footer>
  </main>
<script>
const $=id=>document.getElementById(id);let blob=null,fn='sw_events.zip',profiles=null;
async function loadP(){try{const r=await fetch('/api/profiles');profiles=await r.json();hint()}catch(e){}}
function hint(){const b=$('brand').value;if(!profiles)return;const p=profiles.brands[b];$('hint').textContent='Models: '+p.models.slice(0,3).join(', ')+' • Events: '+p.event_count_range[0].toLocaleString()+'–'+p.event_count_range[1].toLocaleString()}
function rows(l){return l.map(([n,c])=>{const p=Math.min(Math.round(c/10),100);return`<li class="flex items-center gap-2"><span class="w-16 text-right text-xs text-slate-500">${Number(c).toLocaleString()}</span><div class="flex-1 overflow-hidden"><div class="h-2 rounded-full bg-emerald-400/30"><div class="h-2 rounded-full bg-emerald-400" style="width:${p}%"></div></div></div><span class="flex-1 truncate text-xs">${n}</span></li>`}).join('')}
$('brand').addEventListener('change',hint);
$('dl').addEventListener('click',()=>{if(!blob)return;const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=fn;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(u);a.remove()},100)});
$('f').addEventListener('submit',async e=>{e.preventDefault();$('btn').disabled=true;$('btn').textContent='⏳ Generating...';$('st').textContent='Generating';$('st').className='rounded-full bg-amber-400/20 px-3 py-1 text-xs text-amber-200';
try{const fd=new FormData(e.target),r=await fetch('/api/generate',{method:'POST',body:fd}),d=await r.json();if(!r.ok)throw new Error(d.detail||'Failed');
const s=d.summary;$('empty').classList.add('hidden');$('res').classList.remove('hidden');
$('d').textContent=s.device_model+' / Android '+s.android_version;$('e').textContent=Number(s.event_count).toLocaleString();$('sc').textContent=s.score+'/100';
$('w').textContent=s.window_start+' → '+s.window_end;$('sh').textContent=s.sha256;$('sz').textContent=(s.zip_size/1024).toFixed(1)+' KB';
$('tp').innerHTML=rows(s.top_packages);$('et').innerHTML=rows(s.event_types);
const bin=atob(d.zip_base64),arr=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);blob=new Blob([arr],{type:'application/zip'});fn=d.filename;
$('st').textContent='Ready';$('st').className='rounded-full bg-emerald-400/20 px-3 py-1 text-xs text-emerald-200';
}catch(err){alert('Error: '+err.message);$('st').textContent='Error';$('st').className='rounded-full bg-red-400/20 px-3 py-1 text-xs text-red-200';
}finally{$('btn').disabled=false;$('btn').textContent='🚀 Generate ZIP'}});
loadP();
</script>
</body></html>"""
