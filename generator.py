from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import math
import random
import statistics
import zipfile
from io import BytesIO
from typing import Dict, List, Tuple, Any

EVENT_TYPES = [
    "ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23",
    "NOTIFICATION_INTERRUPTION", "NOTIFICATION_SEEN",
    "FOREGROUND_SERVICE_START", "FOREGROUND_SERVICE_STOP",
    "STANDBY_BUCKET_CHANGED", "USER_INTERACTION",
    "SCREEN_INTERACTIVE", "SCREEN_NON_INTERACTIVE",
    "KEYGUARD_HIDDEN", "KEYGUARD_SHOWN", "CONFIGURATION_CHANGE",
]

EVENT_WEIGHTS = [
    ("ACTIVITY_RESUMED", 28.0),
    ("ACTIVITY_PAUSED", 27.5),
    ("EVENT_23", 22.0),
    ("NOTIFICATION_INTERRUPTION", 6.0),
    ("NOTIFICATION_SEEN", 4.5),
    ("FOREGROUND_SERVICE_START", 3.2),
    ("FOREGROUND_SERVICE_STOP", 3.2),
    ("STANDBY_BUCKET_CHANGED", 2.8),
    ("USER_INTERACTION", 1.6),
    ("SCREEN_INTERACTIVE", 0.9),
    ("SCREEN_NON_INTERACTIVE", 0.8),
    ("KEYGUARD_HIDDEN", 0.3),
    ("KEYGUARD_SHOWN", 0.2),
    ("CONFIGURATION_CHANGE", 0.1),
]

BASE_HOUR = [
    0.012, 0.008, 0.007, 0.006, 0.006, 0.009, 0.018, 0.036,
    0.052, 0.068, 0.072, 0.065, 0.070, 0.064, 0.060, 0.062,
    0.068, 0.075, 0.080, 0.078, 0.052, 0.042, 0.028, 0.018,
]

