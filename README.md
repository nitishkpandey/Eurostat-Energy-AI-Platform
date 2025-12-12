#  **Eurostat Energy AI Platform**


A fully Dockerized ETL + Data Warehouse + Analytics + Forecasting + AI Insights platform built using Python, PostgreSQL, and Streamlit.  
This project extracts real-world European energy statistics from the Eurostat REST API, loads them into a PostgreSQL database, and serves an interactive dashboard for exploring electricity production and final energy consumption across Europe.

This is a complete, end-to-end, industry-style data engineering project showcasing:

- Real API ingestion  
- ETL pipeline (Extract → Transform → Load)  
- Containerization (Docker Compose)  
- Data warehousing (PostgreSQL)  
- Analytics dashboard (Streamlit + Plotly)  
- Automated visualizations (Matplotlib/Seaborn)  
- Machine learning forecasting (XGBoost + Exponential Smoothing)  
- AI Insights assistant (RAG + semantic search + trend analysis)  

---

# Tech Stack

## Backend & ETL
- Python 3.11  
- Pandas  
- SQLAlchemy  
- Requests  
- Python-dotenv  
- Docker & Docker Compose  

## Storage
- PostgreSQL 16  
- PGAdmin 4  

## Analytics
- Streamlit  
- Plotly  
- Matplotlib / Seaborn  

## Machine Learning
- XGBoost  
- Statsmodels (Exponential Smoothing)  

## AI / RAG
- Embeddings-based search  
- Trend-based reasoning engine  
- Natural-language insights generation  

---

# Eurostat API — Data Sources

The ETL pipeline retrieves official European energy statistics from the Eurostat REST API (no authentication required).

## Datasets Used

### 1. nrg_cb_e — Electricity Supply / Transformation / Consumption
Indicator:
- GEP — Gross Electricity Production

### 2. ten00124 — Final Energy Consumption by Sector
Indicators:
- FC_E — Final Energy Consumption (All sectors)  
- FC_IND_E — Industry  
- FC_TRA_E — Transport  
- FC_OTH_CP_E — Commercial & Public Services  
- FC_OTH_HH_E — Households  

---

# Project Structure



```
<<<<<<< Updated upstream
EUROSTAT-ENERGY-AI-PLATFORM/
│
├── .venv/
=======
Eurostat-Energy-AI-Platform/
>>>>>>> Stashed changes
│
├── app/
│ └── streamlit_app.py
│
├── etl/
<<<<<<< Updated upstream
│ └── main.py
=======
│   ├── config.py                 # Configuration & environment loading
│   ├── extract.py                # API data fetching
│   ├── transform.py              # Data cleaning & transformation logic
│   ├── load.py                   # Database connection & loading
│   └── main.py                   # Orchestrator script
│
├── tests/
│   └── test_transform.py         # Unit tests for transformation logic
>>>>>>> Stashed changes
│
├── llm_app/
│ ├── init.py
│ ├── build_knowledge_base.py
│ ├── chatbot.py
│ └── rag_engine.py
│
├── ml/
│ ├── init.py
│ ├── forecast_utils.py
│ └── train_forecast_model.py
│
├── outputs/
│ ├── DE_GEP_trend.png
│ ├── heatmap_GEP.png
│ └── top_10_GEP_2024.png
│
├── postgres/
│ └── init.sql
│
├── viz/
│ └── viz_utils.py
│
<<<<<<< Updated upstream
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
=======
├── requirements.txt              # Pinned Python dependencies
├── .env                          # Database credentials (not committed)
└── .gitignore                    # Prevents committing sensitive files
>>>>>>> Stashed changes
```

---

# **ETL Workflow**

The ETL pipeline (`etl/main.py`) performs:

### **1. Extract**

* Fetches JSON responses from Eurostat API endpoints
* Reads metadata, dimensions, indicators, units, and time series values

### **2. Transform**

* Converts Eurostat's multi-dimensional response into a clean tabular format
* Resolves indicator labels and country names
* Deduplicates observations
* Casts year → proper DATE
* Adds load timestamps

### **3. Load**

* Creates the `observations` table (if not exists)
* Supports 3 modes:

  * `full-refresh` (drop + recreate + load)
  * `truncate`
  * `append`
* Loads all observations into PostgreSQL via SQLAlchemy

---

#  **Streamlit Analytics Dashboard**

The project includes a full interactive dashboard (`app/streamlit_app.py`) with:

### **Overview Tab**

* Year selector
* Total EU Gross Electricity Production
* Top 10 GEP-producing countries
* Interactive bar charts

### **Country Explorer**

* Choose any country
* View historical GEP trend
* Sector-wise final energy consumption:

  * Industry
  * Transport
  * Public/Commercial
  * Households
* Line charts, pie charts, tables

### **Heatmap Tab**

* Heatmap of GEP across all years × all countries
* Visual exploration of long-term patterns

Everything is fully dynamic and rendered using **Plotly**.

---

# **Setup Instructions (Docker)**

## 1. Clone the repository

```bash
git clone https://github.com/your-username/Eurostat-Energy-AI-Platform.git
cd Eurostat-Energy-AI-Platform
```

---

## 2. Create a `.env` file in the project root

```
DB_USER=<DB_USER>
DB_PASS=<DB_PASS>
DB_HOST=db
DB_PORT=5432
DB_NAME=<DB_NAME>
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>

PGADMIN_DEFAULT_EMAIL=<PGADMIN_DEFAULT_EMAIL>@admin.com
PGADMIN_DEFAULT_PASSWORD=<PGADMIN_DEFAULT_PASSWORD>
```

**This file must NOT be pushed to GitHub.**

---

## 3. Run the full stack

```bash
docker compose up --build
```

Docker Compose will:

1. Start PostgreSQL
2. Start PGAdmin (access at [http://localhost:5050](http://localhost:5050))
3. Run the ETL pipeline (loads API data into Postgres)
4. Run the Streamlit dashboard server

---

## 4. Access the dashboard

Once everything starts, open:

**[http://localhost:8501](http://localhost:8501)**

---

## 5. Clean up containers & data

```bash
docker compose down -v
```

---

# **Running Tests**

To ensure the data transformation logic is working correctly, you can run the unit tests inside the Docker container:

```bash
docker compose run etl pytest tests/
```

This guarantees that tests run in the exact same environment as the production code.

---

# **Auto-Generated Visualizations**

In addition to the dashboard, the script `viz/viz_utils.py` generates:

* Line chart: GEP trend for Germany
* Bar chart: Top 10 GEP countries
* Heatmap: GEP across years and countries

Saved in:

```
outputs/
```

---

# **Insights from the Data**

**Example findings:**

- EU aggregates (EU27_2020, EA20) report the highest GEP values  
- Germany’s GEP increased until ~2017 and stabilized afterward  
- Transport and household sectors dominate consumption in many regions  
- Some non-EU countries show sparse data coverage  

---

# **Contributions**

PRs, issues, and suggestions are welcome!
This project is fully open for learning and experimentation.

---

# **Contact**

For questions or collaboration:

**Nitish Kumar Pandey** 

**Linkedin: [linkedin.com/in/nitishkpandey](https://www.linkedin.com/in/nitishkpandey/)**

---
