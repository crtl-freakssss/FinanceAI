import sys
import pytest
from pathlib import Path
from security.rate_limiter import rate_limiter

# Add person4_personalization root to sys.path so tests can import modules directly
package_dir = Path(__file__).resolve().parent.parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))


@pytest.fixture(autouse=True)
def reset_rate_limit():
    rate_limiter.reset()