BRAND_PROFILES: Dict[str, Dict[str, Any]] = {
    "samsung": {
        "models": ["samsung SM-A057F", "samsung SM-A155F", "samsung SM-A226B", "samsung SM-A035F", "samsung SM-A105G"],
        "android_versions": ["13", "14"],
        "event_count": (18000, 76000),
        "class_presence": (0.60, 0.82),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.205),
            ("com.sec.android.app.launcher", "com.android.quickstep.RecentsActivity", 0.150),
            ("android", "", 0.058),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.044),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.043),
            ("com.facebook.katana", "com.facebook.katana.LoginActivity", 0.038),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.037),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.035),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.034),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.030),
            ("com.samsung.android.dialer", "com.samsung.android.dialer.DialtactsActivity", 0.024),
            ("com.samsung.android.messaging", "com.samsung.android.messaging.ui.view.main.WithActivity", 0.022),
            ("com.sec.android.gallery3d", "com.samsung.android.gallery.app.activity.GalleryActivity", 0.021),
            ("com.sec.android.app.camera", "com.sec.android.app.camera.Camera", 0.018),
            ("com.android.settings", "com.android.settings.Settings", 0.018),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.015),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.014),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.014),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.013),
            ("com.tokopedia.tkpd", "com.tokopedia.tkpd.ConsumerMainActivity", 0.012),
            ("com.spotify.music", "com.spotify.music.MainActivity", 0.011),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011),
            ("com.samsung.android.calendar", "com.samsung.android.calendar.MainActivity", 0.008),
        ],
    },
    "xiaomi": {
        "models": ["Xiaomi 2201117PG", "Xiaomi M2006C3MG", "Xiaomi M2010J19SG", "Xiaomi 24075RP89G", "Redmi Note 13"],
        "android_versions": ["12", "13", "14"],
        "event_count": (18000, 105000),
        "class_presence": (0.58, 0.80),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.170),
            ("com.mi.android.globallauncher", "com.miui.home.launcher.Launcher", 0.120),
            ("com.miui.home", "com.miui.home.launcher.Launcher", 0.072),
            ("android", "", 0.058),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.048),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.044),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.040),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.038),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.034),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.032),
            ("com.xiaomi.mipicks", "com.xiaomi.mipicks.ui.MainActivity", 0.026),
            ("com.miui.securitycenter", "com.miui.securityscan.MainActivity", 0.024),
            ("com.miui.gallery", "com.miui.gallery.activity.HomePageActivity", 0.022),
            ("com.android.settings", "com.android.settings.Settings", 0.020),
            ("com.google.android.apps.photos", "com.google.android.apps.photos.home.HomeActivity", 0.018),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014),
            ("com.mobile.legends", "com.moba.unityplugin.MobaGameMainActivity", 0.013),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.012),
            ("com.miui.weather2", "com.miui.weather2.ActivityWeatherMain", 0.010),
        ],
    },
    "oppo": {
        "models": ["OPPO CPH2577", "OPPO CPH2387", "OPPO CPH1909", "OPPO CPH2591"],
        "android_versions": ["11", "12", "13", "14"],
        "event_count": (19000, 76000),
        "class_presence": (0.60, 0.84),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.165),
            ("com.whatsapp.w4b", "com.whatsapp.HomeActivity", 0.100),
            ("com.android.launcher", "com.android.launcher3.Launcher", 0.140),
            ("com.oppo.launcher", "com.oppo.launcher.Launcher", 0.052),
            ("android", "", 0.060),
            ("com.facebook.lite", "com.facebook.lite.MainActivity", 0.055),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.045),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.040),
            ("com.coloros.recents", "com.coloros.recents.RecentsActivity", 0.038),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.034),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.030),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.026),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.024),
            ("com.android.settings", "com.android.settings.Settings", 0.022),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.019),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014),
            ("com.spotify.music", "com.spotify.music.MainActivity", 0.012),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.012),
            ("com.panjoy.android", "", 0.010),
        ],
    },
    "infinix": {
        "models": ["Infinix X6833B", "Infinix X669C", "Infinix X6728B", "Infinix X6886"],
        "android_versions": ["12", "13", "14"],
        "event_count": (20000, 65000),
        "class_presence": (0.62, 0.83),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.170),
            ("com.transsion.XOSLauncher", "com.transsion.launcher.Launcher", 0.130),
            ("android", "", 0.055),
            ("tw.nekomimi.nekogram", "org.telegram.ui.LaunchActivity", 0.060),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.045),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.040),
            ("com.twitter.android", "com.twitter.app.main.MainActivity", 0.035),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.032),
            ("com.authy.authy", "com.authy.authy.activities.MainActivity", 0.030),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.028),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.025),
            ("com.openai.chatgpt", "com.openai.chatgpt.MainActivity", 0.022),
            ("com.android.settings", "com.android.settings.Settings", 0.020),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.016),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.015),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.014),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.012),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011),
            ("com.binance.dev", "com.binance.dev.SplashActivity", 0.010),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.010),
        ],
    },
    "advan": {
        "models": ["Advan G5", "Advan G9 Pro", "Advan i6C"],
        "android_versions": ["11", "12", "13"],
        "event_count": (15000, 55000),
        "class_presence": (0.56, 0.78),
        "apps": [
            ("com.whatsapp", "com.whatsapp.HomeActivity", 0.180),
            ("com.advan.launcher", "", 0.110),
            ("android", "", 0.060),
            ("com.android.chrome", "com.google.android.apps.chrome.Main", 0.050),
            ("org.telegram.messenger", "org.telegram.ui.LaunchActivity", 0.042),
            ("com.instagram.android", "com.instagram.mainactivity.InstagramMainActivity", 0.036),
            ("com.google.android.gms", "com.google.android.gms.common.api.GoogleApiActivity", 0.030),
            ("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity", 0.028),
            ("com.google.android.youtube", "com.google.android.apps.youtube.app.WatchWhileActivity", 0.024),
            ("com.android.settings", "com.android.settings.Settings", 0.022),
            ("id.dana", "id.dana.home.HomeTabActivity", 0.018),
            ("com.gojek.app", "com.gojek.app.HomeActivity", 0.016),
            ("com.shopee.id", "com.shopee.app.ui.home.HomeActivity_", 0.014),
            ("com.google.android.gm", "com.google.android.gm.ConversationListActivityGmail", 0.012),
            ("com.android.vending", "com.android.vending.AssetBrowserActivity", 0.011),
            ("com.spotify.music", "com.spotify.music.MainActivity", 0.010),
            ("com.facebook.katana", "com.facebook.katana.LoginActivity", 0.010),
        ],
    },
}


