# SW Events Web Generator

Website generator untuk membuat synthetic Android UsageStats fixture.

## Fitur

- Web UI responsive pakai Tailwind CDN
- Brand profile: Xiaomi, Samsung, OPPO, Infinix, Advan
- Generate synthetic `events.ndjson` + `manifest.json`
- Download hasil sebagai `sw_events.zip`
- Serverless-compatible untuk Vercel: output ZIP dibuat in-memory dan dikirim sebagai base64

## Local run

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

Buka: http://localhost:8000

## API

```bash
curl -X POST http://localhost:8000/api/generate \
  -F brand=xiaomi \
  -F count=1200 \
  -F days=1 \
  -F seed=42
```

Response mengandung:

- `filename`: selalu `sw_events`
- `zip_base64`: ZIP base64 untuk download browser
- `summary`: device, event_count, sha256, score, top packages/types

## ZIP output

Nama file download browser: `sw_events.zip`

Isi ZIP:

- `events.ndjson`
- `manifest.json`

## Deploy Vercel

```bash
vercel --prod
```

Synthetic QA fixture only — bukan data user asli.
