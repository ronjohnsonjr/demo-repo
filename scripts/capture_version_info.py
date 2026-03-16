"""Capture GitHub API version and rate limit info for debugging.

Usage:
    python scripts/capture_version_info.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """Capture and display GitHub API metadata."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Get rate limit info
    resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
    rate_data = resp.json()

    # Get API root for version info
    root_resp = requests.get("https://api.github.com", headers=headers, timeout=10)

    info = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "authenticated": token is not None,
        "rate_limit": rate_data.get("rate", {}),
        "search_limit": rate_data.get("resources", {}).get("search", {}),
        "api_version": resp.headers.get("X-GitHub-Api-Version", "unknown"),
        "python_version": sys.version,
    }

    output_path = Path("reports/version_info.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(info, f, indent=2)

    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