def norm_weights(items: List[Tuple[str, str, float]]) -> List[Tuple[str, str, float]]:
    s = sum(w for _, _, w in items)
    return [(p, c, w / s) for p, c, w in items]


def iso_z(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entropy(counter: collections.Counter) -> float:
    total = sum(counter.values())
    return -sum((v / total) * math.log2(v / total) for v in counter.values() if v and total) if total else 0.0


def quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * q))]


def allocate_days(start: dt.datetime, end: dt.datetime, total: int, rng: random.Random) -> Dict[dt.date, int]:
    days = []
    d = start.date()
    while d <= end.date():
        days.append(d)
        d += dt.timedelta(days=1)
    weights = []
    for day in days:
        w = 1.0
        if day.weekday() in (5, 6):
            w *= rng.uniform(1.05, 1.35)
        if day.weekday() == 0:
            w *= rng.uniform(0.72, 1.05)
        if day == start.date():
            w *= rng.uniform(0.32, 0.65)
        if day == end.date():
            w *= rng.uniform(0.35, 0.75)
        w *= rng.uniform(0.68, 1.42)
        weights.append(w)
    s = sum(weights)
    counts = {d: int(round(total * w / s)) for d, w in zip(days, weights)}
    while sum(counts.values()) < total:
        counts[rng.choice(days)] += 1
    while sum(counts.values()) > total:
        k = rng.choice([d for d in days if counts[d] > 20])
        counts[k] -= 1
    return counts


