"""Check current GitHub API rate limit status.

Usage:
    python scripts/check_rate_limit.py
"""

import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """Display current rate limit status."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
    data = resp.json()

    core = data.get("rate", {})
    search = data.get("resources", {}).get("search", {})

    reset_time = datetime.fromtimestamp(core.get("reset", 0), tz=timezone.utc)

    print(f"Core API:   {core.get('remaining', '?')}/{core.get('limit', '?')} remaining")
    print(f"Search API: {search.get('remaining', '?')}/{search.get('limit', '?')} remaining")
    print(f"Resets at:  {reset_time.isoformat()}")
    print(f"Auth mode:  {'Authenticated' if token else 'Unauthenticated'}")


if __name__ == "__main__":
    main()
