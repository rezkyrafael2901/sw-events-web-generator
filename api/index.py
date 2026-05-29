"""SW Events Generator v2 — improved realism + Vercel-native."""
from __future__ import annotations
import base64, collections, datetime as dt, hashlib, json, math, random, zipfile
from io import BytesIO
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="SW Events Generator")

# Embedded HTML for Vercel serverless compatibility
INDEX_HTML = '<!doctype html>\n<html lang="id">\n<head>\n<meta charset="utf-8"/>\n<meta name="viewport" content="width=device-width,initial-scale=1"/>\n<title>SW Events Generator — Synthetic Android UsageStats</title>\n<script src="https://cdn.tailwindcss.com"></script>\n<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>⚡</text></svg>"/>\n<style>\n*{box-sizing:border-box}\nbody{background:radial-gradient(ellipse at top left,#0f172a,#020617 60%,#000);min-height:100vh}\n.glass{background:rgba(15,23,42,.75);backdrop-filter:blur(20px);border:1px solid rgba(148,163,184,.12)}\n.bar{height:6px;border-radius:3px;background:rgba(52,211,153,.2)}\n.bar>div{height:6px;border-radius:3px;background:#34d399;transition:width .4s}\n.pulse{animation:pulse 2s infinite}\n@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}\n.glow{box-shadow:0 0 30px rgba(52,211,153,.15)}\nselect,input{color-scheme:dark}\n::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}\n</style>\n</head>\n<body class="text-slate-100 antialiased">\n<div class="mx-auto max-w-6xl px-4 py-6 md:py-12">\n\n<!-- HEADER -->\n<div class="mb-8 text-center">\n  <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5">\n    <span class="text-xs font-bold tracking-wide text-emerald-400">SYNTHETIC QA FIXTURE GENERATOR</span>\n    <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-bold text-emerald-300">v2.2</span>\n  </div>\n  <h1 class="text-4xl font-black tracking-tight md:text-6xl">⚡ SW Events</h1>\n  <p class="mt-3 text-base text-slate-400">Generate synthetic Android UsageStats fixtures for QA testing</p>\n  <p class="mt-1 text-xs text-slate-600">14 brands • 132+ models • 26 forensic markers • persona system • 300-500 unique packages</p>\n</div>\n\n<!-- MAIN GRID -->\n<div class="grid gap-6 lg:grid-cols-[400px,1fr]">\n\n  <!-- LEFT: CONFIG -->\n  <form id="f" class="glass rounded-2xl p-6 glow">\n    <h2 class="mb-5 flex items-center gap-2 text-lg font-bold">\n      <span>🎯</span> Generator Config\n    </h2>\n\n    <!-- Brand -->\n    <label class="mb-4 block">\n      <span class="mb-1.5 block text-sm font-semibold text-slate-300">Brand</span>\n      <select name="brand" id="brand" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 transition focus:border-emerald-500 focus:outline-none">\n        <option value="samsung">Samsung</option>\n        <option value="xiaomi">Xiaomi / Redmi</option>\n        <option value="oppo">OPPO</option>\n        <option value="realme">realme</option>\n        <option value="vivo">vivo</option>\n        <option value="poco">POCO</option>\n        <option value="oneplus">OnePlus</option>\n        <option value="google">Google Pixel</option>\n        <option value="asus">ASUS / ROG</option>\n        <option value="motorola">Motorola</option>\n        <option value="tecno">TECNO</option>\n        <option value="infinix">Infinix</option>\n        <option value="advan">Advan</option>\n      </select>\n    </label>\n\n    <!-- Model -->\n    <label class="mb-4 block">\n      <span class="mb-1.5 block text-sm font-semibold text-slate-300">Model <span class="font-normal text-slate-600">(optional)</span></span>\n      <input name="model" id="model" placeholder="Random from brand" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 transition focus:border-emerald-500 focus:outline-none"/>\n      <small id="hint" class="mt-1 block text-xs text-slate-600"></small>\n    </label>\n\n    <!-- Android & Seed -->\n    <div class="mb-4 grid grid-cols-2 gap-3">\n      <label class="block">\n        <span class="mb-1.5 block text-sm font-semibold text-slate-300">Android</span>\n        <input name="android" placeholder="auto" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 focus:border-emerald-500 focus:outline-none"/>\n      </label>\n      <label class="block">\n        <span class="mb-1.5 block text-sm font-semibold text-slate-300">Seed</span>\n        <input name="seed" type="number" min="0" max="999999999" placeholder="random" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 focus:border-emerald-500 focus:outline-none"/>\n      </label>\n    </div>\n\n    <!-- Event Count & Days -->\n    <div class="mb-4 grid grid-cols-2 gap-3">\n      <label class="block">\n        <span class="mb-1.5 block text-sm font-semibold text-slate-300">Event Count</span>\n        <input name="count" type="number" min="1000" max="150000" placeholder="auto (10K-80K)" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 focus:border-emerald-500 focus:outline-none"/>\n      </label>\n      <label class="block">\n        <span class="mb-1.5 block text-sm font-semibold text-slate-300">Days</span>\n        <input name="days" type="number" min="1" max="30" step="0.5" placeholder="auto (7-14)" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 focus:border-emerald-500 focus:outline-none"/>\n      </label>\n    </div>\n\n    <!-- Persona -->\n    <label class="mb-6 block">\n      <span class="mb-1.5 block text-sm font-semibold text-slate-300">User Persona</span>\n      <select name="persona" id="persona" class="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 focus:border-emerald-500 focus:outline-none">\n        <option value="">🎲 Random</option>\n        <option value="student">🎓 Student — social, games, messaging</option>\n        <option value="professional">💼 Professional — productivity, finance, news</option>\n        <option value="elderly">👴 Elderly — messaging, finance</option>\n        <option value="gamer">🎮 Gamer — games, social, streaming</option>\n        <option value="casual">😊 Casual — balanced mix</option>\n        <option value="influencer">📱 Influencer — social, camera, ecommerce</option>\n        <option value="trader">📈 Trader — crypto, finance, news</option>\n        <option value="homemaker">🏠 Homemaker — ecommerce, messaging, games</option>\n      </select>\n    </label>\n\n    <!-- Generate Button -->\n    <button id="btn" type="submit" class="w-full rounded-lg bg-emerald-500 py-3.5 text-lg font-black text-slate-950 transition hover:bg-emerald-400 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed">\n      🚀 Generate\n    </button>\n    <p class="mt-3 text-center text-xs text-slate-600">Synthetic QA fixture • Not real user data • 26 forensic markers</p>\n  </form>\n\n  <!-- RIGHT: RESULT -->\n  <div class="glass rounded-2xl p-6">\n    <div class="mb-5 flex items-center justify-between">\n      <h2 class="text-lg font-bold">📦 Result</h2>\n      <span id="st" class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-500">Waiting</span>\n    </div>\n\n    <!-- Empty State -->\n    <div id="empty" class="flex min-h-[450px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-700/50 text-slate-600">\n      <div class="mb-4 text-5xl">📦</div>\n      <p class="text-base font-semibold text-slate-500">Configure & click Generate</p>\n      <p class="mt-2 text-sm text-slate-600">Pilih brand, persona, lalu klik Generate</p>\n    </div>\n\n    <!-- Result State -->\n    <div id="res" class="hidden">\n      <!-- Stats Cards -->\n      <div class="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">\n        <div class="rounded-xl bg-slate-900/80 p-3">\n          <p class="text-[10px] font-medium uppercase tracking-wider text-slate-500">Device</p>\n          <p id="d" class="mt-1 truncate text-sm font-bold text-white"></p>\n        </div>\n        <div class="rounded-xl bg-slate-900/80 p-3">\n          <p class="text-[10px] font-medium uppercase tracking-wider text-slate-500">Events</p>\n          <p id="ec" class="mt-1 text-sm font-bold text-white"></p>\n        </div>\n        <div class="rounded-xl bg-slate-900/80 p-3">\n          <p class="text-[10px] font-medium uppercase tracking-wider text-slate-500">Packages</p>\n          <p id="pk" class="mt-1 text-sm font-bold text-white"></p>\n        </div>\n        <div class="rounded-xl bg-slate-900/80 p-3">\n          <p class="text-[10px] font-medium uppercase tracking-wider text-slate-500">Score</p>\n          <p id="sc" class="mt-1 text-sm font-bold text-emerald-400"></p>\n        </div>\n      </div>\n\n      <!-- File Info -->\n      <div class="mb-4 rounded-xl bg-slate-900/80 p-3 text-xs">\n        <div class="grid grid-cols-2 gap-2">\n          <p><span class="text-slate-500">Window:</span> <span id="w" class="text-slate-300"></span></p>\n          <p><span class="text-slate-500">Size:</span> <span id="sz" class="text-slate-300"></span></p>\n          <p class="col-span-2 break-all"><span class="text-slate-500">SHA256:</span> <code id="sh" class="text-[10px] text-slate-400"></code></p>\n        </div>\n      </div>\n\n      <!-- Download Button -->\n      <button id="dl" class="mb-5 w-full rounded-lg bg-emerald-500 py-3 text-base font-black text-slate-950 transition hover:bg-emerald-400 active:scale-[0.98]">\n        ⬇️ Download sw_events.zip\n      </button>\n\n      <!-- Charts -->\n      <div class="grid gap-4 md:grid-cols-2">\n        <div class="rounded-xl bg-slate-900/80 p-4">\n          <h3 class="mb-3 text-xs font-bold uppercase tracking-wide text-emerald-500">📊 Top Packages</h3>\n          <ol id="tp" class="space-y-2 text-xs"></ol>\n        </div>\n        <div class="rounded-xl bg-slate-900/80 p-4">\n          <h3 class="mb-3 text-xs font-bold uppercase tracking-wide text-emerald-500">📋 Event Types</h3>\n          <ol id="et" class="space-y-2 text-xs"></ol>\n        </div>\n      </div>\n    </div>\n  </div>\n\n</div>\n\n<!-- FOOTER -->\n<div class="mt-8 text-center text-xs text-slate-700">\n  <p>SW Events Generator v2.3 • 13 brands • 128+ models • Persona system • Forensic-grade synthetic data</p>\n  <p class="mt-1">Built for QA testing • Not real user data</p>\n</div>\n\n</div>\n\n<script>\nconst $ = id => document.getElementById(id);\nlet blob = null, profiles = null;\n\n// Load profiles\nasync function loadProfiles() {\n  try {\n    const r = await fetch(\'/api/profiles\');\n    if (!r.ok) throw new Error(r.statusText);\n    profiles = await r.json();\n    updateHint();\n  } catch (e) {\n    console.warn(\'Failed to load profiles:\', e);\n  }\n}\n\nfunction updateHint() {\n  const b = $(\'brand\').value;\n  if (!profiles || !profiles[b]) return;\n  const p = profiles[b];\n  const models = p.models ? p.models.slice(0, 4).join(\', \') : \'N/A\';\n  const range = p.event_count_range\n    ? p.event_count_range[0].toLocaleString() + \'–\' + p.event_count_range[1].toLocaleString()\n    : \'N/A\';\n  $(\'hint\').textContent = \'Models: \' + models + \' • Events: \' + range;\n}\n\nfunction barrows(list) {\n  if (!list || !list.length) return \'\';\n  const max = list[0][1];\n  return list.map(([name, count]) => {\n    const pct = Math.min(Math.round(count / max * 100), 100);\n    return \'<li class="flex items-center gap-2">\' +\n      \'<span class="w-16 text-right tabular-nums text-slate-500">\' + Number(count).toLocaleString() + \'</span>\' +\n      \'<div class="flex-1 bar"><div style="width:\' + pct + \'%"></div></div>\' +\n      \'<span class="flex-1 truncate text-slate-400">\' + name + \'</span></li>\';\n  }).join(\'\');\n}\n\n// Brand change\n$(\'brand\').addEventListener(\'change\', updateHint);\n\n// Download\n$(\'dl\').addEventListener(\'click\', () => {\n  if (!blob) return;\n  const url = URL.createObjectURL(blob);\n  const a = document.createElement(\'a\');\n  a.href = url;\n  a.download = \'sw_events.zip\';\n  document.body.appendChild(a);\n  a.click();\n  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 200);\n});\n\n// Generate\n$(\'f\').addEventListener(\'submit\', async e => {\n  e.preventDefault();\n  const btn = $(\'btn\');\n  btn.disabled = true;\n  btn.textContent = \'⏳ Generating...\';\n  $(\'st\').textContent = \'Working\';\n  $(\'st\').className = \'rounded-full bg-amber-500/20 px-3 py-1 text-xs text-amber-400 pulse\';\n\n  try {\n    const fd = new FormData(e.target);\n    // Remove empty fields\n    for (const [k, v] of fd.entries()) {\n      if (!v || v === \'\') fd.delete(k);\n    }\n\n    const r = await fetch(\'/api/generate\', { method: \'POST\', body: fd });\n    if (!r.ok) {\n      const err = await r.json().catch(() => ({ detail: r.statusText }));\n      throw new Error(err.detail || \'Generation failed\');\n    }\n\n    const d = await r.json();\n    const s = d.summary;\n\n    // Show result\n    $(\'empty\').classList.add(\'hidden\');\n    $(\'res\').classList.remove(\'hidden\');\n\n    $(\'d\').textContent = s.device_model + \' / Android \' + s.android_version;\n    $(\'ec\').textContent = Number(s.event_count).toLocaleString();\n    $(\'pk\').textContent = s.unique_packages ? Number(s.unique_packages).toLocaleString() : \'N/A\';\n    $(\'sc\').textContent = s.score + \'/100\';\n    $(\'w\').textContent = s.window_start + \' → \' + s.window_end;\n    $(\'sh\').textContent = s.sha256;\n    $(\'sz\').textContent = (s.zip_size / 1024).toFixed(1) + \' KB\';\n\n    $(\'tp\').innerHTML = barrows(s.top_packages);\n    $(\'et\').innerHTML = barrows(s.event_types);\n\n    // Decode base64 zip\n    const bin = atob(d.zip_base64);\n    const arr = new Uint8Array(bin.length);\n    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);\n    blob = new Blob([arr], { type: \'application/zip\' });\n\n    $(\'st\').textContent = \'✅ Ready\';\n    $(\'st\').className = \'rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-400\';\n  } catch (err) {\n    alert(\'Error: \' + err.message);\n    $(\'st\').textContent = \'❌ Error\';\n    $(\'st\').className = \'rounded-full bg-red-500/20 px-3 py-1 text-xs text-red-400\';\n  } finally {\n    btn.disabled = false;\n    btn.textContent = \'🚀 Generate\';\n  }\n});\n\n// Init\nloadProfiles();\n</script>\n</body>\n</html>\n'

