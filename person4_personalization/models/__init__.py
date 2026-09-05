import pkgutil
import sys
from pathlib import Path

__path__ = pkgutil.extend_path(__path__, __name__)

# Ensure person1 models path is always included in models namespace
_p1_models = str(Path(__file__).resolve().parent.parent.parent / "person1" / "models")
if _p1_models not in __path__:
    __path__.append(_p1_models)
