"""Clean up test artifacts (database, logs, reports).

Usage:
    python scripts/cleanup_test_data.py
"""

from pathlib import Path


def main() -> None:
    """Remove generated test artifacts."""
    artifacts = [
        "data/test_results.db",
        "logs/test_run.log",
        "reports/junit.xml",
        "reports/report.html",
        "reports/version_info.json",
    ]

    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            path.unlink()
            print(f"Removed: {artifact}")
        else:
            print(f"Skipped: {artifact} (not found)")

    print("\nCleanup complete.")


if __name__ == "__main__":
    main()