# ── Event type weights ──
EW = [
    ("ACTIVITY_RESUMED",14),("ACTIVITY_PAUSED",13),("EVENT_23",14),
    ("NOTIFICATION_INTERRUPTION",17),("NOTIFICATION_SEEN",5.5),
    ("FOREGROUND_SERVICE_START",3.2),("FOREGROUND_SERVICE_STOP",3.0),
    ("STANDBY_BUCKET_CHANGED",17),("USER_INTERACTION",1.3),
    ("SCREEN_INTERACTIVE",0.9),("SCREEN_NON_INTERACTIVE",0.8),
    ("KEYGUARD_HIDDEN",0.3),("KEYGUARD_SHOWN",0.2),("CONFIGURATION_CHANGE",0.1)
]

# ── Indonesian user hour distribution (UTC) ──
BH_INDONESIA = [
    0.040, 0.046, 0.044, 0.046, 0.044, 0.045,
    0.050, 0.055, 0.058, 0.060, 0.055, 0.050,
    0.048, 0.045, 0.042, 0.040, 0.042, 0.045,
    0.050, 0.048, 0.040, 0.035, 0.030, 0.028,
]

# ── System / bloatware packages ──
# ── System / bloatware packages (GENERIC ONLY — no brand-specific) ──
# Brand-specific packages live in SAMSUNG_SYSTEM, XIAOMI_SYSTEM, OPPO_SYSTEM, etc.
SYSTEM_APPS = [
    # Generic AOSP / Android packages
    "com.android.settings","com.android.systemui","com.android.launcher3",
    "com.android.phone","com.android.dialer","com.android.contacts",
    "com.android.mms","com.android.email","com.android.calendar",
    "com.android.calculator2","com.android.camera2","com.android.gallery3d",
    "com.android.music","com.android.deskclock","com.android.browser",
    "com.android.providers.contacts","com.android.providers.media",
    "com.android.providers.downloads","com.android.providers.telephony",
    "com.android.providers.settings","com.android.vending","com.android.chrome",
    "com.android.nfc","com.android.bluetooth","com.android.wifi.resources",
    "com.android.inputmethod.latin","com.android.documentsui",
    "com.android.quicksearchbox","com.android.stk","com.android.stk2",
    "com.android.traceur","com.android.vpndialogs","com.android.wallpapercropper",
    "com.android.wallpaperpicker","com.android.providers.userdictionary",
    "com.android.providers.calendar","com.android.sharedstoragebackup",
    "com.android.externalstorage","com.android.keychain","com.android.location.fused",
    "com.android.shell","com.android.packageinstaller","com.android.se",
    "com.android.incallui","com.android.server.telecom","com.android.mms.service",
    "com.android.htmlviewer","com.android.wallpaper.livepicker",
    "com.android.hotspot2","com.android.carrierdefaultapp",
    "com.android.storagemanager","com.android.printspooler","com.android.proxyhandler",
    "com.android.smspush","com.android.companiondevicemanager","com.android.certinstaller",
    "com.android.networkstack.inprocess","com.android.networkstack.tethering",
    "com.android.inputdevices","com.android.managedprovisioning",
    # Generic Google packages
    "com.google.android.gms","com.google.android.gsf","com.google.android.feedback",
    "com.google.android.tts","com.google.android.apps.maps",
    "com.google.android.apps.photos","com.google.android.apps.docs",
    "com.google.android.gm","com.google.android.youtube",
    "com.google.android.music","com.google.android.videos",
    "com.google.android.apps.messaging","com.google.android.dialer",
    "com.google.android.contacts","com.google.android.deskclock",
    "com.google.android.calculator","com.google.android.apps.nbu.files",
    "com.google.android.apps.chromecast.app","com.google.android.apps.wellbeing",
    "com.google.android.as","com.google.android.partnersetup",
    "com.google.android.play.games","com.google.android.apps.googleassistant",
    "com.google.android.apps.turbo","com.google.ar.core",
    "com.google.android.marvin.talkback","com.google.android.configupdater",
    "com.google.android.ext.services","com.google.android.overlay.gmsconfig",
    "com.google.mainline.telemetry","com.google.android.apps.inputmethod.hindi",
    "com.google.android.apps.translate","com.google.android.apps.accessibility.voiceaccess",
    "com.google.android.apps.tachyon","com.google.android.apps.wearables.maestro.companion",
    "com.google.android.apps.gmm","com.google.android.apps.work.oobconfig",
    "com.google.android.backuptransport","com.google.android.setupwizard",
    "com.google.android.syncadapters.contacts","com.google.android.gms.setup",
    "com.google.android.turboadapter","com.google.ar.lens",
    "com.google.android.webview","com.google.android.networkstack",
    "com.google.android.captiveportallogin","com.google.android.tetheringentitlement",
    "com.google.android.printservice.recommendation",
    "com.google.android.overlay.modules.ext.services",
    "com.google.android.overlay.modules.modulemetadata",
    "com.google.android.safetycore","com.google.android.tag",
    "com.google.android.cellbroadcastreceiver","com.google.android.connectivity.healthlog",
    "com.google.android.ims","com.google.android.as.oss",
    # Additional generic Android components
    "com.google.android.overlay.modules.config┒common","com.google.android.euicc",
    "com.google.android.printservice.recommendation","com.google.android.storagemanager",
    "com.google.android.secontroller","com.google.android.uwb.resources",
    "com.google.mainline.googledts","com.google.mainline.googleroot",
    "com.google.mainline.native","com.google.odad.proxy",
    "com.google.android.providers.media.module",
    "com.google.android.providers.settings",
    "com.android.launcher","com.android.providers.blockednumber",
    "com.android.providers.downloads","com.android.providers.media",
    "com.android.providers.telephony","com.android.providers.contacts",
    "com.android.providers.calendar","com.android.providers.settings",
    "com.android.providers.userdictionary","com.android.providers.downloads.ui",
    "com.android.providers.media.module",
    "com.android.wallpaper.livepicker","com.android.wallpaperbackup",
    "com.android.emergency","com.android.healthconnect.controller",
    "com.android.providers.taskstack","com.android.providers.settings",
    "com.android.credentialmanager","com.android.intentresolver",
    "com.android.bips","com.android.bookmarkprovider",
    "com.android.cellbroadcastreceiver","com.android.cellbroadcastservice",
    "com.android.wallpaper.holospiral","com.android.wallpaper.noise",
    "com.android.dreams.basic","com.android.dreams.phototable",
    "com.google.android.tts","com.google.android.feedback",
    "com.google.android.deskclock","com.google.android.calculator",
    "com.google.android.music","com.google.android.videos",
    "com.google.android.apps.photos","com.google.android.apps.docs",
    "com.google.android.apps.maps","com.google.android.apps.messaging",
    "com.google.android.apps.googleassistant","com.google.android.apps.wellbeing",
    "com.google.android.apps.turbo","com.google.android.apps.fitness",
    "com.google.android.apps.nbu.files","com.google.android.apps.googleone",
    "com.google.android.apps.families","com.google.android.apps.accessibility.audience",
    "com.google.android.apps.googlehome","com.google.android.apps.gmm",
    "com.google.android.apps.work.oobconfig","com.google.android.apps.youtube.music",
    "com.google.android.googlequicksearchbox",
    "com.google.android.keep","com.google.android.storagemanager",
    "com.google.android.soundpicker","com.google.android.dialer",
    "com.google.android.contacts","com.google.android.calendar",
    "com.google.ar.core","com.google.ar.lens",
]

SAMSUNG_SYSTEM = [
    "com.samsung.android.messaging","com.samsung.android.dialer",
    "com.samsung.android.contacts","com.samsung.android.calendar",
    "com.samsung.android.app.clock","com.samsung.android.calculator",
    "com.samsung.android.camera","com.samsung.android.gallery3d",
    "com.samsung.android.music","com.samsung.android.video",
    "com.samsung.android.email.provider","com.samsung.android.fmm",
    "com.samsung.android.game.gamehome","com.samsung.android.game.gametools",
    "com.samsung.android.ardrawing","com.samsung.android.aremoji",
    "com.samsung.android.app.routines","com.samsung.android.bixby.agent",
    "com.samsung.android.bixby.service","com.samsung.android.visionintelligence",
    "com.samsung.android.spay","com.samsung.android.mateagent",
    "com.samsung.android.app.tips","com.samsung.android.themestore",
    "com.samsung.android.icecone","com.samsung.android.forest",
    "com.samsung.android.app.sharelive","com.samsung.android.kidsinstaller",
    "com.samsung.android.app.spage","com.samsung.android.dqagent",
    "com.samsung.android.securitylogagent","com.samsung.android.mobileservice",
    "com.samsung.android.app.omcagent","com.samsung.android.samsungpass",
    "com.samsung.android.samsungpassautofill","com.samsung.android.authfw",
    "com.samsung.android.kgclient","com.samsung.android.MtpApplication",
    "com.samsung.android.server.iris","com.samsung.android.privateshare",
    "com.samsung.android.app.telephonyui","com.samsung.android.incallui",
    "com.samsung.android.da.daagent","com.samsung.android.mdx.kit",
    "com.samsung.android.wellbeing","com.samsung.android.app.galaxyfinder",
    "com.samsung.android.honeyboard","com.samsung.android.setting.multisound",
    "com.sec.android.app.launcher","com.sec.android.app.sbrowser",
    "com.sec.android.app.popupcalculator","com.sec.android.gallery3d",
    "com.sec.android.daemonapp","com.sec.android.provider.logsprovider",
    "com.sec.android.app.bluetoothtest","com.sec.android.easyMover",
    "com.sec.android.easyMover.Agent","com.sec.msc.android",
    "com.sec.android.app.camera","com.sec.android.app.myfiles",
    "com.sec.android.app.fmradio",
    "com.sec.android.widgetapp.easymodecontactswidget",
    "com.sec.android.widgetapp.digitalclock",
    "com.sec.android.provider.emergencylocation",
]

