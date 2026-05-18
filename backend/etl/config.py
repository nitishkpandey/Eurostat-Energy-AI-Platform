"""ETL dataset definitions.

Database configuration has been consolidated into backend.core.database.
Import get_engine() from there — do NOT add DB credentials here.
"""
from __future__ import annotations

# Dataset Definitions
DATASETS = {
    "nrg_cb_e": {
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_cb_e?nrg_bal=GEP&lang=EN",
        "indicators": ["GEP"],
    },
    "ten00124": {
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ten00124?lang=EN",
        "indicators": [
            "FC_E",
            "FC_IND_E",
            "FC_TRA_E",
            "FC_OTH_CP_E",
            "FC_OTH_HH_E",
        ],
    },
}