def generate_events(brand: str, model: str | None, android_version: str | None, count: int | None, seed: int | None, days: float | None) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    rng = random.Random(seed)
    brand = brand.lower()
    if brand not in BRAND_PROFILES:
        raise ValueError(f"unknown brand {brand}; choose {', '.join(BRAND_PROFILES)}")
    prof = BRAND_PROFILES[brand]
    model = model or rng.choice(prof["models"])
    android_version = android_version or rng.choice(prof["android_versions"])
    if count is None:
        lo, hi = prof["event_count"]
        count = rng.randint(lo, hi)
    if days is None:
        days = rng.uniform(7.1, 9.8)
    end = dt.datetime(2026, 5, 26, rng.randint(5, 20), rng.randint(0, 59), rng.randint(0, 59), tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days, minutes=rng.randint(0, 180), seconds=rng.randint(0, 59))
    apps = norm_weights(prof["apps"])
    packages = [p for p, _, _ in apps]
    classes = {p: c for p, c, _ in apps}
    pkg_weights = [w for _, _, w in apps]
    class_target = rng.uniform(*prof["class_presence"])
    day_counts = allocate_days(start, end, count, rng)
    rows: List[Dict[str, Any]] = []
    type_names = [t for t, _ in EVENT_WEIGHTS]
    type_weights = [w * rng.uniform(0.82, 1.18) for _, w in EVENT_WEIGHTS]
    for day, nday in sorted(day_counts.items()):
        hw = [max(0.0004, w * rng.uniform(0.70, 1.35)) for w in BASE_HOUR]
        if day.weekday() in (5, 6):
            for h in range(12, 23):
                hw[h] *= rng.uniform(1.02, 1.32)
            for h in range(7, 11):
                hw[h] *= rng.uniform(0.75, 1.05)
        hs = sum(hw)
        hw = [x / hs for x in hw]
        per_hour = [int(round(nday * w)) for w in hw]
        while sum(per_hour) < nday:
            per_hour[rng.randrange(24)] += 1
        while sum(per_hour) > nday:
            h = rng.choice([i for i, v in enumerate(per_hour) if v > 0])
            per_hour[h] -= 1
        for hour, nh in enumerate(per_hour):
            remaining = nh
            while remaining > 0:
                burst = min(remaining, max(1, int(rng.lognormvariate(2.12, 0.80))))
                remaining -= burst
                current = dt.datetime(day.year, day.month, day.day, hour, rng.randrange(60), rng.randrange(60), rng.randrange(1000) * 1000, tzinfo=dt.timezone.utc)
                if current < start:
                    current = start + dt.timedelta(seconds=rng.randint(0, 2400), milliseconds=rng.randint(0, 999))
                if current > end:
                    current = end - dt.timedelta(seconds=rng.randint(0, 2400), milliseconds=rng.randint(0, 999))
                session_pkg = rng.choices(packages, weights=pkg_weights, k=1)[0]
                for i in range(burst):
                    if i:
                        r = rng.random()
                        if r < 0.62:
                            delta = rng.uniform(0.04, 0.95)
                        elif r < 0.91:
                            delta = rng.uniform(1, 20)
                        elif r < 0.985:
                            delta = rng.uniform(20, 210)
                        else:
                            delta = rng.uniform(210, 950)
                        current = current + dt.timedelta(seconds=delta, milliseconds=rng.randint(0, 25))
                    if not (start <= current <= end):
                        continue
                    ppkg = session_pkg
                    if rng.random() < 0.13:
                        vendor_launcher = packages[1] if len(packages) > 1 else packages[0]
                        ppkg = rng.choices([vendor_launcher, "android", "com.google.android.gms", "com.android.settings"], weights=[0.46, 0.30, 0.17, 0.07], k=1)[0]
                    if i == 0 and rng.random() < 0.70:
                        typ = "ACTIVITY_RESUMED"
                    elif i == burst - 1 and rng.random() < 0.63:
                        typ = "ACTIVITY_PAUSED"
                    else:
                        typ = rng.choices(type_names, weights=type_weights, k=1)[0]
                    rec: Dict[str, Any] = {"ts": int(current.timestamp() * 1000) + rng.randint(0, 12), "package": ppkg, "type": typ}
                    cls = classes.get(ppkg, "")
                    if cls:
                        if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION", "CONFIGURATION_CHANGE"):
                            has_cls = rng.random() < min(0.94, class_target + 0.18)
                        elif typ.startswith("FOREGROUND_SERVICE"):
                            has_cls = rng.random() < max(0.25, class_target - 0.30)
                        elif typ.startswith("SCREEN") or typ.startswith("KEYGUARD") or typ == "STANDBY_BUCKET_CHANGED":
                            has_cls = rng.random() < max(0.04, class_target - 0.58)
                        else:
                            has_cls = rng.random() < max(0.08, class_target - 0.48)
                        if has_cls:
                            rec["class"] = cls
                    rows.append(rec)
    rows.sort(key=lambda r: r["ts"])
    while len(rows) > count:
        rows.pop(rng.randrange(len(rows)))
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
        "schema_version": 1,
        "app_version": "1.0.0",
        "android_version": android_version,
        "device_model": model,
        "export_generated_at": iso_z(max_t),
        "window_start": iso_z(min_t),
        "window_end": iso_z(max_t),
        "event_count": len(rows),
        "notes": "Event-level data subject to Android system retention; older periods may be summarised only.",
    }
    meta = {"brand": brand, "seed": seed, "class_target": class_target, "requested_count": count, "requested_days": days}
    return rows, manifest, meta


