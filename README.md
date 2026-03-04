# ⚡ Eurostat Energy AI Platform

A fully Dockerized ETL + Data Warehouse + Analytics + Forecasting + AI Insights platform built with Python, PostgreSQL, FastAPI, and React.

This project extracts real-world European energy statistics from the Eurostat REST API, loads them into a PostgreSQL database, and serves a professional interactive dashboard for exploring electricity production and final energy consumption across Europe.

---

## Tech Stack

### Backend & ETL
- Python 3.11
- FastAPI + Uvicorn (REST API)
- Pandas, SQLAlchemy, Requests
- Python-dotenv
- Docker & Docker Compose

### Storage
- PostgreSQL 16
- PGAdmin 4

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Recharts (charts)
- TanStack Query (data fetching)
- Axios

### Machine Learning
- XGBoost
- Statsmodels (Exponential Smoothing)

### AI / RAG
- TF-IDF semantic search
- Trend-based reasoning engine
- Natural-language insights generation

---

## Architecture

```
Eurostat-Energy-AI-Platform/
│
├── api/                          # FastAPI backend
│   ├── main.py                   # App entry-point + CORS
│   ├── dependencies.py           # Shared DB engine (cached)
│   ├── schemas.py                # Pydantic response models
│   └── routers/
│       ├── data.py               # GET /data/, GET /data/metrics
│       ├── forecast.py           # GET /forecast/
│       └── insights.py           # POST /insights/ask
│
├── frontend/                     # React + TypeScript SPA
│   ├── src/
│   │   ├── api/client.ts         # Typed axios API client
│   │   ├── components/           # KPICard, Sidebar, Spinner, ErrorAlert
│   │   ├── pages/                # Overview, DataExplorer, Forecasting, AIInsights
│   │   └── App.tsx
│   ├── Dockerfile                # Multi-stage: build → Nginx
│   └── nginx.conf                # Nginx config with API proxy
│
├── etl/                          # ETL pipeline
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── llm_app/                      # RAG-based AI insights
│   ├── build_knowledge_base.py
│   ├── chatbot.py
│   └── rag_engine.py
│
├── ml/                           # ML forecasting
│   ├── forecast_utils.py
│   └── train_forecast_model.py
│
├── tests/                        # Unit tests
│   └── test_transform.py
│
├── viz/                          # Static chart generation
│   └── viz_utils.py
│
├── postgres/
│   └── init.sql
│
├── Dockerfile                    # Python backend image
├── docker-compose.yml
└── requirements.txt
```

---

## Eurostat API — Data Sources

The ETL pipeline retrieves official European energy statistics from the Eurostat REST API (no authentication required).

### Datasets Used

#### 1. nrg_cb_e — Electricity Supply / Transformation / Consumption
- GEP — Gross Electricity Production

#### 2. ten00124 — Final Energy Consumption by Sector
- FC_E — Final Energy Consumption (All sectors)
- FC_IND_E — Industry
- FC_TRA_E — Transport
- FC_OTH_CP_E — Commercial & Public Services
- FC_OTH_HH_E — Households

---

## Setup Instructions (Docker)

### 1. Clone the repository

```bash
git clone https://github.com/nitishkpandey/Eurostat-Energy-AI-Platform.git
cd Eurostat-Energy-AI-Platform
```

### 2. Create a `.env` file in the project root

```env
DB_USER=energy_user
DB_PASS=energy_pass
DB_HOST=db
DB_PORT=5432
DB_NAME=energy
POSTGRES_PASSWORD=energy_pass

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```

### 3. Run the full stack

```bash
docker compose up --build
```

Docker Compose will:

1. Start PostgreSQL
2. Run the ETL pipeline (loads API data into Postgres)
3. Start the FastAPI backend on **port 8000**
4. Build and serve the React frontend on **port 3000** (via Nginx)
5. Start PGAdmin on **port 5050**

### 4. Access the services

| Service        | URL                          |
|----------------|------------------------------|
| React Dashboard | http://localhost:3000        |
| FastAPI Docs   | http://localhost:8000/docs   |
| PGAdmin        | http://localhost:5050        |

### 5. Clean up

```bash
docker compose down -v
```

---

## Running Tests

```bash
# Python unit tests
pytest tests/

# Type checking
mypy api/ etl/ ml/ llm_app/ --ignore-missing-imports

# Frontend build check
cd frontend && npm run build
```

---

## API Endpoints

| Method | Endpoint         | Description                        |
|--------|------------------|------------------------------------|
| GET    | /health          | Liveness probe                     |
| GET    | /data/           | All observations (year filter)     |
| GET    | /data/metrics    | KPI metrics for overview dashboard |
| GET    | /forecast/       | ML forecast for country+indicator  |
| POST   | /insights/ask    | AI-powered question answering      |

Full interactive documentation: `http://localhost:8000/docs`

---

## Contact

**Nitish Kumar Pandey**  
LinkedIn: [linkedin.com/in/nitishkpandey](https://www.linkedin.com/in/nitishkpandey/)
