import math
import re
from typing import Any, Optional


SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9\.\-\_]{1,30}$")
USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9\.\-\_]{1,100}$")


def is_safe_identifier(val: str) -> bool:
    """Checks whether an identifier contains dangerous path traversal or special chars."""
    if not val or not isinstance(val, str):
        return False
    if ".." in val or "/" in val or "\\" in val or "\0" in val:
        return False
    return True


def validate_symbol(symbol: str) -> bool:
    if not is_safe_identifier(symbol):
        return False
    return bool(SYMBOL_PATTERN.match(symbol))


def validate_user_id(user_id: str) -> bool:
    if not is_safe_identifier(user_id):
        return False
    return bool(USER_ID_PATTERN.match(user_id))


def is_valid_finite_number(val: Any) -> bool:
    """Checks whether a number is a valid finite float/int (not NaN or Inf)."""
    try:
        if val is None:
            return False
        num = float(val)
        return not (math.isnan(num) or math.isinf(num))
    except (TypeError, ValueError):
        return False


def sanitize_numeric(val: Any, default: float = 0.0, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    """Sanitizes a numeric value to ensure it is finite and bounded."""
    if not is_valid_finite_number(val):
        return default
    num = float(val)
    if min_val is not None and num < min_val:
        num = min_val
    if max_val is not None and num > max_val:
        num = max_val
    return num
