from __future__ import annotations

import sys
import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "postgresql://jarvis:jarvis@localhost:5432/jarvis")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
