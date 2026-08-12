"""Put the repository root on sys.path so tests can import `src.greeting_service`.

pytest's default import mode adds the test file's own directory, not the repo
root, so without this the acceptance tests cannot see the package.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