XIAOMI_SYSTEM = [
    "com.miui.home","com.miui.gallery","com.miui.player",
    "com.miui.video","com.miui.weather2","com.miui.calculator",
    "com.miui.compass","com.miui.fm","com.miui.notes",
    "com.miui.screenrecorder","com.miui.securitycenter",
    "com.miui.securitycore","com.miui.cleanmaster",
    "com.miui.personalassistant","com.miui.bugreport",
    "com.miui.mishare","com.miui.misound","com.miui.voiceassist",
    "com.miui.cloudservice","com.miui.cloudbackup","com.miui.backup",
    "com.miui.packageinstaller","com.miui.daemon","com.miui.aod",
    "com.miui.extraphoto","com.miui.mediaviewer","com.miui.contentcatcher",
    "com.miui.freeform","com.miui.guardprovider","com.miui.notification",
    "com.miui.phrase","com.miui.smsextra","com.miui.system",
    "com.miui.touchassistant","com.miui.vidaaiv4",
    "com.miui.miwallpaper","com.miui.hybrid",
    "com.xiaomi.mipicks","com.xiaomi.xmsf","com.xiaomi.joyose",
    "com.xiaomi.finddevice","com.xiaomi.simactivate",
    "com.xiaomi.aiasst.service","com.xiaomi.account",
    "com.xiaomi.drivemode","com.xiaomi.payment",
    "com.xiaomi.misettings","com.xiaomi.barrage",
    "com.xiaomi.channel","com.xiaomi.shop","com.xiaomi.smarthome",
    "com.xiaomi.scanner","com.mi.android.globallauncher",
]

OPPO_SYSTEM = [
    "com.oppo.launcher","com.oppo.camera","com.oppo.gallery3d",
    "com.oppo.music","com.oppo.video","com.oppo.weather2",
    "com.oppo.calculator","com.oppo.compass","com.oppo.fmradio",
    "com.oppo.note","com.oppo.screenrecorder","com.oppo.safecenter",
    "com.oppo.cleanmaster","com.oppo.personalassistant",
    "com.oppo.bugreport","com.oppo.mishare","com.oppo.misound",
    "com.oppo.voiceassist","com.oppo.cloudservice","com.oppo.cloudbackup",
    "com.oppo.backup","com.oppo.packageinstaller","com.oppo.daemon",
    "com.oppo.aod","com.oppo.extraphoto","com.oppo.mediaviewer",
    "com.oppo.quicksearchbox","com.oppo.exserviceui","com.oppo.atlas",
    "com.oppo.operationManual","com.oppo.usercenter","com.oppo.powermonitor",
    "com.oppo.securepay","com.oppo.speechassist","com.oppo.deepthinker",
    "com.oppo.store","com.oppo.push","com.oppo.screenrecorder",
    "com.coloros.assistant","com.coloros.athena","com.coloros.bootreg",
    "com.coloros.childrenspace","com.coloros.compass2",
    "com.coloros.deepthinker","com.coloros.encryption",
    "com.coloros.floatassistant","com.coloros.focusmode",
    "com.coloros.gamespace","com.coloros.gallery3d",
    "com.coloros.healthcheck","com.coloros.healthservice",
    "com.coloros.notificationmanager","com.coloros.ocrservice",
    "com.coloros.oppomultiapp","com.coloros.oshare",
    "com.coloros.phonemanager","com.coloros.safecenter",
    "com.coloros.safesdkproxy","com.coloros.screenshot",
    "com.coloros.securitypermission","com.coloros.smartsidebar",
    "com.coloros.soundrecorder","com.coloros.uxdesign",
    "com.coloros.weather2","com.coloros.wirelesssettings",
    "com.coloros.recents","com.coloros.operationManual",
    "com.coloros.assistantscreen","com.coloros.screenrecorder",
    "com.heytap.cloud","com.heytap.browser","com.heytap.colorfulengine",
    "com.heytap.habit.analysis","com.heytap.market","com.heytap.mcs",
    "com.heytap.pictorial","com.heytap.themestore","com.heytap.usercenter",
    "com.nearme.gamecenter","com.nearme.atlas",
    "com.heytap.mcsservice","com.heytap.openid",
]

INFINIX_SYSTEM = [
    "com.transsion.hilauncher","com.transsion.XOSLauncher",
    "com.transsion.microintelligence","com.transsion.soundrecorder",
    "com.transsion.XOS.chargeanim","com.transsion.XOS.weather",
    "com.transsion.XOS.compass","com.transsion.XOS.calculator",
    "com.transsion.XOS.fmradio","com.transsion.XOS.gallery3d",
    "com.transsion.XOS.music","com.transsion.XOS.video",
    "com.transsion.XOS.securitycenter","com.transsion.XOS.cleanmaster",
    "com.transsion.XOS.personalassistant","com.transsion.XOS.bugreport",
    "com.transsion.XOS.mishare","com.transsion.XOS.misound",
    "com.transsion.XOS.voiceassist","com.transsion.XOS.cloudservice",
    "com.transsion.XOS.cloudbackup","com.transsion.XOS.backup",
    "com.transsion.XOS.packageinstaller","com.transsion.XOS.daemon",
    "com.transsion.XOS.aod","com.transsion.XOS.extraphoto",
    "com.transsion.XOS.mediaviewer","com.transsion.XOS.quicksearchbox",
    "com.transsion.XOS.safecenter","com.transsion.XOS.screenshot",
    "com.transsion.XOS.soundrecorder","com.transsion.XOS.uxdesign",
    "com.transsion.XOS.weather2","com.transsion.XOS.wirelesssettings",
]

VIVO_SYSTEM = [
    "com.vivo.weather","com.vivo.browser","com.vivo.video","com.vivo.music",
    "com.vivo.notes","com.vivo.email","com.vivo.translator","com.vivo.scanner",
    "com.vivo.gallery","com.vivo.calculator","com.vivo.clock","com.vivo.compass",
    "com.vivo.filemanager","com.vivo.launcher","com.vivo.camera",
    "com.vivo.permissionmanager","com.vivo.abe","com.vivo.smartshare",
    "com.vivo.globalgenius","com.vivo.magazine","com.vivo.FMRadio",
    "com.vivo.vivokaili","com.vivo.sos","com.vivo.networkchecker",
    "com.vivo.phonefix","com.vivo.bbkaccount","com.vivo.appstore",
    "com.vivo.gamecenter","com.vivo.TipsUserGuide",
    "com.vivo.widget.weather","com.vivo.widget.calendar","com.vivo.widget.clock",
    "com.bbk.launcher.theme","com.bbk.launcher2","com.bbk.calendar",
    "com.bbk.cloud","com.bbk.account.sync",
]

ADVAN_SYSTEM = [
    "com.advan.dlauncher","com.advan.launcher","com.advan.camera",
    "com.advan.filemanager","com.advan.gallery","com.advan.calculator",
    "com.advan.clock","com.advan.weather","com.advan.fmradio",
    "com.advan.music","com.advan.video","com.advan.notes",
    "com.advan.browser","com.advan.compass","com.advan.soundrecorder",
    "com.advan.securitycenter","com.advan.cleanmaster",
    "com.advan.backuprestore","com.advan.thememanager",
    "com.advan.appstore","com.bubble.umusic",
]

ASUS_SYSTEM = [
    "com.asus.launcher","com.asus.camera","com.asus.gallery","com.asus.filemanager",
    "com.asus.calculator","com.asus.clock","com.asus.weather","com.asus.fmradio",
    "com.asus.music","com.asus.video","com.asus.notes","com.asus.browser",
    "com.asus.compass","com.asus.soundrecorder","com.asus.zenui",
    "com.asus.mobilemanager","com.asus.task","com.asus.splendid",
    "com.asus.supernote","com.asus.azs","com.asus.audiowizard",
    "com.asus.theme","com.asus.email","com.asus.contacts","com.asus.messaging",
    "com.asus.phone","com.asus.settings","com.asus.systemupdate",
    "com.asus.custompresetsettings","com.asus.gamecenter",
]

GOOGLE_SYSTEM = [
    "com.google.android.apps.nexuslauncher","com.google.android.GoogleCamera",
    "com.google.android.apps.photos","com.google.android.apps.maps",
    "com.google.android.gm","com.google.android.calendar","com.google.android.deskclock",
    "com.google.android.calculator","com.google.android.contacts",
    "com.google.android.dialer","com.google.android.messaging",
    "com.google.android.youtube","com.google.android.music",
    "com.google.android.videos","com.google.android.apps.docs",
    "com.google.android.apps.turbo","com.google.android.apps.wellbeing",
    "com.google.android.as","com.google.android.settings.intelligence",
    "com.google.android.cellbroadcastreceiver","com.google.android.overlay.modules.cellbroadcastservice",
    "com.google.android.networkstack","com.google.android.providers.media.module",
    "com.google.android.permissioncontroller","com.google.android.modulemetadata",
    "com.google.android.printservice.recommendation","com.google.android.syncadapters.calendar",
    "com.google.android.syncadapters.contacts","com.google.android.tag",
    "com.google.android.partnersetup","com.google.android.feedback",
    "com.google.android.backuptransport","com.google.android.configupdater",
    "com.google.android.webview","com.google.android.trichromelibrary",
]

ONEPLUS_SYSTEM = [
    "com.oneplus.launcher","com.oneplus.camera","com.oneplus.gallery",
    "com.oneplus.filemanager","com.oneplus.calculator","com.oneplus.clock",
    "com.oneplus.weather","com.oneplus.fmradio","com.oneplus.music",
    "com.oneplus.video","com.oneplus.notes","com.oneplus.compass",
    "com.oneplus.soundrecorder","com.oneplus.screenrecorder",
    "com.oneplus.security","com.oneplus.appupdater","com.oneplus.backuprestore",
    "com.oneplus.wifiapsettings","com.oneplus.skin","com.oneplus.opswitch",
    "com.oneplus.simsettings","com.oneplus.cloud","com.oneplus.account",
    "com.oos.oself","com.oos.oiface","com.oos.ohealth",
    "com.heytap.cloud","com.heytap.browser",
]

MOTOROLA_SYSTEM = [
    "com.motorola.launcher3","com.motorola.camera3","com.motorola.gallery",
    "com.motorola.filemanager","com.motorola.calculator","com.motorola.clock",
    "com.motorola.weather","com.motorola.fmradio","com.motorola.music",
    "com.motorola.motocare","com.motorola.actions","com.motorola.bug2",
    "com.motorola.audio","com.motorola.faceunlock","com.motorola.gestures",
    "com.motorola.help","com.motorola.hiddenmenu","com.motorola.moto",
    "com.motorola.motodisplay","com.motorola.setup","com.motorola.targetnotif",
    "com.motorola.videoplayer","com.motorola.cnw","com.motorola.brnhprovision",
    "com.motorola.process.system","com.motorola.android.fmradio",
]

POCO_SYSTEM = [
    "com.mi.launcher","com.miui.home","com.miui.gallery","com.miui.player",
    "com.miui.video","com.miui.weather2","com.miui.calculator",
    "com.miui.fm","com.miui.notes","com.miui.securitycenter",
    "com.miui.cleanmaster","com.miui.mishare","com.miui.backup",
    "com.xiaomi.mipicks","com.xiaomi.xmsf","com.xiaomi.finddevice",
    "com.xiaomi.joyose","com.xiaomi.account","com.xiaomi.shop",
    "com.xiaomi.smarthome","com.xiaomi.scanner","com.mi.android.globallauncher",
    "com.miui.aod","com.miui.daemon","com.miui.packageinstaller",
]

