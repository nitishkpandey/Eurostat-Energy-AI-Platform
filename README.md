# Eurostat Energy AI Platform

A Dockerized data + AI platform for European energy analytics.

This version ships a React frontend with a FastAPI backend, keeping ETL + forecasting + AI insights in one cohesive stack.

## Highlights

- Eurostat API ingestion and ETL into PostgreSQL
- API-first architecture with FastAPI
- Dynamic React dashboard with multi-tab analytics workflows
- Forecasting pipeline (XGBoost + Exponential Smoothing)
- AI Q&A assistant with semantic retrieval
- Static typing checks with mypy
- uv-first dependency and lockfile workflow

## Architecture

- Backend API: FastAPI + Python analytics modules
- Frontend UI: React + Vite + Recharts
- Storage: PostgreSQL
- Orchestration: Docker Compose

## Project Structure

```text
Eurostat-Energy-AI-Platform/
├── backend/
│   ├── api/                    # FastAPI routes and request schemas
│   ├── core/                   # Shared DB utilities
│   ├── etl/                    # ETL pipeline
│   ├── services/               # Analytics/forecast/assistant service layer
│   │   ├── analytics/          # Overview/explorer/metadata builders
│   │   ├── ai/                 # AI question answering + RAG modules
│   │   └── models/             # Forecast model implementations
│   ├── tests/                  # Unit tests
│   └── viz/                    # Static visual exports
├── frontend/
│   └── src/
│       ├── app/                # App shell + routing
│       ├── features/           # Feature pages (overview/explorer/forecast/ai)
│       ├── shared/
│       │   ├── api/            # Frontend API client
│       │   ├── ui/             # Shared UI components
│       │   └── utils/          # Shared data/format helpers
│       └── styles/             # Global theme and layout styles
├── outputs/                    # Generated figures
├── postgres/                   # DB init SQL
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml              # uv + mypy config
├── uv.lock                     # uv lockfile
└── README.md
```

## API Endpoints

Base URL: `http://localhost:8000`

- `GET /api/health`
- `GET /api/metadata`
- `GET /api/overview?start_year=&end_year=`
- `GET /api/explorer?country_code=&indicator_code=&start_year=&end_year=`
- `POST /api/forecast`
- `POST /api/ai/ask`
- `POST /api/cache/refresh`

## Run With Docker

1. Create `.env` in project root:

```env
POSTGRES_USER=energy_user
POSTGRES_PASSWORD=energy_pass
POSTGRES_DB=energy

DB_USER=energy_user
DB_PASS=energy_pass
DB_HOST=db
DB_PORT=5432
DB_NAME=energy

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
```

2. Start services:

```bash
docker compose up --build
```

3. Access:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- PGAdmin: `http://localhost:5050`

4. Stop:

```bash
docker compose down -v
```

## Local Development (uv Preferred)

### Backend

```bash
uv sync --python 3.11 --extra dev
uv run uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

The project targets Python 3.11/3.12 for dependency compatibility.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run Full App With uv + Persistent Logs

Run backend + frontend together with one command:

```bash
uv run run-app
```

Optional first-time frontend install:

```bash
uv run run-app --install-frontend
```

This writes persistent logs to:

- `logs/main.log` (launcher/orchestration events)
- `logs/backend.log` (FastAPI/uvicorn output)
- `logs/frontend.log` (Vite/frontend output)

Tail all logs live:

```bash
tail -f logs/main.log logs/backend.log logs/frontend.log
```

If Docker is already running on ports `8000` or `5173`, either stop it first or run on different ports:

```bash
uv run run-app --backend-port 8001 --frontend-port 5174 --frontend-api-base-url http://localhost:8001
```

## Static Typing (mypy)

Run type checks from project root:

```bash
uv run mypy
```

Configuration lives in `pyproject.toml` under `[tool.mypy]`.

## ETL and Visual Generation

```bash
python -m backend.etl.main --mode full-refresh
python -m backend.viz.viz_utils
```

Modes:

- `full-refresh`
- `truncate`
- `append`

## Tests

```bash
uv sync --extra dev
uv run pytest backend/tests
```

## UI Notes

The dashboard is keyboard-first and optimized for focused analysis:

- Command palette and quick-create flows for faster navigation
- Centered platform identity in the main workspace area
- Collapsible sidebar for distraction-free exploration
- Single-column content sections to reduce visual noise

## Engineering Notes

- Shared database logic is centralized in `backend/core/database.py` (DRY)
- API response shaping is centralized in `backend/services/analytics/`
- AI assistant and forecasting model internals are centralized in `backend/services/ai/` and `backend/services/models/`
- Frontend API access is centralized in `frontend/src/shared/api/client.js`
- Frontend shared UI and helper logic live in `frontend/src/shared/ui/` and `frontend/src/shared/utils/`
- Legacy Streamlit codepath has been removed

