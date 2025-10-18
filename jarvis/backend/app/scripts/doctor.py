from __future__ import annotations

from ..core.settings import settings

REQUIRED = [
    "DATABASE_URL",
    "REDIS_URL",
    "LLM_PROVIDER",
]


def main() -> None:
    missing = [name for name in REQUIRED if not getattr(settings, name.lower())]
    if missing:
        print(f"Missing settings: {', '.join(missing)}")
    else:
        print("All required settings present")


if __name__ == "__main__":
    main()
