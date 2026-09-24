# Activity Log

**A tamper-evident activity journal with cryptographic proof of integrity.**

Every entry you log is chained to the one before it using SHA-256 hashing — the same principle behind blockchains. If anyone edits, deletes, or reorders a past entry, the chain breaks and you'll know exactly where.

No cloud required. No account needed. Open `index.html` and start logging.

---

## Why this exists

Most activity logs are just text files. Text files can be silently edited — by you, by a teammate, by anyone with access. There's no way to prove what was written, or when.

Activity Log solves this by making every entry **self-verifying**. Each log entry contains a cryptographic fingerprint that depends on every entry before it. The chain is either intact or it isn't — there's no in-between.

Useful for:
- **Freelancers** logging billable work with verifiable timestamps
- **Teams** keeping tamper-proof incident timelines
- **Developers** tracking what changed and when during a debug session
- **Anyone** who needs a lightweight, trustworthy activity record

---

## How it works

When you add an entry, the browser computes:

```
hash = SHA-256([ prevHash, id, timestamp, text ])
```

Each entry's hash depends on the entire history before it. Change anything in the past — even a single character — and every subsequent hash becomes invalid. The **Verify chain** button walks the entire log and reports the exact entry where integrity was broken.

The hash algorithm is byte-identical between the browser (Web Crypto API) and the Python backend (hashlib), so logs can be verified server-side too.

---

## Features

- **Hash chain integrity** — every entry cryptographically links to the previous one
- **One-click verification** — detects tampering and pinpoints the broken entry
- **Multiple projects** — separate logs, each with its own independent chain
- **Inline editing** — edit the last entry (rehashes correctly)
- **Download report** — export a plain-text report with all hashes for archiving
- **Real-time sync** — WebSocket push from the backend when agents submit events
- **Background agent** — auto-logs process starts/stops, window focus changes, and file modifications on your machine
- **Fully offline** — the frontend works as a standalone HTML file with no build step

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Plain HTML + Tailwind CDN + Web Crypto API |
| Backend | FastAPI · Python 3.12 · asyncpg · SQLAlchemy 2 |
| Queue | Redis Streams (XADD / XREADGROUP / XACK) |
| Database | PostgreSQL 16 |
| Agent | psutil · watchdog · pywin32 / python-xlib |
| Package manager | uv |
| Containers | Docker + Docker Compose |

---

## Quick start

### Frontend only (no backend needed)

Open `frontend/index.html` directly in any modern browser. Everything runs locally — hashing, storage, verification. No server, no install.

Or serve it with:

```bash
python -m http.server 5500 --directory frontend
# → http://localhost:5500
```

### Full stack with Docker

```bash
git clone https://github.com/your-username/activity-log
cd activity-log
cp .env.example .env        # review defaults — works out of the box
docker compose up -d
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5500 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

### Local development (without Docker)

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL, Redis

```bash
# Backend
cd backend
uv sync
cp ../.env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

```bash
# Worker (separate terminal)
cd backend
uv run python -m app.worker.main
```

```bash
# Agent (runs on your host machine — cannot run in Docker)
cd agent
uv sync
cp ../.env.example .env
uv run python -m agent.main
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health/` | Service health check |
| `POST` | `/devices/` | Register a device |
| `GET` | `/devices/` | List devices |
| `POST` | `/events/` | Submit a batch of events |
| `GET` | `/events/` | Query events with filters |
| `GET` | `/verify/{device_id}` | Verify hash chain for a device |
| `WS` | `/ws/events` | Live event stream |

Interactive docs available at `/docs` when the backend is running.

---

## Project structure

```
activity-log/
├── frontend/
│   └── index.html          # entire frontend — one file, no build step
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI routers (health, devices, events, verify, ws)
│   │   ├── core/           # config, logging
│   │   ├── db/             # SQLAlchemy engine + session
│   │   ├── models/         # ORM models (Device, Event)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # hash_chain, event_service, redis stream
│   │   └── worker/         # Redis Streams consumer
│   ├── alembic/            # database migrations
│   └── tests/
├── agent/
│   ├── agent/
│   │   ├── collectors/     # processes, active window, file changes
│   │   ├── platform/       # Windows / Linux window detection
│   │   ├── buffer.py       # thread-safe event buffer
│   │   ├── client.py       # HTTP client with retry
│   │   └── main.py         # entrypoint
│   └── tests/
├── docker-compose.yml
└── .env.example
```

---

## Running tests

```bash
cd backend
uv run pytest tests/ -v
```

```bash
cd agent
uv run pytest tests/ -v
```

---

## Contributing

Issues and pull requests are welcome. If you find a way to break the hash chain verification or produce a false-positive integrity check, please open an issue — that's the most valuable kind of feedback for this project.

---

## License

MIT
