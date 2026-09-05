import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


LOG_FILE = (
    Path(__file__).resolve().parents[1]
    / "mock_data"
    / "personalization_logs.jsonl"
)


def create_analysis_session(
    user_id: str,
    symbol: str,
) -> str:
    session_id = str(uuid4())

    record = {
        "event": "analysis_session",
        "session_id": session_id,
        "user_id": user_id,
        "symbol": symbol,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    _write(record)

    return session_id


def log_personalization_result(
    session_id: str,
    risk_score: float,
    suitability_score: float,
    risk_level: str,
    suitability: str,
) -> None:
    record = {
        "event": "personalization_result",
        "session_id": session_id,
        "risk_score": risk_score,
        "suitability_score": suitability_score,
        "risk_level": risk_level,
        "suitability": suitability,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    _write(record)


def _write(record: dict) -> None:
    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(record)
            + "\n"
        )