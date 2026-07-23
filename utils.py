import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate hash of the given string."""
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode())
    return hasher.hexdigest()


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def safe_json_dumps(data: Any, **kwargs) -> str:
    """Safely serialize data to JSON with pretty formatting."""
    try:
        return json.dumps(data, default=str, indent=2, **kwargs)
    except (TypeError, ValueError) as e:
        return f"{{\"error\": \"Failed to serialize: {str(e)}\"}}"


def batch_process(items: List[Any], process_fn, batch_size: int = 10) -> List[Any]:
    """Process items in batches."""
    results = []
    for batch in chunk_list(items, batch_size):
        for item in batch:
            results.append(process_fn(item))
    return results


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
