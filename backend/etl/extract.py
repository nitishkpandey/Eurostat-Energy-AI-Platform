import time
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def fetch_dataset(dataset_code: str, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    Fetches JSON data from the Eurostat API with retry logic.
    Returns the parsed JSON dictionary or None if the request failed or keys are missing.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Basic validation
            required_keys = ['dimension', 'value', 'size']
            if not all(key in data for key in required_keys):
                logger.warning(f"Skipping {dataset_code}: Missing expected keys {required_keys}.")
                return None
                
            return data
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {dataset_code}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"All retries failed for {dataset_code}.")
                return None
