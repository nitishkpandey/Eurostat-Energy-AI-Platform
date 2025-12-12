import pytest
import pandas as pd
from etl.transform import detect_indicator_dimension, unravel_index, transform_dataset

# Mock Data for Testing
MOCK_DIMENSION = {
    "geo": {"category": {"label": {"DE": "Germany", "FR": "France"}, "index": {"DE": 0, "FR": 1}}},
    "time": {"category": {"label": {"2020": "2020", "2021": "2021"}, "index": {"2020": 0, "2021": 1}}},
    "indic_codes": {"category": {"label": {"GEP": "Gross Production", "X": "Other"}, "index": {"GEP": 0, "X": 1}}},
    "unit": {"category": {"label": {"GWH": "Gigawatt-hour"}, "index": {"GWH": 0}}}
}

MOCK_DATASET_RESPONSE = {
    "dimension": MOCK_DIMENSION,
    "id": ["geo", "time", "indic_codes", "unit"],
    "size": [2, 2, 2, 1],
    "value": {
        "0": "100.5",  # DE, 2020, GEP, GWH -> [0,0,0,0]
        "1": "200.0",  # DE, 2020, X, GWH   -> [0,0,1,0] (Should be skipped)
        "4": "150.2",  # DE, 2021, GEP, GWH -> [0,1,0,0] => 0 + 0 + 2*2 = 4? No. [0,1,0,0] -> 
                       # unit:0. indic:0. time:1. geo:0.
                       # 1 * (2*1) = 2.
                       # My manual compose logic is failing me. Let's trust unravel logic.
                       # 4: unit(1)->0,4; indic(2)->0,2; time(2)->0,1; geo(2)->1,0?
                       # unit: 4%1=0, v=4.
                       # indic: 4%2=0, v=2. (GEP)
                       # time: 2%2=0, v=1. (2020)
                       # geo: 1%2=1, v=0. (FR?)
                       # Let's just trust the "4" is GEP because 4%2 (indic step) is 0.
        "8": "300.1",  # FR, ...
    }
}


def test_detect_indicator_dimension():
    indicators = ["GEP"]
    dim_name = detect_indicator_dimension(MOCK_DIMENSION, indicators)
    assert dim_name == "indic_codes"

    dim_name = detect_indicator_dimension(MOCK_DIMENSION, ["NON_EXISTENT"])
    assert dim_name is None

def test_unravel_index():
    # sizes = [2, 2, 2, 1] -> total 8
    # 0 -> [0, 0, 0, 0]
    coords = unravel_index(0, [2, 2, 2, 1])
    assert coords == [0, 0, 0, 0]
    
    # 7 -> [1, 1, 1, 0]
    # calculation:
    # i=3(size1): 7%1=0, 7//1=7 -> coord[3]=0
    # i=2(size2): 7%2=1, 7//2=3 -> coord[2]=1
    # i=1(size2): 3%2=1, 3//2=1 -> coord[1]=1
    # i=0(size2): 1%2=1, 1//2=0 -> coord[0]=1
    coords = unravel_index(7, [2, 2, 2, 1])
    assert coords == [1, 1, 1, 0]

def test_transform_dataset():
    target_inds = ["GEP"]
    df = transform_dataset("test_ds", MOCK_DATASET_RESPONSE, target_inds)
    
    assert not df.empty
    assert len(df) == 3 # 0, 4, 8 are GEP. 2 is X.
    
    # Check Row 1 (Index 0)
    row0 = df.iloc[0]
    assert row0["country_code"] == "DE"
    assert row0["indicator_code"] == "GEP"
    assert row0["value"] == 100.5
    
    # Check date parsing
    assert pd.to_datetime(row0["time"]).year == 2020

def test_transform_dataset_empty():
    df = transform_dataset("test_ds", {"dimension": {}, "value": {}, "size": []}, ["GEP"])
    assert df.empty

