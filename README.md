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
│   ├── api/                    # FastAPI routes and service layer
│   ├── core/                   # Shared DB utilities
│   ├── etl/                    # ETL pipeline
│   ├── llm_app/                # AI / semantic search
│   ├── ml/                     # Forecasting
│   ├── tests/                  # Unit tests
│   └── viz/                    # Static visual exports
├── frontend/                   # React app (Vite)
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
DB_USER=energy_user
DB_PASS=energy_pass
DB_HOST=db
DB_PORT=5432
DB_NAME=energy
POSTGRES_PASSWORD=energy_pass

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
uv run pytest backend/tests
```

## UI Notes

The dashboard UI is intentionally dynamic and production-styled:

- Live API health status and realtime clock in the hero header
- Animated ambient background and tab-based accent themes
- Year-window presets and data sync controls
- Interactive producer cards that deep-link into explorer analysis
- Enhanced forecasting summary cards and richer chart styling
- AI quick-question chips for faster exploratory prompts

## Engineering Notes

- Shared database logic is centralized in `backend/core/database.py` (DRY)
- API response shaping is centralized in `backend/api/services.py`
- Frontend API access is centralized in `frontend/src/api/client.js`
- Legacy Streamlit codepath has been removed