# ── Background services ──
BG_SERVICES = [
    "com.google.android.gms.policy_sidecar_aps","com.google.android.gms.feedback",
    "com.google.android.gms.icing","com.google.android.gms.nearby",
    "com.google.android.gms.persistent","com.google.android.gms.ui",
    "com.google.android.gms.unstable","com.google.android.gms.chimera",
    "com.google.android.gms.auth","com.google.android.gms.location",
    "com.google.android.gms.cast.service","com.google.android.gms.backup",
    "com.google.android.gms.measurement","com.google.android.gms.ads",
    "com.google.android.gms.clearcut","com.google.android.gms.config",
    "com.google.android.gms.tapandpay","com.google.android.gms.wallet",
    "com.google.android.gms.security","com.google.android.gms.telephonyspam",
    "com.google.android.gms.update","com.google.android.gms.vision",
    "com.google.android.gms.wearable","com.google.android.gms.matchstick",
    "com.google.android.gms.deviceconnection","com.google.android.gms.droidguard",
    "com.google.android.gms.appinvite","com.google.android.gms.auth.api.phone",
    "com.google.android.instantapps.supervisor","com.google.android.webview",
    "com.google.android.networkstack","com.google.android.captiveportallogin",
    "com.google.android.documentsui","com.google.android.permissioncontroller",
    "com.google.android.packageinstaller","com.google.android.ext.shared",
    "com.android.vpndialogs","com.android.hotspot2","com.android.carrierdefaultapp",
    "com.android.storagemanager","com.android.shell","com.android.se",
    "com.android.traceur","com.android.wallpaperbackup","com.android.wallpapercropper",
    "com.android.providers.downloads.ui","com.android.providers.media.module",
    "com.android.providers.calendar","com.android.providers.userdictionary",
    "com.android.providers.blockednumber","com.android.certinstaller",
    "com.android.companiondevicemanager","com.android.htmlviewer",
    "com.android.inputdevices","com.android.keychain",
    "com.android.location.fused","com.android.managedprovisioning",
    "com.android.networkstack.inprocess","com.android.networkstack.tethering",
    "com.android.printspooler","com.android.proxyhandler",
    "com.android.server.telecom","com.android.simappdialog",
    "com.android.smspush","com.dsi.ant.server",
    "com.qualcomm.qti.qdma","com.qualcomm.qti.cne",
    "com.qualcomm.qti.telephonyservice","com.qualcomm.qti.ims",
    "org.codeaurora.ims","com.quicinc.cne.CNEService",
    "com.mediatek.ims","com.mediatek.telephony","com.mediatek.ygps",
    "com.sprd.engineermode","com.sprd.validationtools","com.unisoc.phone",
    "com.google.android.as","com.google.android.as.oss",
    "com.google.android.cellbroadcastreceiver","com.google.android.configupdater",
    "com.google.android.connectivity.healthlog","com.google.android.ims",
    "com.google.android.safetycore","com.google.android.tag",
    "com.google.mainline.telemetry","com.google.android.overlay.gmsconfig",
    "com.google.android.overlay.modules.ext.services",
    "com.google.android.overlay.modules.modulemetadata",
    "com.google.android.tetheringentitlement",
    "com.google.android.printservice.recommendation",
    "com.qualcomm.qti.services.systemhelper","com.qualcomm.qti.callfeaturessetting",
    "com.mediatek.mtklogger","com.mediatek.providers.drm",
    "com.mediatek.security","com.mediatek.nlpservice",
    "com.megvii.faceassistant","com.fingerprints.service",
    "com.goodix.fingerprint","com.arcsoft.arcfuseloader",
    "com.dolby.daxservice","com.dolby.ds1appUI",
    "com.realtek.hardware","com.immersion.haptics",
    "com.nxp.nfc","com.broadcom.nfc","com.marvell.nfc",
    "com.sonyericsson.extras",
    # Additional generic background services & components
    "com.qualcomm.qti.workloadclassifier","com.qualcomm.qti.qmmi",
    "com.qualcomm.qti.dynamicddsservice","com.qualcomm.qti.uimGbaApp",
    "com.qualcomm.qti.lpa","com.qualcomm.qti.ims.rcsservice",
    "com.qualcomm.qti.qdma","com.qualcomm.qti.cne",
    "com.mediatek.gnss.nonframeworklbs","com.mediatek.mtklogger",
    "com.mediatek.providers.drm","com.mediatek.security",
    "com.mediatek.nlpservice","com.mediatek.thermalmanager",
    "com.mediatek.atfwd","com.mediatek.capctrl.service",
    "com.google.android.euicc","com.google.android.overlay.modules.config┒common",
    "com.google.android.overlay.modules.modulemetadata.api31",
    "com.google.android.overlay.modules.modulemetadata.api32",
    "com.google.android.overlay.modules.modulemetadata.api33",
    "com.google.android.overlay.modules.modulemetadata.api34",
    "com.google.android.configupdater","com.google.android.ext.shared",
    "com.google.android.trichromelibrary","com.google.android.tts",
    "com.google.mainline.telemetry","com.google.android.cellbroadcastservice",
    "com.google.android.permissioncontroller",
    "com.android.providers.downloads","com.android.providers.media",
    "com.android.providers.telephony","com.android.providers.calendar",
    "com.android.providers.contacts","com.android.providers.userdictionary",
    "com.android.providers.blockednumber","com.android.emergency",
    "com.android.healthconnect.controller",
    "com.android.systemui","com.android.settings",
    "com.android.nfc","com.android.bluetooth",
    "com.android.launcher3","com.android.providers.media.module",
    "com.fingerprints.samsung","com.samsung.android.biometrics.app.fingerprint",
    "com.mtk.telephony","com.mtk.mtklogger","com.mtk.gnss",
    "com.unisoc.phone","com.unisoc.server.telecom",
    "com.unisoc.providers.telephony","com.unisoc.ims",
    "com.sprd.engineermode","com.sprd.validationtools",
    "com.sprd.telephony","com.sprd.providers.telephony",
    "com.dsi.ant.server","com.qualcomm.qti.services.systemhelper",
    "com.qualcomm.qti.callfeaturessetting","com.qualcomm.qti.telephonyservice",
    "com.qualcomm.qti.ims","org.codeaurora.ims","com.quicinc.cne.CNEService",
    "com.google.android.overlay.modules.ext.services.config",
    "com.google.android.overlay.modules.statsd",
    "com.google.android.overlay.modules.permissioncontroller",
]

# ── Common user apps (package, weight) ──
COMMON_USER_APPS = [
    ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",10),("com.instagram.android","com.instagram.android.MainTabActivity",5),
    ("com.facebook.katana","com.facebook.katana.LoginActivity",4),("com.facebook.lite","com.facebook.lite.MainActivity",4),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",4),
    ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3),("com.twitter.android","com.twitter.android.MainActivity",2),("com.spotify.music","com.spotify.music.MainActivity",2),
    ("com.netflix.mediaclient","com.netflix.mediaclient.ui.launch.UIWebViewActivity",1.5),("com.google.android.apps.youtube.music","com.google.android.apps.youtube.music.HomeActivity",1.5),
    ("com.zhiliaoapp.musically.go","com.zhiliaoapp.musically.go.SplashActivity",2),("com.kwai.video","com.kwai.video.SplashActivity",1),("com.pinterest","com.pinterest.activity.PinterestActivity",1),
    ("com.linkedin.android","com.linkedin.android.authenticator.LaunchActivity",1),("com.reddit.frontpage","com.reddit.frontpage.SplashActivity",1),("com.quora.android","com.quora.android.SplashActivity",0.5),
    ("id.dana","id.dana.MainActivity",3),("com.gojek.app","com.gojek.app.SplashActivity",3),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",3),
    ("com.tokopedia.tkpd","com.tokopedia.tkpd.activity.SplashScreenActivity",2),("com.grab.id","com.grab.id.SplashActivity",2),("com.bukalapak.android","com.bukalapak.android.SplashActivity",1),
    ("id.co.bca","id.co.bca.mobile.banking.MainActivity",2),("id.co.bni","id.co.bni.mobile.MainActivity",1.5),("id.co.bri","id.co.bri.mobile.MainActivity",1.5),
    ("id.co.bankbkemobile.digitalbank","id.co.bankbkemobile.digitalbank.MainActivity",1),("com.telkom.mwallet","com.telkom.mwallet.MainActivity",1),
    ("com.binance.dev","com.binance.dev.SplashActivity",2),("com.coinbase.android","com.coinbase.android.SplashActivity",1),("com.okx.wallet","com.okx.wallet.SplashActivity",1),
    ("com.android.chrome","com.google.android.apps.chrome.Main",3),("org.mozilla.firefox","org.mozilla.firefox.MainActivity",1),("com.opera.browser","com.opera.browser.MainActivity",1),
    ("com.microsoft.teams","com.microsoft.teams.ui.SplashActivity",1.5),("com.microsoft.office.outlook","com.microsoft.office.outlook.MainActivity",1),
    ("com.google.android.apps.docs","com.google.android.apps.docs.app.NewMainProxyActivity",1.5),("com.google.android.apps.maps","com.google.android.maps.MapsActivity",2),
    ("cn.wps.moffice_eng","cn.wps.moffice_eng.MainActivity",1),("com.adobe.reader","com.adobe.reader.MainActivity",0.5),
    ("com.duolingo","com.duolingo.SplashActivity",1),("com.shazam.android","com.shazam.android.MainActivity",0.5),("com.canva.editor","com.canva.editor.SplashActivity",1),
    ("com.picsart.studio","com.picsart.studio.SplashActivity",1),("com.ubercab","com.ubercab.MainActivity",1),("com.airbnb.android","com.airbnb.android.MainActivity",0.5),
    ("com.booking","com.booking.MainActivity",0.5),("com.traveloka.android","com.traveloka.android.SplashActivity",1),
    ("com.mobile.legends","com.mobile.legends.SplashActivity",2),("com.garena.game.codm","com.garena.game.codm.SplashActivity",1.5),
    ("com.supercell.clashofclans","com.supercell.clashofclans.GameApp",1),("com.pubg.mobile","com.pubg.mobile.SplashActivity",1.5),
    ("com.dts.freefiremax","com.dts.freefiremax.SplashActivity",1),("com.joox","com.joox.MainActivity",1),("com.deezer.android.app","com.deezer.android.app.MainActivity",0.5),
    ("tv.twitch.android.app","tv.twitch.android.app.MainActivity",1),("com.discord","com.discord.main.MainActivity",1),
    ("com.snapchat.android","com.snapchat.android.LandingPageActivity",1.5),("com.viber.voip","com.viber.voip.MainActivity",0.5),
    ("com.skype.raider","com.skype.raider.MainActivity",0.5),("us.zoom.videomeetings","us.zoom.videomeetings.MainActivity",1),
    ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",1),("com.anthropic.claude","com.anthropic.claude.MainActivity",0.5),
    ("com.ebay.mobile","com.ebay.mobile.MainActivity",0.5),("com.amazon.mShop.android.shopping","com.amazon.mShop.android.shopping.MainActivity",0.5),
    ("com.aliexpress","com.aliexpress.MainActivity",1),("com.lazada.android","com.lazada.android.MainActivity",1),
    ("com.pou.app","com.pou.app.MainActivity",0.5),("com.king.candycrushsaga","com.king.candycrushsaga.MainActivity",0.5),
    ("com.imdb.mobile","com.imdb.mobile.MainActivity",0.3),("com.medium.reader","com.medium.reader.SplashActivity",0.3),
    ("com.nytimes.android","com.nytimes.android.SplashActivity",0.3),("com.bbc.news","com.bbc.news.SplashActivity",0.3),
    ("com.detik.android","com.detik.android.SplashActivity",0.3),("id.co.kompas","id.co.kompas.SplashActivity",0.3),
    # Additional Indonesian & regional apps (expanded for 300-500 unique packages)
    ("id.co.bsi.mobile","id.co.bsi.mobile.MainActivity",0.8),("com.btn.mobile","com.btn.mobile.MainActivity",0.5),
    ("id.co.bankmandiri","id.co.bankmandiri.MainActivity",0.7),("com.bca","com.bca.MainActivity",0.6),
    ("com.doku.dokuapp","com.doku.dokuapp.MainActivity",0.4),("com.ovo.id","com.ovo.id.MainActivity",0.8),
    ("com.linkaja.android","com.linkaja.android.SplashActivity",0.6),("com.shopeepay.id","com.shopeepay.id.MainActivity",0.5),
    ("com.gopay","com.gopay.MainActivity",0.4),("com.tiket.android","com.tiket.android.SplashActivity",0.5),
    ("com.sicepat.express","com.sicepat.express.SplashActivity",0.3),("com.jnt.id","com.jnt.id.SplashActivity",0.3),
    ("com.pos.indonesia","com.pos.indonesia.SplashActivity",0.2),("com.vidio.android","com.vidio.android.SplashActivity",0.8),
    ("com.mola.mola","com.mola.mola.SplashActivity",0.3),("com.wechat","com.wechat.ui.SplashActivity",0.5),
    ("com.linecorp.android.line","com.linecorp.android.line.SplashActivity",0.6),
    ("com.cinema31","com.cinema31.SplashActivity",0.3),("com.tokopedia.seller","com.tokopedia.seller.SplashActivity",0.4),
    ("com.shopee.seller","com.shopee.seller.SplashActivity",0.3),("com.midtrans","com.midtrans.SplashActivity",0.2),
    ("com.flip","com.flip.SplashActivity",0.3),("id.co.pintek","id.co.pintek.SplashActivity",0.2),
    ("com.stockbit","com.stockbit.SplashActivity",0.4),("com.indodax","com.indodax.SplashActivity",0.3),
    ("com.pintu","com.pintu.SplashActivity",0.3),("com.bybit","com.bybit.SplashActivity",0.3),
    ("com.tiktok.shop","com.tiktok.shop.SplashActivity",0.4),("com.temu","com.temu.SplashActivity",0.3),
    ("com.threads.android","com.threads.android.SplashActivity",0.4),("com.mastodon.social","com.mastodon.social.SplashActivity",0.2),
    ("com.zhiliaoapp.musically","com.zhiliaoapp.musically.SplashActivity",0.3),
    ("com.capcut.android","com.capcut.android.SplashActivity",0.5),("com.inshot.app","com.inshot.app.SplashActivity",0.3),
    ("com.vsco.cam","com.vsco.cam.SplashActivity",0.3),("com.swiftkey.swiftkey","com.swiftkey.swiftkey.SplashActivity",0.4),
    ("com.grammarly.android","com.grammarly.android.SplashActivity",0.2),("com.trello","com.trello.SplashActivity",0.3),
    ("com.notion.id","com.notion.id.SplashActivity",0.3),("com.slack","com.slack.SplashActivity",0.3),
    ("com.figma","com.figma.SplashActivity",0.2),("com.nerdvault.bmkg","com.nerdvault.bmkg.SplashActivity",0.3),
    ("com.bpjs.mobile","com.bpjs.mobile.SplashActivity",0.3),("com.pajak","com.pajak.SplashActivity",0.2),
    ("com.wetv.vod","com.wetv.vod.SplashActivity",0.3),
    ("com.cnn.indonesia","com.cnn.indonesia.SplashActivity",0.3),
    ("com.tempo","com.tempo.SplashActivity",0.2),("id.co.liputan6","id.co.liputan6.SplashActivity",0.3),
    ("com.tirto.id","com.tirto.id.SplashActivity",0.2),("com.brilio.net","com.brilio.net.SplashActivity",0.2),
    ("com.suara.com","com.suara.com.SplashActivity",0.2),("com.kumparan","com.kumparan.SplashActivity",0.3),
    ("com.blibli.commerce","com.blibli.commerce.SplashActivity",0.5),
    ("com.zalora.android","com.zalora.android.SplashActivity",0.3),("com.sepulsa","com.sepulsa.SplashActivity",0.2),
    ("com.kredivo","com.kredivo.SplashActivity",0.3),("com.ayopop","com.ayopop.SplashActivity",0.2),
    ("com.bukalapak.seller","com.bukalapak.seller.SplashActivity",0.2),
    ("com.garena.game.kgtw","com.garena.game.kgtw.SplashActivity",0.3),
    ("com.activision.callofduty.warzone","com.activision.callofduty.warzone.SplashActivity",0.3),
    ("com.riot.league.wildrift","com.riot.league.wildrift.SplashActivity",0.3),
    ("com.genshin.hoyoverse","com.genshin.hoyoverse.SplashActivity",0.4),
    ("com.habby.archero","com.habby.archero.SplashActivity",0.2),
    ("com.innersloth.spacemafia","com.innersloth.spacemafia.SplashActivity",0.2),
    ("com.google.android.apps.chime","com.google.android.apps.chime.SplashActivity",0.2),
    ("com.google.ar.lens","com.google.ar.lens.SplashActivity",0.2),
    ("com.google.android.apps.nearby","com.google.android.apps.nearby.SplashActivity",0.2),
    ("com.google.android.apps.adm","com.google.android.apps.adm.SplashActivity",0.2),
    ("com.microsoft.office.word","com.microsoft.office.word.SplashActivity",0.3),
    ("com.microsoft.office.excel","com.microsoft.office.excel.SplashActivity",0.3),
    ("com.microsoft.office.powerpoint","com.microsoft.office.powerpoint.SplashActivity",0.2),
    ("com.dropbox.android","com.dropbox.android.SplashActivity",0.3),
    ("com.evernote","com.evernote.SplashActivity",0.3),
    ("com.todoist","com.todoist.SplashActivity",0.2),
    ("com.ticktick.task","com.ticktick.task.SplashActivity",0.2),
    ("com.canva.canva","com.canva.canva.SplashActivity",0.3),
    ("com.adobe.lrmobile","com.adobe.lrmobile.SplashActivity",0.2),
    ("com.snapseed","com.snapseed.SplashActivity",0.3),
    ("com.google.android.apps.fitness","com.google.android.apps.fitness.SplashActivity",0.3),
    ("com.google.android.apps.families","com.google.android.apps.families.SplashActivity",0.2),
    ("com.samsung.health","com.samsung.health.SplashActivity",0.3),
    ("com.mi.health","com.mi.health.SplashActivity",0.2),
    ("com.huawei.health","com.huawei.health.SplashActivity",0.2),
    ("com.strava","com.strava.SplashActivity",0.2),
    ("com.myfitnesspal.android","com.myfitnesspal.android.SplashActivity",0.2),
    ("com.calm.android","com.calm.android.SplashActivity",0.2),
    ("com.headspace.android","com.headspace.android.SplashActivity",0.2),
    ("com.photomath.app","com.photomath.app.SplashActivity",0.3),
    ("com.babbel.mobile.android.en","com.babbel.mobile.android.en.SplashActivity",0.2),
    ("com.quizlet.quizletandroid","com.quizlet.quizletandroid.SplashActivity",0.2),
    ("com.khanacademy.android","com.khanacademy.android.SplashActivity",0.3),
    ("com.udemy.android","com.udemy.android.SplashActivity",0.2),
    ("com.coursera.android","com.coursera.android.SplashActivity",0.3),
    ("com.google.classroom","com.google.classroom.SplashActivity",0.3),
]

