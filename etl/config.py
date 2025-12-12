import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
# Assuming this file is in etl/config.py, the root is two levels up
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOTENV_PATH = PROJECT_ROOT / '.env'
load_dotenv(DOTENV_PATH)

# Database Credentials
DB_USER = os.environ.get("DB_USER", "user")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "db")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Dataset Definitions
DATASETS = {
    "nrg_cb_e": {
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_cb_e?nrg_bal=GEP&lang=EN",
        "indicators": ["GEP"]
    },
    "ten00124": {
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ten00124?lang=EN",
        "indicators": [
            "FC_E", "FC_IND_E", "FC_TRA_E", "FC_OTH_CP_E", "FC_OTH_HH_E"
        ]
    }
}
