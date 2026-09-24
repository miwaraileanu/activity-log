# Activity Log

A tamper-evident activity logger with SHA-256 hash chaining.

## Structure

```
frontend/   — plain HTML + Tailwind CSS app
backend/    — FastAPI + PostgreSQL + Redis
agent/      — background collector (processes, active window, file changes)
```

## Quick start

**Frontend** — open `frontend/index.html` directly in a browser, or:
```bash
python -m http.server 5500 --directory frontend
```

**Backend**
```bash
cd backend
uv sync
cp ../.env.example .env   # fill in values
uv run uvicorn app.main:app --reload
```

**Agent**
```bash
cd agent
uv sync
cp ../.env.example .env
uv run python -m agent.main
```

**Infrastructure** (Postgres + Redis)
```bash
docker compose up postgres redis
```
