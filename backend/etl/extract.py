import requests
from typing import Dict, Any, Optional

def fetch_dataset(dataset_code: str, url: str) -> Optional[Dict[str, Any]]:
    """
    Fetches JSON data from the Eurostat API.
    Returns the parsed JSON dictionary or None if the request failed or keys are missing.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Basic validation
        required_keys = ['dimension', 'value', 'size']
        if not all(key in data for key in required_keys):
            print(f"Skipping {dataset_code}: Missing expected keys {required_keys}.")
            return None
            
        return data
    except requests.RequestException as e:
        print(f"Error fetching {dataset_code}: {e}")
        return None