# ── Brand profiles ──
BP: Dict[str, Any] = {
    "samsung": {
        "models": ["samsung SM-A155F","samsung SM-A256B","samsung SM-A356E","samsung SM-A556E","samsung SM-S911B","samsung SM-A165F","samsung SM-A057G","samsung SM-S711B","samsung SM-S921B","samsung SM-S926B","samsung SM-S928B","samsung SM-F741B","samsung SM-F956B","samsung SM-A566B","samsung SM-S931B","samsung SM-S936B","samsung SM-S938B"],
        "av": ["11","12","13","14"], "ec": [20000, 90000], "cp": [0.62, 0.84],
        "system": SAMSUNG_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20.5),("com.sec.android.app.launcher","com.sec.android.app.launcher.Launcher",15),("android","android.app.Activity",5.8),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.4),("com.instagram.android","com.instagram.android.MainTabActivity",4.3),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",3.8),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.7),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3.5),("com.android.chrome","com.google.android.apps.chrome.Main",3.4),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",3.0),("com.samsung.android.dialer","com.samsung.android.dialer.DialtactsActivity",2.4),
            ("com.samsung.android.messaging","com.samsung.android.messaging.ui.ConversationListActivity",2.2),("com.sec.android.gallery3d","com.sec.android.gallery3d.app.Gallery",2.1),
            ("com.sec.android.app.camera","com.sec.android.app.camera.Camera",1.8),("com.android.settings","com.android.settings.Settings",1.8),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),("id.dana","id.dana.MainActivity",1.4),("com.gojek.app","com.gojek.app.SplashActivity",1.4),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),("com.tokopedia.tkpd","com.tokopedia.tkpd.activity.SplashScreenActivity",1.2),
            ("com.spotify.music","com.spotify.music.MainActivity",1.1),("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),
            ("com.samsung.android.calendar","com.samsung.android.calendar.LaunchActivity",0.8),("com.samsung.android.bixby.agent","com.samsung.android.bixby.agent.SplashActivity",0.7),
            ("com.samsung.android.spay","com.samsung.android.spay.SplashActivity",0.5),("com.samsung.android.themestore","com.samsung.android.themestore.SplashActivity",0.4),
            ("com.samsung.android.game.gamehome","com.samsung.android.game.gamehome.SplashActivity",0.3),("com.microsoft.teams","com.microsoft.teams.ui.SplashActivity",0.3),
            ("com.netflix.mediaclient","com.netflix.mediaclient.ui.launch.UIWebViewActivity",0.3),("com.binance.dev","com.binance.dev.SplashActivity",0.2),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "xiaomi": {
        "models": ["Xiaomi 24075RP89G","Xiaomi 23127PN0CC","Xiaomi 23053RN02A","Redmi Note 13","Xiaomi 24015RAI8I","POCO X6 Pro","Xiaomi 2312DRA50G","Xiaomi 2404ARN4CM","Xiaomi 23129RA5FL","Xiaomi 23124RA7EO","Xiaomi 24069RA21I","Xiaomi 24115RA8EI","Xiaomi 23116PN5BC","Xiaomi 2412DRA50I"],
        "av": ["11","12","13","14"], "ec": [25000, 110000], "cp": [0.58, 0.80],
        "system": XIAOMI_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.miui.home","com.miui.home.launcher.Launcher",12),("com.mi.android.globallauncher","com.mi.android.globallauncher.Launcher",7.2),
            ("android","android.app.Activity",5.8),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.8),("com.android.chrome","com.google.android.apps.chrome.Main",4.4),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.0),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.4),("com.google.android.youtube","com.google.android.youtube.HomeActivity",3.2),
            ("com.xiaomi.mipicks","com.xiaomi.mipicks.SplashActivity",2.6),("com.miui.securitycenter","com.miui.securitycenter.MainActivity",2.4),
            ("com.miui.gallery","com.miui.gallery.activity.HomePageActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.apps.photos","com.google.android.apps.photos.home.HomeActivity",1.8),("id.dana","id.dana.MainActivity",1.6),
            ("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),
            ("com.mobile.legends","com.mobile.legends.SplashActivity",1.3),("com.android.vending","com.android.vending.AssetBrowserActivity",1.2),
            ("com.miui.weather2","com.miui.weather2.ActivityWeatherMain",1.0),("com.miui.notes","com.miui.notes.ui.NotesListActivity",0.8),
            ("com.xiaomi.scanner","com.xiaomi.scanner.SplashActivity",0.5),("com.xiaomi.shop","com.xiaomi.shop.SplashActivity",0.4),
            ("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",0.3),("com.facebook.lite","com.facebook.lite.MainActivity",0.3),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.2),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "oppo": {
        "models": ["OPPO CPH2577","OPPO CPH2387","OPPO CPH2591","OPPO CPH2609","OPPO CPH2589","OPPO CPH2565","OPPO CPH2481","OPPO CPH2531","OPPO CPH2613","OPPO CPH2645","OPPO CPH2495","OPPO CPH2553","OPPO CPH2669","OPPO CPH2683"],
        "av": ["11","12","13","14"], "ec": [20000, 85000], "cp": [0.60, 0.84],
        "system": OPPO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",16.5),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",10),("com.oppo.launcher","com.oppo.launcher.Launcher",14),
            ("android","android.app.Activity",6.0),("com.facebook.lite","com.facebook.lite.MainActivity",5.5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.5),
            ("com.android.chrome","com.google.android.apps.chrome.Main",4.0),("com.coloros.recents","com.coloros.recents.RecentsActivity",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.4),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3.0),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.6),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.4),
            ("com.android.settings","com.android.settings.Settings",2.2),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.9),
            ("id.dana","id.dana.MainActivity",1.6),("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),
            ("com.spotify.music","com.spotify.music.MainActivity",1.2),("com.android.vending","com.android.vending.AssetBrowserActivity",1.2),
            ("com.oppo.camera","com.oppo.camera.CameraActivity",1.0),("com.coloros.gallery3d","com.coloros.gallery3d.app.Gallery",0.8),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.3),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "infinix": {
        "models": ["Infinix X6833B","Infinix X669C","Infinix X6728B","Infinix X6886","Infinix X6725B","Infinix X6720","Infinix X6850","Infinix X6851","Infinix X6838","Infinix X6835B","Infinix X6962"],
        "av": ["12","13","14"], "ec": [25000, 70000], "cp": [0.62, 0.83],
        "system": INFINIX_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.transsion.hilauncher","com.transsion.hilauncher.Launcher",13),("android","android.app.Activity",5.5),
            ("tw.nekomimi.nekogram","tw.nekomimi.nekogram.SplashActivity",6),("com.android.chrome","com.google.android.apps.chrome.Main",4.5),
            ("com.instagram.android","com.instagram.android.MainTabActivity",4.0),("com.twitter.android","com.twitter.android.MainActivity",3.5),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3.2),("com.authy.authy","com.authy.authy.SplashActivity",3.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",2.8),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",2.5),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.transsion.XOS.gallery3d","com.transsion.XOS.gallery3d.GalleryActivity",1.8),("com.transsion.XOS.music","com.transsion.XOS.music.MusicActivity",1.5),
            ("id.dana","id.dana.MainActivity",1.6),("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",1.4),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.2),("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),
            ("com.binance.dev","com.binance.dev.SplashActivity",1.0),("com.google.android.youtube","com.google.android.youtube.HomeActivity",1.0),
        ],
    },
    "vivo": {
        "models": ["vivo V2322","vivo V2227","vivo V2058","vivo V2348","vivo V2351","vivo V2239","vivo V2304","vivo V2318","vivo V2354","vivo V2358","vivo V2405","vivo V2327","vivo V2339","vivo V2350","vivo V2352","vivo V2416","vivo V2422"],
        "av": ["12","13","14","15"], "ec": [25000, 90000], "cp": [0.60, 0.82],
        "system": VIVO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.vivo.launcher","com.vivo.launcher.Launcher",12),("android","android.app.Activity",4.5),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",5),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",3.5),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3.2),("com.android.chrome","com.google.android.apps.chrome.Main",3.0),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",2.8),("com.instagram.android","com.instagram.android.MainTabActivity",2.5),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.vivo.camera","com.vivo.camera.CameraActivity",1.8),("com.vivo.gallery","com.vivo.gallery.GalleryActivity",1.5),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),
            ("id.dana","id.dana.MainActivity",1.4),("com.gojek.app","com.gojek.app.SplashActivity",1.3),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.2),
            ("com.vivo.appstore","com.vivo.appstore.MainActivity",1.0),("com.binance.dev","com.binance.dev.SplashActivity",1.0),
            ("com.spotify.music","com.spotify.music.MainActivity",0.8),("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.5),
        ],
    },
    "realme": {
        "models": ["realme RMX5388","realme RMX3771","realme RMX3700","realme RMX3870","realme RMX3840","realme RMX3868","realme RMX3939","realme RMX3987","realme RMX3615","realme RMX3765","realme RMX3913","realme RMX3800","realme RMX5000"],
        "av": ["10","11","12","13","14","15"], "ec": [20000, 95000], "cp": [0.60, 0.83],
        "system": OPPO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.oppo.launcher","com.oppo.launcher.Launcher",12),("android","android.app.Activity",5.5),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.0),("com.instagram.android","com.instagram.android.MainTabActivity",3.5),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",3.0),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",2.8),("com.android.chrome","com.google.android.apps.chrome.Main",2.5),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.8),("id.dana","id.dana.MainActivity",1.5),
            ("com.gojek.app","com.gojek.app.SplashActivity",1.4),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),
            ("com.oppo.camera","com.oppo.camera.CameraActivity",1.0),("com.coloros.gallery3d","com.coloros.gallery3d.app.Gallery",0.8),
            ("com.spotify.music","com.spotify.music.MainActivity",0.8),("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.4),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),
        ],
    },
    "advan": {
        "models": ["Advan Tab VX","Advan G9 Pro Max","Advan G5","Advan Nasa Plus","Advan Sketsa 2","Advan Nasa Pro"],
        "av": ["11","12","13"], "ec": [15000,60000], "cp": [0.56,0.78],
        "system": ADVAN_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.advan.launcher","com.advan.launcher.Launcher",11),("android","android.app.Activity",6),
            ("com.android.chrome","com.google.android.apps.chrome.Main",5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.2),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.6),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.8),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.4),
            ("com.android.settings","com.android.settings.Settings",2.2),("id.dana","id.dana.MainActivity",1.8),("com.gojek.app","com.gojek.app.SplashActivity",1.6),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.2),
            ("com.advan.gallery","com.advan.gallery.GalleryActivity",1.1),("com.advan.camera","com.advan.camera.CameraActivity",1.0),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),("com.spotify.music","com.spotify.music.MainActivity",1),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",1),
        ],
    },
    "tecno": {
        "models": ["TECNO TECNO AD8","TECNO SPARK 10","TECNO SPARK 20","TECNO TECNO KG7","TECNO BG7","TECNO CK9n","TECNO CH9","TECNO CL8","TECNO AE10","TECNO LI9","TECNO AM8","TECNO BJ8"],
        "av": ["12","13","14","15"], "ec": [20000,75000], "cp": [0.60,0.82],
        "system": INFINIX_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.transsion.hilauncher","com.transsion.hilauncher.Launcher",13),("android","android.app.Activity",5.5),
            ("com.kubi.kucoin","com.kubi.kucoin.SplashActivity",5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.5),
            ("com.transsion.microintelligence","com.transsion.microintelligence.SplashActivity",3),("com.android.chrome","com.google.android.apps.chrome.Main",2.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",2.5),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.2),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",2),("com.android.settings","com.android.settings.Settings",1.8),
            ("com.transsion.XOS.gallery3d","com.transsion.XOS.gallery3d.GalleryActivity",1.6),("com.transsion.XOS.music","com.transsion.XOS.music.MusicActivity",1.4),
            ("id.dana","id.dana.MainActivity",1.5),("com.gojek.app","com.gojek.app.SplashActivity",1.4),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),
            ("com.binance.dev","com.binance.dev.SplashActivity",1.2),("com.google.android.youtube","com.google.android.youtube.HomeActivity",1),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),("com.facebook.lite","com.facebook.lite.MainActivity",0.5),
        ],
    },
    "asus": {
        "models": ["ASUS_AI2401","ASUS_AI2501","ASUS_A2302"],
        "av": ["13","14","15"], "ec": [20000, 70000], "cp": [0.60, 0.82],
        "system": ASUS_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.asus.launcher","com.asus.launcher.Launcher",12),("android","android.app.Activity",5.0),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.0),
            ("com.android.chrome","com.google.android.apps.chrome.Main",3.8),("com.instagram.android","com.instagram.android.MainTabActivity",3.5),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.0),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.8),
            ("com.asus.zenui","com.asus.zenui.HomeActivity",2.5),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.8),("com.facebook.katana","com.facebook.katana.LoginActivity",1.5),
            ("com.spotify.music","com.spotify.music.MainActivity",1.2),("com.android.vending","com.android.vending.AssetBrowserActivity",1.0),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.5),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),
        ],
    },
    "google": {
        "models": ["Pixel 8","Pixel 8 Pro","Pixel 8a","Pixel 9","Pixel 9 Pro","Pixel 9a","Pixel 7a"],
        "av": ["13","14","15"], "ec": [15000, 60000], "cp": [0.65, 0.85],
        "system": GOOGLE_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.google.android.apps.nexuslauncher","com.google.android.apps.nexuslauncher.NexusLauncherActivity",14),
            ("android","android.app.Activity",5.5),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",5.0),
            ("com.google.android.GoogleCamera","com.google.android.camera.CameraActivity",4.0),("com.android.chrome","com.google.android.apps.chrome.Main",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.2),("com.google.android.youtube","com.google.android.youtube.HomeActivity",3.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",2.8),("com.google.android.apps.photos","com.google.android.apps.photos.home.HomeActivity",2.5),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",2.0),("com.google.android.apps.maps","com.google.android.maps.MapsActivity",1.8),
            ("com.android.settings","com.android.settings.Settings",1.5),("com.google.android.apps.docs","com.google.android.apps.docs.drive.startup.StartupActivity",1.2),
            ("com.spotify.music","com.spotify.music.MainActivity",1.0),("com.android.vending","com.android.vending.AssetBrowserActivity",1.0),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.5),("com.binance.dev","com.binance.dev.SplashActivity",0.3),
        ],
    },
    "oneplus": {
        "models": ["OnePlus CPH2609","OnePlus CPH2611","OnePlus CPH2649","OnePlus CPH2703","OnePlus CPH2725"],
        "av": ["13","14","15"], "ec": [20000, 75000], "cp": [0.62, 0.84],
        "system": ONEPLUS_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",19),("com.oneplus.launcher","com.oneplus.launcher.Launcher",13),("android","android.app.Activity",5.0),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.2),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.0),
            ("com.android.chrome","com.google.android.apps.chrome.Main",3.8),("com.instagram.android","com.instagram.android.MainTabActivity",3.5),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.0),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.5),
            ("com.oneplus.security","com.oneplus.security.MainActivity",2.0),("com.android.settings","com.android.settings.Settings",1.8),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),("com.spotify.music","com.spotify.music.MainActivity",1.2),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",1.0),("com.facebook.katana","com.facebook.katana.LoginActivity",0.8),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.5),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),
        ],
    },
    "motorola": {
        "models": ["Motorola XT2431-1","Motorola XT2433-1","Motorola XT2409-1","Motorola XT2427-1","Motorola XT2439-1"],
        "av": ["13","14","15"], "ec": [18000, 65000], "cp": [0.60, 0.82],
        "system": MOTOROLA_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.motorola.launcher3","com.motorola.launcher3.Launcher",12),("android","android.app.Activity",5.5),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.5),("com.android.chrome","com.google.android.apps.chrome.Main",4.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3.5),("com.instagram.android","com.instagram.android.MainTabActivity",3.2),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.8),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.5),
            ("com.motorola.moto","com.motorola.moto.MainActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),("com.spotify.music","com.spotify.music.MainActivity",1.0),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",1.0),("com.facebook.katana","com.facebook.katana.LoginActivity",0.8),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),("com.binance.dev","com.binance.dev.SplashActivity",0.2),
        ],
    },
    "poco": {
        "models": ["POCO F6","POCO X7 Pro","POCO M6 Pro","POCO C75","POCO F7"],
        "av": ["13","14","15"], "ec": [25000, 90000], "cp": [0.60, 0.83],
        "system": POCO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.mi.launcher","com.mi.launcher.Launcher",13),("com.miui.home","com.miui.home.launcher.Launcher",7),
            ("android","android.app.Activity",5.5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.5),
            ("com.android.chrome","com.google.android.apps.chrome.Main",4.0),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.2),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.0),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.8),("com.xiaomi.mipicks","com.xiaomi.mipicks.SplashActivity",2.2),
            ("com.miui.securitycenter","com.miui.securitycenter.MainActivity",2.0),("com.android.settings","com.android.settings.Settings",1.8),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),("com.mobile.legends","com.mobile.legends.SplashActivity",1.3),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",1.0),("com.spotify.music","com.spotify.music.MainActivity",0.8),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.4),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),
        ],
    },
}


