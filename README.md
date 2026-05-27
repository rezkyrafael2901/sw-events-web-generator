# SW Events Web Generator

Web UI untuk generate synthetic Android `sw_events.zip` fixture buat QA/staging parser test.

## Run lokal

```bash
cd /home/ubuntu/.hermes/cache/documents/sw_events_web_generator
python -m uvicorn app:app --host 0.0.0.0 --port 7860
```

Buka:

```text
http://SERVER_IP:7860
```

## Output

Setiap generate bikin folder baru di:

```text
outputs/<job_id>/
```

Isi:

- `sw_events_<model>_<seed>.zip`
- `sw_events_<model>_<seed>_report.json`
- `result.json`

## API

Generate:

```bash
curl -X POST http://127.0.0.1:7860/api/generate \
  -F brand=xiaomi \
  -F count=22000 \
  -F days=8.8 \
  -F seed=86421
```

Profiles:

```bash
curl http://127.0.0.1:7860/api/profiles
```

## Catatan

Output adalah synthetic QA fixture, bukan export asli user.
