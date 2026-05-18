import pandas as pd
from backend.services.analytics.overview import build_overview

def test_build_overview():
    data = [
        {"geo": "FR", "country_name": "France", "indicator": "GEP", "year": 2020, "value": 100},
        {"geo": "FR", "country_name": "France", "indicator": "GEP", "year": 2021, "value": 110},
        {"geo": "DE", "country_name": "Germany", "indicator": "GEP", "year": 2020, "value": 200},
        {"geo": "DE", "country_name": "Germany", "indicator": "GEP", "year": 2021, "value": 190},
    ]
    df = pd.DataFrame(data)
    
    overview = build_overview(df, 2020, 2021)
    
    assert overview["latest_year"] == 2021
    # 2021 Total GEP: FR(110) + DE(190) = 300
    # 2020 Total GEP: FR(100) + DE(200) = 300
    assert overview["kpis"]["latest_gep"] == 300.0
    assert overview["kpis"]["gep_change_pct"] == 0.0 # 300 to 300
    assert overview["kpis"]["countries_reporting"] == 2
    
    # Top producer should be DE in 2021 (190)
    assert overview["kpis"]["top_producer"]["country_code"] == "DE"
    
    assert overview["selected_country_code"] == "DE" # It has the highest mean over the period
    assert len(overview["top_producers"]) == 2

def test_build_overview_empty():
    df = pd.DataFrame(columns=["geo", "country_name", "indicator", "year", "value"])
    overview = build_overview(df, 2020, 2021)
    
    assert overview["latest_year"] is None
    assert overview["kpis"]["latest_gep"] == 0.0
    assert overview["selected_country_code"] is None