# ══════════════════════════════════════════
#  GENERATOR ENGINE
# ══════════════════════════════════════════

def _norm_apps(items):
    """Normalize app list to (package, class, weight) tuples."""
    if items and len(items[0]) == 2:
        s = sum(w for _, w in items)
        return [(p, "", w / s) for p, w in items]
    s = sum(w for _, _, w in items)
    return [(p, c, w / s) for p, c, w in items]


def _build_pool(brand, prof, rng, persona_name=None):
    """Build realistic package pool — each device has a unique user persona."""
    apps = _norm_apps(prof["apps"])
    brand_sys = prof.get("system", [])

    # ═══ USER PERSONA SYSTEM ═══
    # Each device gets a random persona that determines which apps are installed.
    # This prevents 63%+ package overlap between generated files.
    personas = {
        "student":     {"social": 0.95, "messaging": 0.9, "games": 0.85, "ecommerce": 0.75, "finance": 0.4, "productivity": 0.35, "news": 0.25, "crypto": 0.2, "travel": 0.2},
        "professional": {"social": 0.55, "messaging": 0.85, "games": 0.2, "ecommerce": 0.6, "finance": 0.75, "productivity": 0.9, "news": 0.7, "crypto": 0.3, "travel": 0.55},
        "elderly":     {"social": 0.4, "messaging": 0.75, "games": 0.15, "ecommerce": 0.35, "finance": 0.5, "productivity": 0.15, "news": 0.4, "crypto": 0.05, "travel": 0.1},
        "gamer":       {"social": 0.6, "messaging": 0.7, "games": 0.95, "ecommerce": 0.5, "finance": 0.3, "productivity": 0.2, "news": 0.2, "crypto": 0.4, "travel": 0.1},
        "casual":      {"social": 0.7, "messaging": 0.8, "games": 0.4, "ecommerce": 0.6, "finance": 0.5, "productivity": 0.3, "news": 0.3, "crypto": 0.15, "travel": 0.3},
        "influencer":  {"social": 0.95, "messaging": 0.8, "games": 0.15, "ecommerce": 0.7, "finance": 0.3, "productivity": 0.4, "news": 0.2, "crypto": 0.15, "travel": 0.4},
        "trader":      {"social": 0.4, "messaging": 0.65, "games": 0.15, "ecommerce": 0.4, "finance": 0.85, "productivity": 0.6, "news": 0.75, "crypto": 0.95, "travel": 0.2},
        "homemaker":   {"social": 0.6, "messaging": 0.85, "games": 0.5, "ecommerce": 0.9, "finance": 0.6, "productivity": 0.2, "news": 0.25, "crypto": 0.05, "travel": 0.2},
    }
    if persona_name and persona_name in personas:
        persona = personas[persona_name]
    else:
        persona_name = rng.choice(list(personas.keys()))
        persona = personas[persona_name]

    # App category mapping (package → category)
    _cat_map = {
        "com.instagram.android": "social", "com.facebook.katana": "social", "com.facebook.lite": "social",
        "com.ss.android.ugc.trill": "social", "com.zhiliaoapp.musically.go": "social",
        "com.twitter.android": "social", "com.pinterest": "social", "com.linkedin.android": "social",
        "com.reddit.frontpage": "social", "com.quora.android": "social", "com.snapchat.android": "social",
        "com.kwai.video": "social",
        "com.whatsapp": "messaging", "com.whatsapp.w4b": "messaging", "org.telegram.messenger": "messaging",
        "com.facebook.orca": "messaging", "com.discord": "messaging", "com.viber.voip": "messaging",
        "com.skype.raider": "messaging", "us.zoom.videomeetings": "messaging",
        "com.mobile.legends": "games", "com.garena.game.codm": "games", "com.supercell.clashofclans": "games",
        "com.pubg.mobile": "games", "com.dts.freefiremax": "games", "com.pou.app": "games",
        "com.king.candycrushsaga": "games",
        "com.shopee.id": "ecommerce", "com.tokopedia.tkpd": "ecommerce", "com.bukalapak.android": "ecommerce",
        "com.lazada.android": "ecommerce", "com.ebay.mobile": "ecommerce",
        "com.amazon.mShop.android.shopping": "ecommerce", "com.aliexpress": "ecommerce",
        "id.dana": "finance", "id.co.bca": "finance", "id.co.bni": "finance", "id.co.bri": "finance",
        "id.co.bankbkemobile.digitalbank": "finance", "com.telkom.mwallet": "finance",
        "com.binance.dev": "crypto", "com.coinbase.android": "crypto", "com.okx.wallet": "crypto",
        "com.microsoft.teams": "productivity", "com.microsoft.office.outlook": "productivity",
        "com.google.android.apps.docs": "productivity", "cn.wps.moffice_eng": "productivity",
        "com.adobe.reader": "productivity", "com.canva.editor": "productivity",
        "com.google.android.apps.maps": "productivity",
        "com.nytimes.android": "news", "com.bbc.news": "news", "com.detik.android": "news",
        "id.co.kompas": "news", "com.medium.reader": "news", "com.imdb.mobile": "news",
        "com.ubercab": "travel", "com.airbnb.android": "travel", "com.booking": "travel",
        "com.traveloka.android": "travel", "com.gojek.app": "travel", "com.grab.id": "travel",
        "com.spotify.music": "social", "com.netflix.mediaclient": "social",
        "com.google.android.apps.youtube.music": "social", "com.joox": "social",
        "com.deezer.android.app": "social", "tv.twitch.android.app": "social",
        "com.openai.chatgpt": "productivity", "com.anthropic.claude": "productivity",
        "com.picsart.studio": "social", "com.shazam.android": "social",
        "com.duolingo": "productivity", "org.mozilla.firefox": "productivity",
        "com.opera.browser": "productivity", "com.android.chrome": "productivity",
    }

    # Filter COMMON_USER_APPS by persona
    extra_raw = []
    for item in COMMON_USER_APPS:
        pkg = item[0]
        weight = item[-1]
        cat = _cat_map.get(pkg, "casual")
        # If category not in persona map, use 0.4 as default inclusion rate
        rate = persona.get(cat, 0.35)  # Higher default = more apps pass through
        if rng.random() < rate:
            extra_raw.append((pkg, weight))
    extra = _norm_apps(extra_raw)

    # Brand apps: include 70-95% (real devices have more brand bloatware)
    brand_apps = [(p, c, w) for p, c, w in apps if rng.random() < rng.uniform(0.80, 0.98)]

    # SYSTEM_APPS: include 45-75% (real devices have more system packages)
    sys_pick = [p for p in SYSTEM_APPS + brand_sys if rng.random() < rng.uniform(0.70, 0.92)]
    # BG_SERVICES: include 25-55% (real devices have more background services)
    bg_pick = [p for p in BG_SERVICES if rng.random() < rng.uniform(0.50, 0.75)]

    # Combine brand + extra (reduced weight)
    all_apps = list(brand_apps)
    for p, _, w in extra:
        all_apps.append((p, "", w * 0.15))

    total_w = sum(w for _, _, w in all_apps)
    if total_w > 0:
        all_apps = [(p, c, w / total_w) for p, c, w in all_apps]
    return all_apps, sys_pick, bg_pick


