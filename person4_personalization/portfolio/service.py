import json
from pathlib import Path
from typing import Any, Dict, Optional

_DATA_FILE = Path(__file__).resolve().parent.parent / "mock_data" / "portfolios.json"


def _load_portfolios_raw() -> Dict[str, dict]:
    if not _DATA_FILE.exists():
        return {}
    with open(_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_portfolio(user_id: str) -> Optional[Dict[str, Any]]:
    portfolios = _load_portfolios_raw()
    return portfolios.get(user_id)
