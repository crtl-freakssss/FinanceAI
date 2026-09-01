import sys
from pathlib import Path

# Add person4_personalization root to sys.path so tests can import modules directly
package_dir = Path(__file__).resolve().parent.parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))