def _gen(brand, model, av, count, seed, days, persona=None):
    rng = random.Random(seed)
    prof = BP[brand]
    model = model or rng.choice(prof["models"])
    av = av or rng.choice(prof["av"])
    if count is None:
        lo, hi = prof["ec"]
        count = rng.randint(lo, hi)
    count = min(count, 120000)
    if days is None:
        days = rng.uniform(7.1, 9.8)

    # Time window
    end = dt.datetime(2026, 5, 28, rng.randint(5, 20), rng.randint(0, 59), rng.randint(0, 59), tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days, minutes=rng.randint(0, 180), seconds=rng.randint(0, 59))

    # Build package pool
    apps, sys_pkgs, bg_pkgs = _build_pool(brand, prof, rng, persona)
    pkgs = [p for p, _, _ in apps]
    cls = {p: c for p, c, _ in apps}
    pw = [w for _, _, w in apps]

    # FIX 5: Primary app system — 1-2 apps dominate 25-40% of events (like real devices)
    # Pick 1-2 "primary apps" (WhatsApp, launcher, or top social) and boost their weight heavily
    primary_candidates = [p for p in pkgs if p in (
        "com.whatsapp", "com.whatsapp.w4b", "com.sec.android.app.launcher",
        "com.android.launcher3", "com.transsion.hilauncher", "com.oppo.launcher",
        "com.mi.android.globallauncher", "com.instagram.android",
        "com.facebook.katana", "com.ss.android.ugc.trill",
    )]
    if primary_candidates:
        primary = rng.choice(primary_candidates)
        primary_idx = pkgs.index(primary)
        pw[primary_idx] = pw[primary_idx] * rng.uniform(2, 3.5)  # Boost to dominate (capped for realism)
        # Re-normalize
        pw_sum = sum(pw)
        pw = [w / pw_sum for w in pw]

    ct = rng.uniform(*prof["cp"])
    tn = [t for t, _ in EW]
    tw = [w * rng.uniform(0.82, 1.18) for _, w in EW]

    # Hour weights with randomness
    bh = [w * rng.uniform(0.85, 1.15) for w in BH_INDONESIA]
    bh_sum = sum(bh)
    bh = [w / bh_sum for w in bh]

    # Day allocation
    ds = []
    d = start.date()
    while d <= end.date():
        ds.append(d)
        d += dt.timedelta(days=1)

    ws = []
    for day in ds:
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
        ws.append(w)

    s = sum(ws)
    dc = {d: int(round(count * w / s)) for d, w in zip(ds, ws)}
    while sum(dc.values()) < count:
        dc[rng.choice(ds)] += 1
    while sum(dc.values()) > count:
        k = rng.choice([d for d in ds if dc[d] > 20])
        dc[k] -= 1

    rows = []

    for day, nd in sorted(dc.items()):
        hw = [max(0.0004, w * rng.uniform(0.7, 1.35)) for w in bh]
        if day.weekday() in (5, 6):
            for h in range(10, 23):
                hw[h] *= rng.uniform(1.02, 1.32)
        hs = sum(hw)
        hw = [x / hs for x in hw]

        # Session-based generation: each session = one package, multiple events
        # Session size distribution: fat-tailed (most are small, some are huge)
        day_events = 0
        while day_events < int(nd * 0.95):
            # Pick a random hour weighted by distribution
            hr = rng.choices(range(24), weights=hw, k=1)[0]

            # Session size: fat-tailed distribution
            r = rng.random()
            if r < 0.60:
                session_size = rng.randint(1, 8)
            elif r < 0.85:
                session_size = rng.randint(8, 40)
            elif r < 0.95:
                session_size = rng.randint(40, 150)
            elif r < 0.99:
                session_size = rng.randint(150, 300)
            else:
                session_size = rng.randint(300, 450)

            session_size = min(session_size, nd - day_events)
            if session_size <= 0:
                break

            # Pick session package
            sp = rng.choices(pkgs, weights=pw, k=1)[0]
            # Sometimes use system/bg package for the session
            if rng.random() < 0.15 and sys_pkgs:
                sp = rng.choice(sys_pkgs)
            elif rng.random() < 0.05 and bg_pkgs:
                sp = rng.choice(bg_pkgs)

            # Session start time
            cur = dt.datetime(day.year, day.month, day.day, hr,
                              rng.randrange(60), rng.randrange(60),
                              rng.randrange(1000) * 1000, tzinfo=dt.timezone.utc)
            if cur < start:
                cur = start + dt.timedelta(seconds=rng.randint(0, 2400))
            if cur > end:
                cur = end - dt.timedelta(seconds=rng.randint(0, 2400))

            # Generate events in this session
            for i in range(session_size):
                if i:
                    # Inter-event gap (mostly small for bursts)
                    r = rng.random()
                    if r < 0.22:
                        delta = 0  # concurrent event (same timestamp)
                    elif r < 0.50:
                        delta = rng.uniform(0.02, 0.8)
                    elif r < 0.72:
                        delta = rng.uniform(1, 10)
                    elif r < 0.88:
                        delta = rng.uniform(10, 60)
                    elif r < 0.96:
                        delta = rng.uniform(60, 600)
                    else:
                        delta = rng.uniform(600, 2400)
                    cur += dt.timedelta(seconds=delta, milliseconds=rng.randint(0, 25))

                if not (start <= cur <= end):
                    continue

                # Package: mostly session package, sometimes switch
                pp = sp
                if rng.random() < 0.20:
                    # Switch to a different package temporarily
                    pp = rng.choices(pkgs, weights=pw, k=1)[0]
                elif rng.random() < 0.05 and sys_pkgs:
                    pp = rng.choice(sys_pkgs)
                elif rng.random() < 0.02 and bg_pkgs:
                    pp = rng.choice(bg_pkgs)
                # Hard cap: force switch if same package streak > 160
                if rows and pp == rows[-1]["package"]:
                    same_streak = 1
                    for prev in reversed(rows):
                        if prev["package"] == pp:
                            same_streak += 1
                        else:
                            break
                    if same_streak >= 160:
                        pp = rng.choices(pkgs, weights=pw, k=1)[0]

                # Event type
                if i == 0 and rng.random() < 0.7:
                    typ = "ACTIVITY_RESUMED"
                elif i == session_size - 1 and rng.random() < 0.63:
                    typ = "ACTIVITY_PAUSED"
                else:
                    typ = rng.choices(tn, weights=tw, k=1)[0]

                rec = {"ts": int(cur.timestamp() * 1000) + rng.randint(0, 12), "package": pp, "type": typ}

                # Class field
                c = cls.get(pp, "")
                if c:
                    if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION", "CONFIGURATION_CHANGE"):
                        h = rng.random() < min(0.96, ct + 0.22)
                    elif typ.startswith("FOREGROUND_SERVICE"):
                        h = rng.random() < max(0.25, ct - 0.3)
                    elif typ.startswith("SCREEN") or typ.startswith("KEYGUARD") or typ == "STANDBY_BUCKET_CHANGED":
                        h = rng.random() < max(0.04, ct - 0.58)
                    else:
                        h = rng.random() < max(0.08, ct - 0.48)
                    if h:
                        rec["class"] = c
                elif rng.random() < 0.40 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION"):
                    rec["class"] = pp + ".MainActivity"

                rows.append(rec)

            day_events += session_size

    rows.sort(key=lambda r: r["ts"])

    # Post-process: inject mega-bursts, long streaks, extra unique packages
    rows = _post_process(rows, start, end, pkgs, pw, sys_pkgs, bg_pkgs, cls, tn, tw, ct, rng, count)
    rows.sort(key=lambda r: r["ts"])

    # Trim to count — preserve post-processing bursts by trimming from padding events first
    if len(rows) > count:
        # Sort by timestamp, remove events from the end (padding) first
        rows.sort(key=lambda r: r["ts"])
        rows = rows[:count]
    while len(rows) < count:
        cur = start + dt.timedelta(seconds=rng.randint(0, max(1, int((end - start).total_seconds()))),
                                   milliseconds=rng.randint(0, 999))
        pp = rng.choices(pkgs, weights=pw, k=1)[0]
        typ = rng.choices(tn, weights=tw, k=1)[0]
        rec = {"ts": int(cur.timestamp() * 1000), "package": pp, "type": typ}
        if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23") and rng.random() < 0.86 and cls.get(pp):
            rec["class"] = cls[pp]
        elif rng.random() < 0.40 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23"):
            rec["class"] = pp + ".MainActivity"
        rows.append(rec)

    rows.sort(key=lambda r: r["ts"])

    # Cap same-package streaks at 160 — break long runs with package switches
    MAX_STREAK = 160
    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows) and rows[j]["package"] == rows[i]["package"]:
            j += 1
        run_len = j - i
        if run_len > MAX_STREAK:
            # Break every MAX_STREAK events by switching package
            for k in range(i + MAX_STREAK, j, MAX_STREAK):
                alt = rng.choices(pkgs, weights=pw, k=1)[0]
                if alt == rows[k]["package"]:
                    for p in (sys_pkgs + bg_pkgs + pkgs):
                        if p != rows[k]["package"]:
                            alt = p
                            break
                rows[k]["package"] = alt
        i = j
    rows.sort(key=lambda r: r["ts"])

    mn = dt.datetime.fromtimestamp(rows[0]["ts"] / 1000, dt.timezone.utc)
    mx = dt.datetime.fromtimestamp(rows[-1]["ts"] / 1000, dt.timezone.utc)
    iso = lambda t: t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "schema_version": 1, "app_version": "1.0.0",
        "android_version": av, "device_model": model,
        "export_generated_at": iso(mx),
        "window_start": iso(mn), "window_end": iso(mx),
        "event_count": len(rows),
        "notes": "Event-level data subject to Android system retention; older periods may be summarised only."
    }
    return rows, manifest



