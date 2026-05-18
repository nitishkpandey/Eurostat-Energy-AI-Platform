# Eurostat Energy AI Platform

A modern, enterprise-grade Data & AI platform built to analyze, forecast, and chat with European energy data. 

This platform extracts data from Eurostat, transforms it using modern ELT pipelines, stores it in PostgreSQL, and serves it through a FastAPI backend to a dynamic React dashboard. It also features a machine-learning forecasting engine and a conversational AI agent powered by semantic vector search.

---

## 🌟 Highlights

- **Modern Data Stack (ELT):** Infrastructure-as-code orchestration with **Apache Airflow** and SQL transformations using **dbt (Data Build Tool)**.
- **AI Agent (RAG):** Multi-turn conversational AI powered by semantic vector embeddings (`sentence-transformers` / `all-MiniLM-L6-v2`) and cosine similarity.
- **Predictive Analytics:** Forecasting pipelines using XGBoost and Exponential Smoothing models.
- **Unified DX:** Configured as a `pnpm` workspace for seamless one-command `pnpm dev` startup across backend, frontend, and database.
- **API-First Architecture:** Strongly typed **FastAPI** backend with automated Swagger documentation.
- **Modular Frontend:** React + Vite architecture utilizing custom React Hooks for state management and Recharts for beautiful visualizations.
- **Resilience:** Built-in TTL caching (`cachetools`) and exponential backoff retry logic for external API ingestion.

---

## 🏗️ Architecture

```text
Eurostat-Energy-AI-Platform/
├── airflow/                    # Apache Airflow DAGs (Pipeline Orchestration)
├── dbt/                        # dbt project (SQL Data Transformations)
├── backend/
│   ├── api/                    # FastAPI routes and request schemas
│   ├── core/                   # Shared Database connection pooling
│   ├── etl/                    # Python Data Ingestion (Extract/Load)
│   ├── services/
│   │   ├── analytics/          # Overview & Explorer data services
│   │   ├── ai/                 # Vector Embeddings & RAG Chatbot
│   │   └── forecasting/        # ML Models (XGBoost)
│   └── tests/                  # Pytest validation suites
├── frontend/                   # React Workspace
│   └── src/
│       ├── features/           # Modular Pages (Overview, Explorer, AiAgent)
│       └── shared/             # Custom Hooks, UI Components, API Client
├── package.json                # pnpm workspace root
└── docker-compose.yml          # Container orchestration
```

---

## 🚀 Quick Start (Local Development)

We use a `pnpm` workspace to manage the entire full-stack application. 

### Prerequisites
- Node.js & pnpm (`npm i -g pnpm`)
- Python 3.11+ & uv (`pip install uv`)
- Docker Desktop (for PostgreSQL & Airflow)

### 1. Environment Setup
Create a `.env` file in the root directory (you can copy `.env.example`):
```bash
cp .env.example .env
```

### 2. Install Dependencies
Install both backend (Python) and frontend (Node) dependencies with one command from the project root:
```bash
pnpm install
```

### 3. Run the Platform
Spin up the database, backend, and frontend concurrently:
```bash
pnpm dev
```

- **Frontend Dashboard:** `http://localhost:5173`
- **Backend API & Swagger:** `http://localhost:8000/docs`

---

## 🧠 The AI Agent

The AI Agent allows users to interact with complex energy datasets using natural language. 
Unlike basic search algorithms, this agent uses **Retrieval-Augmented Generation (RAG)** powered by semantic vector embeddings.

When data is loaded, the backend uses `sentence-transformers` to map energy trends into a high-dimensional vector space. When a user asks a question, the platform converts the question into a vector and mathematically calculates the **Cosine Similarity** to find the most relevant data—even if the user uses different vocabulary. It also maintains conversation history for context-aware follow-up questions.

---

## 🛠️ Data Engineering (Airflow & dbt)

This project showcases enterprise-grade data engineering patterns:
- **Apache Airflow (`airflow/dags/eurostat_etl_dag.py`):** Orchestrates the daily ELT pipeline, waits for database availability, triggers data extraction, and runs transformations.
- **dbt (`dbt/models/`):** Replaces basic Pandas transformations with modular, testable SQL models, transforming raw JSON extracts into a clean analytical Star Schema.

---

## 🧪 Testing

The backend is fully typed (checked via `mypy`) and tested (via `pytest`).

```bash
# Run type checking
uv run mypy backend/

# Run unit and service tests
uv run pytest backend/tests/
```
