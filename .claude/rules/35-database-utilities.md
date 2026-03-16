# Database Utilities

## Overview
`utils/database/db.py` provides a SQLite-backed test result tracker for:
- Recording test run metadata (endpoint, status, response, duration)
- Storing API response snapshots for regression testing
- Querying historical test data

## Models
- `TestRun` — Records of individual test executions
- `APISnapshot` — Response snapshots for regression comparison

## Usage Pattern
```python
from utils.database.db import TestResultDB

db = TestResultDB()
db.record_test_run(
    test_name="test_get_repo",
    endpoint="/repos/octocat/Hello-World",
    status_code=200,
    response_body={"name": "Hello-World"},
    duration_ms=150,
)
```

## Guidelines
- Use `TestResultDB` for any persistent test data tracking.
- Snapshots enable regression testing by comparing response hashes.
- The database file is gitignored (`data/test_results.db`).