def _post_process(rows, start, end, pkgs, pw, sys_pkgs, bg_pkgs, cls, tn, tw, ct, rng, count):
    """Inject mega-bursts, long streaks, and extra unique packages."""
    
    # 1. Inject 2-4 mega-bursts (400-600 events, same package, <1s gaps)
    for _ in range(2):
        burst_size = rng.randint(410, 520)
        # Pick a random time in the window
        base_ts = start.timestamp() + rng.random() * (end.timestamp() - start.timestamp())
        burst_pkg = rng.choices(pkgs, weights=pw, k=1)[0]
        # Use 2-3 packages in mega-burst to keep burst max high but same-pkg max low
        burst_pkgs = [burst_pkg]
        if rng.random() < 0.7:
            burst_pkgs.append(rng.choices(pkgs, weights=pw, k=1)[0])
        if rng.random() < 0.3:
            burst_pkgs.append(rng.choices(pkgs, weights=pw, k=1)[0])
        
        cur_ts = base_ts
        for i in range(burst_size):
            if i:
                cur_ts += rng.uniform(0.02, 0.95)  # <1s gap
            
            cur_dt = dt.datetime.fromtimestamp(cur_ts, dt.timezone.utc)
            if not (start <= cur_dt <= end):
                continue
            
            typ = rng.choices(tn, weights=tw, k=1)[0]
            if i == 0:
                typ = "ACTIVITY_RESUMED"
            elif i == burst_size - 1:
                typ = "ACTIVITY_PAUSED"
            
            rec = {"ts": int(cur_ts * 1000) + rng.randint(0, 12), "package": rng.choice(burst_pkgs), "type": typ}
            c = cls.get(rec["package"], "")
            if c and rng.random() < 0.80:
                rec["class"] = c
            rows.append(rec)
    
    # 2. Inject 5-10 long same-package streaks (80-155 events)
    prev_streak_pkg = ""
    for _ in range(4):
        streak_size = rng.randint(85, 135)
        base_ts = start.timestamp() + rng.random() * (end.timestamp() - start.timestamp())
        streak_pkg = rng.choices(pkgs[:8], weights=pw[:8], k=1)[0]  # top 8 packages
        # Ensure different package from previous streaks
        if streak_pkg == prev_streak_pkg:
            streak_pkg = rng.choices(pkgs[2:8], weights=pw[2:8], k=1)[0]
        prev_streak_pkg = streak_pkg
        
        cur_ts = base_ts
        for i in range(streak_size):
            if i:
                # Mix of small and medium gaps
                r = rng.random()
                if r < 0.70:
                    cur_ts += rng.uniform(0.5, 5.0)
                elif r < 0.90:
                    cur_ts += rng.uniform(5, 30)
                else:
                    cur_ts += rng.uniform(30, 120)
            
            cur_dt = dt.datetime.fromtimestamp(cur_ts, dt.timezone.utc)
            if not (start <= cur_dt <= end):
                continue
            
            typ = rng.choices(tn, weights=tw, k=1)[0]
            rec = {"ts": int(cur_ts * 1000) + rng.randint(0, 12), "package": streak_pkg, "type": typ}
            c = cls.get(streak_pkg, "")
            if c and rng.random() < 0.80:
                rec["class"] = c
            rows.append(rec)
    
    # 3. Inject extra unique package events to boost unique count
    # Add events for system/bg packages that aren't yet in the dataset
    existing_pkgs = set(r["package"] for r in rows)
    missing_sys = [p for p in sys_pkgs if p not in existing_pkgs]
    missing_bg = [p for p in bg_pkgs if p not in existing_pkgs]
    
    # Inject ALL missing packages — spread across timeline to survive trimming
    extra_pkgs = missing_sys + missing_bg
    rng.shuffle(extra_pkgs)
    total_span = (end - start).total_seconds()
    for idx, pkg in enumerate(extra_pkgs):
        # Spread evenly across timeline + small random offset
        frac = (idx + 0.5) / max(len(extra_pkgs), 1)
        base_ts = start.timestamp() + frac * total_span + rng.uniform(-1800, 1800)
        cur_dt = dt.datetime.fromtimestamp(base_ts, dt.timezone.utc)
        if not (start <= cur_dt <= end):
            base_ts = start.timestamp() + rng.random() * total_span
        typ = rng.choices(tn, weights=tw, k=1)[0]
        rec = {"ts": int(base_ts * 1000) + rng.randint(0, 12), "package": pkg, "type": typ}
        if rng.random() < 0.35 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23"):
            rec["class"] = pkg + ".MainActivity"
        rows.append(rec)
    
    # 4. Inject concurrent events (same timestamp) — real devices have 2-5% gap=0
    # Pick random existing events and add "shadow" events with identical timestamps
    existing_ts = [(i, r['ts']) for i, r in enumerate(rows)]
    rng.shuffle(existing_ts)
    num_concurrent = int(len(rows) * rng.uniform(0.025, 0.04))  # 2.5-4% of events
    for idx, ts in existing_ts[:num_concurrent]:
        pkg = rng.choices(pkgs[:15], weights=pw[:15], k=1)[0]
        typ = rng.choices(tn, weights=tw, k=1)[0]
        rec = {"ts": ts, "package": pkg, "type": typ}
        c = cls.get(pkg, "")
        if c and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION"):
            if rng.random() < 0.75:
                rec["class"] = c
        rows.append(rec)
    
    return rows


def _analyze(rows):
    pkg = collections.Counter(r["package"] for r in rows)
    typ = collections.Counter(r["type"] for r in rows)
    gaps = [(b["ts"] - a["ts"]) / 1000 for a, b in zip(rows, rows[1:])]
    cp = sum(1 for r in rows if "class" in r) / len(rows) * 100 if rows else 0

    def q(vs, n):
        if not vs:
            return 0
        vs = sorted(vs)
        return vs[min(len(vs) - 1, int((len(vs) - 1) * n))]

    def H(c):
        t = sum(c.values())
        return -sum((v / t) * math.log2(v / t) for v in c.values() if v and t) if t else 0

    return {
        "event_count": len(rows), "unique_packages": len(pkg),
        "package_entropy": round(H(pkg), 3), "event_type_entropy": round(H(typ), 3),
        "class_presence_pct": round(cp, 2),
        "gap_p50": round(q(gaps, 0.5), 3), "gap_p90": round(q(gaps, 0.9), 3),
        "gap_p99": round(q(gaps, 0.99), 3),
        "lte1": round(sum(g <= 1 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "gt10m": round(sum(g > 600 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "top_packages": pkg.most_common(30), "event_types": typ.most_common()
    }


def _score(m):
    s = 100
    if not (5000 <= m["event_count"] <= 120000):
        s -= 15
    if not (44 <= m["class_presence_pct"] <= 86):
        s -= 18
    if not (0.25 <= m["gap_p50"] <= 1.2):
        s -= 18
    if not (8 <= m["gap_p90"] <= 60):
        s -= 12
    if not (50 <= m["gap_p99"] <= 950):
        s -= 8
    if not (48 <= m["lte1"] <= 80):
        s -= 14
    if not (0.05 <= m["gt10m"] <= 3):
        s -= 8
    if not (2.5 <= m["package_entropy"] <= 6.8):
        s -= 6
    if not (1.2 <= m["event_type_entropy"] <= 3.8):
        s -= 6
    return max(0, s)


def _zip(rows, manifest):
    nd = "\n".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in rows) + "\n"
    ms = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("events.ndjson", nd)
        z.writestr("manifest.json", ms)
    d = buf.getvalue()
    return d, hashlib.sha256(d).hexdigest()


# ══════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)


@app.get("/api/profiles")
def profiles():
    return {b: {"models": p["models"], "android_versions": p["av"],
                 "event_count_range": p["ec"]}
            for b, p in BP.items()}


@app.post("/api/generate")
def generate(brand: str = Form("xiaomi"), model: Optional[str] = Form(None),
             android: Optional[str] = Form(None), count: Optional[str] = Form(None),
             days: Optional[str] = Form(None), seed: Optional[str] = Form(None),
             persona: Optional[str] = Form(None)):
    brand = brand.lower().strip()
    if brand not in BP:
        raise HTTPException(400, "Unknown brand")

    def pi(v, lo, hi):
        if not v or not v.strip():
            return None
        n = int(v.strip())
        if not lo <= n <= hi:
            raise HTTPException(400, f"Must be {lo}-{hi}")
        return n

    def pf(v, lo, hi):
        if not v or not v.strip():
            return None
        n = float(v.strip())
        if not lo <= n <= hi:
            raise HTTPException(400, f"Must be {lo}-{hi}")
        return n

    try:
        rows, manifest = _gen(
            brand, (model or "").strip() or None, (android or "").strip() or None,
            pi(count, 1000, 120000), pi(seed, 0, 999999999), pf(days, 1, 14),
            (persona or "").strip() or None
        )
    except Exception as e:
        raise HTTPException(500, str(e))

    m = _analyze(rows)
    sc = _score(m)
    zb, sha = _zip(rows, manifest)
    return {
        "filename": "sw_events", "zip_size": len(zb), "zip_sha256": sha,
        "zip_base64": base64.b64encode(zb).decode(),
        "summary": {
            "device_model": manifest["device_model"],
            "android_version": manifest["android_version"],
            "event_count": manifest["event_count"],
            "window_start": manifest["window_start"],
            "window_end": manifest["window_end"],
            "score": sc, "sha256": sha, "zip_size": len(zb),
            "top_packages": m["top_packages"][:10],
            "event_types": m["event_types"][:10],
            "unique_packages": m["unique_packages"],
        },
        "notice": "Synthetic QA fixture only."
    }
