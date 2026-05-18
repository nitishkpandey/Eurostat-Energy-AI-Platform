import pandas as pd
from backend.services.models.forecast_utils import run_forecast

def test_run_forecast():
    # Provide enough data to satisfy XGBoost and ES (requires history >= 5)
    data = [
        {"geo": "DE", "indicator": "GEP", "time": "2010-01-01", "value": 100},
        {"geo": "DE", "indicator": "GEP", "time": "2011-01-01", "value": 105},
        {"geo": "DE", "indicator": "GEP", "time": "2012-01-01", "value": 110},
        {"geo": "DE", "indicator": "GEP", "time": "2013-01-01", "value": 115},
        {"geo": "DE", "indicator": "GEP", "time": "2014-01-01", "value": 120},
        {"geo": "DE", "indicator": "GEP", "time": "2015-01-01", "value": 125},
        {"geo": "DE", "indicator": "GEP", "time": "2016-01-01", "value": 130},
        {"geo": "DE", "indicator": "GEP", "time": "2017-01-01", "value": 135},
        {"geo": "DE", "indicator": "GEP", "time": "2018-01-01", "value": 140},
    ]
    df = pd.DataFrame(data)
    
    forecast_df, model_name = run_forecast(df, country="DE", indicator="GEP", horizon=3)
    
    assert not forecast_df.empty
    assert model_name in ["XGBoost", "ExponentialSmoothing"]
    
    historical = forecast_df[forecast_df["type"] == "historical"]
    forecast = forecast_df[forecast_df["type"] == "forecast"]
    
    assert len(historical) == 9
    assert len(forecast) == 3
    assert int(forecast.iloc[0]["year"]) == 2019

def test_run_forecast_insufficient_data():
    # Only 3 points (needs >=5)
    data = [
        {"geo": "DE", "indicator": "GEP", "time": "2010-01-01", "value": 100},
        {"geo": "DE", "indicator": "GEP", "time": "2011-01-01", "value": 105},
        {"geo": "DE", "indicator": "GEP", "time": "2012-01-01", "value": 110},
    ]
    df = pd.DataFrame(data)
    
    forecast_df, model_name = run_forecast(df, country="DE", indicator="GEP", horizon=3)
    
    assert forecast_df.empty
    assert "insufficient data" in model_name.lower()
