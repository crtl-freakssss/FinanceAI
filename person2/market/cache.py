import json
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")

def get_cache(key, max_age_seconds=3600):
    path = _get_cache_path(key)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if time.time() - data.get('timestamp', 0) <= max_age_seconds:
                return data.get('payload')
        except Exception:
            pass
    return None

def set_cache(key, payload):
    path = _get_cache_path(key)
    data = {
        'timestamp': time.time(),
        'payload': payload
    }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception:
        pass