def analyze_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    pkg = collections.Counter(r["package"] for r in rows)
    typ = collections.Counter(r["type"] for r in rows)
    day = collections.Counter(dt.datetime.fromtimestamp(r["ts"] / 1000, dt.timezone.utc).date().isoformat() for r in rows)
    hour = collections.Counter(dt.datetime.fromtimestamp(r["ts"] / 1000, dt.timezone.utc).hour for r in rows)
    gaps = [(b["ts"] - a["ts"]) / 1000 for a, b in zip(rows, rows[1:])]
    class_pct = sum(1 for r in rows if "class" in r) / len(rows) * 100 if rows else 0
    return {
        "event_count": len(rows),
        "unique_packages": len(pkg),
        "package_entropy": round(entropy(pkg), 3),
        "event_type_entropy": round(entropy(typ), 3),
        "class_presence_pct": round(class_pct, 2),
        "gap_p50_sec": round(quantile(gaps, 0.50), 3),
        "gap_p90_sec": round(quantile(gaps, 0.90), 3),
        "gap_p99_sec": round(quantile(gaps, 0.99), 3),
        "gap_lte_1s_pct": round(sum(g <= 1 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "gap_gt_10m_pct": round(sum(g > 600 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "top_packages": pkg.most_common(30),
        "event_types": typ.most_common(),
        "per_day": dict(sorted(day.items())),
        "per_hour": {str(k): hour[k] for k in sorted(hour)},
        "first_record": rows[0] if rows else None,
        "last_record": rows[-1] if rows else None,
    }


def score_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    score = 100
    reasons = []
    n = metrics["event_count"]
    if not (5000 <= n <= 110000):
        score -= 15; reasons.append("event_count outside observed wide range")
    cp = metrics["class_presence_pct"]
    if not (55 <= cp <= 86):
        score -= 18; reasons.append("class presence outside observed range")
    p50, p90, p99 = metrics["gap_p50_sec"], metrics["gap_p90_sec"], metrics["gap_p99_sec"]
    if not (0.25 <= p50 <= 1.2):
        score -= 18; reasons.append("gap p50 not bursty-realistic")
    if not (8 <= p90 <= 60):
        score -= 12; reasons.append("gap p90 outside observed range")
    if not (80 <= p99 <= 900):
        score -= 8; reasons.append("gap p99 outside observed range")
    le1 = metrics["gap_lte_1s_pct"]
    if not (50 <= le1 <= 73):
        score -= 14; reasons.append("<=1s burst ratio outside observed range")
    long = metrics["gap_gt_10m_pct"]
    if not (0.05 <= long <= 3.0):
        score -= 8; reasons.append(">10m idle gap ratio outside observed range")
    pe = metrics["package_entropy"]
    if not (2.5 <= pe <= 5.4):
        score -= 6; reasons.append("package entropy outside observed range")
    te = metrics["event_type_entropy"]
    if not (1.5 <= te <= 3.5):
        score -= 6; reasons.append("event type entropy outside observed range")
    return {"score": max(0, score), "reasons": reasons or ["all heuristic checks inside observed QA range"]}


def build_zip_bytes(rows: List[Dict[str, Any]], manifest: Dict[str, Any]) -> Tuple[bytes, str]:
    """Build ZIP in memory and return (bytes, sha256)."""
    ndjson = "\n".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in rows) + "\n"
    manifest_str = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("events.ndjson", ndjson)
        z.writestr("manifest.json", manifest_str)
    data = buf.getvalue()
    sha = hashlib.sha256(data).hexdigest()
    return data, sha


def generate_full(brand: str, model: str | None, android_version: str | None, count: int | None, seed: int | None, days: float | None) -> dict:
    rows, manifest, meta = generate_events(brand, model, android_version, count, seed, days)
    metrics = analyze_rows(rows)
    quality = score_metrics(metrics)
    zip_bytes, sha = build_zip_bytes(rows, manifest)
    safe_model = manifest["device_model"].lower().replace(" ", "_").replace("/", "-")
    seed_part = meta.get("seed") if meta.get("seed") is not None else "auto"
    filename = f"sw_events_{safe_model}_{seed_part}.zip"
    return {
        "filename": filename,
        "zip_bytes": zip_bytes,
        "zip_size": len(zip_bytes),
        "zip_sha256": sha,
        "manifest": manifest,
        "meta": meta,
        "metrics": metrics,
        "quality": quality,
    }
