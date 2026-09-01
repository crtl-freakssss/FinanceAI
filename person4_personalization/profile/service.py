import json
from pathlib import Path
from typing import Dict, Optional
from models.profile import UserProfile
from models.preferences import UserPreferences
from models.constraints import InvestmentConstraints

_DATA_FILE = Path(__file__).resolve().parent.parent / "mock_data" / "profiles.json"


def _load_profiles_raw() -> Dict[str, dict]:
    if not _DATA_FILE.exists():
        return {}
    with open(_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_profile(user_id: str) -> Optional[UserProfile]:
    profiles = _load_profiles_raw()
    data = profiles.get(user_id)
    if not data:
        return None
    return UserProfile(**data)


def get_preferences(user_id: str) -> Optional[UserPreferences]:
    profile = get_profile(user_id)
    if profile and profile.preferences:
        return profile.preferences
    return None


def get_constraints(user_id: str) -> Optional[InvestmentConstraints]:
    profile = get_profile(user_id)
    if profile and profile.constraints:
        return profile.constraints
    return None
