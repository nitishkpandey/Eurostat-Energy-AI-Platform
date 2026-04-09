import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

def detect_indicator_dimension(dimensions: Dict[str, Any], indicators: List[str]) -> Optional[str]:
    """
    Identifies which dimension key corresponds to the 'indicator' concept
    by checking if any of the target indicators are present in the dimension labels.
    """
    for dim_name, dim_info in dimensions.items():
        labels = dim_info.get("category", {}).get("label", {})
        if any(ind in labels for ind in indicators):
            return dim_name
    return None

def unravel_index(flat_index: int, sizes: List[int]) -> List[int]:
    """
    Converts a flat index from Eurostat's JSON format into multi-dimensional coordinates.
    """
    coords = []
    # Eurostat flattening usually matches C-order relative to the 'size' array reversed in the original code logic,
    # or the code assumes a specific packing. 
    # The original code:
    # for size in reversed(sizes):
    #     coords.append(flat_index % size)
    #     flat_index //= size
    # return list(reversed(coords))
    
    for size in reversed(sizes):
        coords.append(flat_index % size)
        flat_index //= size
    return list(reversed(coords))

def transform_dataset(dataset_code: str, data: Dict[str, Any], target_indicators: List[str]) -> pd.DataFrame:
    """
    Transforms raw JSON data from Eurostat into a clean Pandas DataFrame.
    """
    dim = data['dimension']
    dim_ids = data.get('id', list(dim.keys()))
    sizes = data['size']
    value_data = data['value']
    
    labels = {k: dim[k]['category']['label'] for k in dim if 'category' in dim[k]}
    indexes = [dim[d]['category']['index'] for d in dim_ids]

    indicator_dim = detect_indicator_dimension(dim, target_indicators)
    if not indicator_dim:
        print(f"Could not detect indicator dimension in dataset {dataset_code}")
        return pd.DataFrame()

    result = []
    
    # Pre-calculate keys for efficiency if possible, but the original logic
    # iterates over value_data items which are sparse.
    
    for flat_index_str, val in value_data.items():
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            # value might be ":", "na" etc.
            continue
            
        idx = unravel_index(int(flat_index_str), sizes)
        
        # Mapping dimension names to their value labels
        # The 'indexes' list maps position -> label_key
        # We need to look up label_key -> actual label text
        
        # Make a dictionary of {dimension_id: key_code}
        keys = [list(indexes[i].keys())[idx[i]] for i in range(len(idx))]
        dim_map = {dim_ids[i]: keys[i] for i in range(len(dim_ids))}
        
        indicator = dim_map.get(indicator_dim)
        if indicator not in target_indicators:
            continue

        result.append({
            "dataset_code": dataset_code,
            "country_code": dim_map.get("geo"),
            "country_name": labels.get("geo", {}).get(dim_map.get("geo"), dim_map.get("geo")),
            "indicator_code": indicator,
            "indicator_label": labels.get(indicator_dim, {}).get(indicator),
            "unit_code": dim_map.get("unit"),
            "unit_label": labels.get("unit", {}).get(dim_map.get("unit")),
            "time": dim_map.get("time"),
            "value": val_float
        })

    print(f"Transformed {len(result)} rows for {dataset_code}")
    
    if not result:
        return pd.DataFrame()

    df = pd.DataFrame(result)

    # Cleaning
    # Remove duplicates
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        print(f"Found {num_duplicates} duplicate rows. Removing them.")
        df = df.drop_duplicates()

    # Handle missing values
    cols_check = ['country_code', 'country_name', 'indicator_code', 'indicator_label', 'time', 'value']
    missing_count = df[cols_check].isnull().sum().sum()
    if missing_count > 0:
        print("Missing values detected. Dropping rows with missing critical values.")
        df = df.dropna(subset=cols_check)

    # Parse date
    df['time'] = pd.to_datetime(df['time'], format='%Y')
    
    # Add timestamp
    df["load_timestamp"] = datetime.now()

    print(f"Cleaned data: {len(df)} rows remaining for {dataset_code}.")
    return df
