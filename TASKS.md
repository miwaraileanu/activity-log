# Activity Log — Learning Roadmap

Work through these steps in order. Each step leaves the project in a runnable state.

## Frontend
The frontend is `frontend/index.html` — a single HTML file using Tailwind CDN and IBM Plex Sans.
Open it directly in a browser (no build step needed). It works fully offline using the Web Crypto API.
To serve it locally: `npx serve frontend` or `python -m http.server 5500 --directory frontend`.

---

## Step 1 — Agent prints events to the console

- [ ] Run `uv run python -m agent.main` from the `agent/` directory
- [ ] Verify process start/stop lines appear as you open/close apps
- [ ] Verify window title changes appear as you switch windows
- [ ] To watch files too: set `WATCHED_DIRS=["C:/some/folder"]` in `agent/.env`

**Done when:** the terminal prints `[process_start]`, `[process_stop]`, and `[window_focus]` events in real time without errors.

---

## Step 2 — FastAPI with /health and POST /events writing to Postgres

- [ ] Start Postgres locally (or via Docker: `docker run -e POSTGRES_USER=activitylog -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=activitylog -p 5432:5432 postgres:16-alpine`)
- [ ] Copy `.env.example` → `backend/.env` and adjust values
- [ ] Run `uv run uvicorn app.main:app --reload` from `backend/`
- [ ] Visit `http://localhost:8000/docs` — Swagger UI should load
- [ ] Test `GET /health` — should return `{"status":"ok","db":"ok","redis":"ok"}` (Redis will show error until Step 6)

**Done when:** `POST /events` with a JSON body returns 202 and the row appears in Postgres.

---

## Step 3 — Alembic migration for devices + events tables

- [ ] Fill in `backend/alembic/env.py` — it imports Base and settings (already done if agents ran)
- [ ] Run `uv run alembic revision --autogenerate -m "create devices and events"` from `backend/`
- [ ] Run `uv run alembic upgrade head`
- [ ] Confirm both tables exist in Postgres

**Done when:** `alembic upgrade head` creates both tables with no errors, and `alembic downgrade -1` drops them cleanly.

---

## Step 4 — Agent sends batches to the API

- [ ] With the backend running, start the agent: `uv run python -m agent.main` from `agent/`
- [ ] The agent will register the device and start sending events to POST /events
- [ ] Verify with `GET /events?device_id=<your-device-id>` in the Swagger UI

**Done when:** events from the agent show up via `GET /events` within one poll interval.

---

## Step 5 — Docker Compose for api + postgres

- [ ] Fill in `docker-compose.yml` (the TODO comments describe each service)
- [ ] Run `docker compose up --build`

**Done when:** `docker compose up` starts both services, `/health` returns `{"db":"ok"}`, and `POST /events` still persists rows.

---

## Step 6 — Redis Stream between API and worker

- [ ] Add Redis to `docker-compose.yml`
- [ ] Run `docker compose up` (now includes redis)
- [ ] Start the worker: `uv run python -m app.worker.main` from `backend/`
- [ ] POST /events now enqueues to Redis; the worker reads and writes to Postgres

**Done when:** `POST /events` returns 202 immediately, and rows appear in Postgres a moment later (written by the worker).

---

## Step 7 — Server-side hash chain + GET /verify

- [ ] Run `GET /verify/{device_id}` after the agent has sent some events
- [ ] Should return `{"valid": true, "count": N}`
- [ ] Manually UPDATE one row's text in Postgres, then verify again — should return `{"valid": false, "broken_at": ...}`
- [ ] Run `uv run pytest` from `backend/` — hash chain tests should pass

**Done when:** verify returns correct results both for valid and tampered chains.

---

## Step 8 — WebSocket live updates via Redis pub/sub

- [ ] Open browser console on `frontend/index.html`
- [ ] Run: `const ws = new WebSocket("ws://localhost:8000/ws/events"); ws.onmessage = e => console.log(JSON.parse(e.data))`
- [ ] Start the agent — events should stream into the browser console within seconds

**Done when:** submitting an event (via agent or curl) appears in the browser console within one second.

---

## Step 9 — Connect the HTML frontend to the API

- [ ] Open `frontend/index.html` in a text editor
- [ ] Replace the in-browser `addEntry()` with a call to `POST /events`
- [ ] Replace `onVerify()` with a call to `GET /verify/{device_id}`
- [ ] Open a WebSocket to `ws://localhost:8000/ws/events` on page load; append incoming events to the log list
- [ ] Replace `onDownload()` to fetch from `GET /events` and format the response

**Done when:** the HTML page works end-to-end with no in-browser hash computation; all data lives in Postgres.

---

## Step 10 — Tests for hash chain and events API

- [ ] Run `uv run pytest -v` from `backend/`
- [ ] All tests in `tests/test_hash_chain.py` and `tests/test_events_api.py` should pass
- [ ] Run `uv run pytest -v` from `agent/` — buffer tests should pass

**Done when:** all pytest suites pass with no warnings.

---

## API Contract

Every endpoint the frontend and agent will call.

### POST /devices
Register a device (idempotent — safe to call on every agent startup).

| Direction | Field | Type | Notes |
|-----------|-------|------|-------|
| Request   | name  | string | Human-readable hostname |
| Response  | id    | UUID string | Use this as device_id in all future calls |
| Response  | name  | string | Echo of the registered name |
| Response  | registered_at | ISO 8601 datetime (UTC) | |

### GET /devices
Returns an array of all registered devices (same fields as POST /devices response).

### POST /events
Ingest a batch of events. Returns 202 immediately.

**Request body:** `{ "events": [ <EventCreate>, ... ] }`

Each `EventCreate`:

| Field | Type | Notes |
|-------|------|-------|
| id | UUID string | Generated by the agent |
| device_id | UUID string | From POST /devices response |
| event_type | string enum | `process_start`, `process_stop`, `window_focus`, `file_change` |
| text | string | Human-readable description |
| timestamp | ISO 8601 datetime (UTC) | Must end in Z |
| prev_hash | string (64 hex chars) | Hash of previous event; 64 zeros for first |
| hash | string (64 hex chars) | SHA-256 of `JSON.stringify([prevHash, id, timestamp, text])` |

**Response:** `{ "accepted": <count> }`

### GET /events

| Query param | Type | Default | Notes |
|-------------|------|---------|-------|
| device_id | UUID | — | Filter by device |
| since | ISO 8601 datetime | — | Events at or after this time |
| until | ISO 8601 datetime | — | Events before or at this time |
| limit | integer | 100 | Max 1000 |

Response: array of EventCreate fields ordered by timestamp ASC.

### GET /verify/{device_id}

| Response field | Type | Notes |
|----------------|------|-------|
| valid | boolean | True if every hash checks out |
| count | integer | Total events checked (when valid=true) |
| broken_at | integer | 0-based index of first bad event (when valid=false) |
| event_id | UUID string | ID of first bad event (when valid=false) |

### GET /health
`{ "status": "ok", "db": "ok", "redis": "ok" }` — or 503 with which component failed.

### WebSocket /ws/events
Streams one JSON object per text frame as events are ingested. Same fields as EventCreate.

---

## Gotchas

### Hash payload must be byte-identical to the frontend

The frontend computes:
```js
JSON.stringify([prevHash, id, timestamp, text])
```
Python MUST use:
```python
json.dumps([prev_hash, id, timestamp, text], separators=(',', ':'), ensure_ascii=False)
```
Then `.encode('utf-8')` and SHA-256. One extra space = every hash mismatches.

### Store all timestamps in UTC

The agent sends timestamps ending in `Z` (UTC ISO 8601). Postgres columns use `timezone=True`. Never store naive datetimes.

### Redis Stream consumer groups need XACK after a successful write

Call `XACK` **only after** the Postgres commit succeeds. If you `XACK` before the commit and the worker crashes, the event is lost forever. Use `XAUTOCLAIM` on startup to re-process messages that were claimed but never acknowledged.

### Running the frontend

No build step needed. Just open `frontend/index.html` in a browser. For local development with the API, serve it via a local HTTP server (not `file://`) so CORS works:
```bash
npx serve frontend
# or
python -m http.server 5500 --directory frontend
```
Then set `CORS_ORIGINS=http://localhost:5500` in `backend/.env`.
