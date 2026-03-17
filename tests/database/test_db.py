"""Unit tests for utils/database/db.py.

Validates record_test_run, save_snapshot, get_latest_snapshot, and
get_test_run_count using an in-memory SQLite database.
"""

import pytest

from utils.database.db import APISnapshot, TestResultDB, TestRun


@pytest.fixture()
def db(tmp_path):
    """Provide a fresh TestResultDB backed by a temporary SQLite file.

    Setup: Create a temporary database path.
    Action: Instantiate TestResultDB with the temp path.
    Assertions: (fixture teardown -- file is removed after each test)
    """
    db_file = str(tmp_path / "test_results.db")
    return TestResultDB(db_path=db_file)


@pytest.mark.test_database
class TestRecordTestRun:
    """Tests for TestResultDB.record_test_run."""

    def test_inserts_a_record(self, db: TestResultDB):
        """Verify that record_test_run inserts one row.

        Setup: Fresh in-memory database with zero test runs.
        Action: Call record_test_run once.
        Assertions: get_test_run_count returns 1.
        """
        # Setup
        assert db.get_test_run_count() == 0

        # Action
        db.record_test_run(
            test_name="test_example",
            endpoint="/repos/octocat/Hello-World",
            status_code=200,
        )

        # Assertions
        assert db.get_test_run_count() == 1

    def test_stores_test_name_and_endpoint(self, db: TestResultDB):
        """Verify that the stored record preserves test_name and endpoint.

        Setup: Fresh database.
        Action: Insert a record with known test_name and endpoint.
        Assertions: Querying the DB returns a row matching those values.
        """
        # Setup / Action
        db.record_test_run(
            test_name="test_get_repo",
            endpoint="/repos/octocat/Hello-World",
            status_code=200,
        )

        # Assertions -- query via SQLAlchemy directly
        with db._session_factory() as session:
            row = session.query(TestRun).first()
        assert row.test_name == "test_get_repo"
        assert row.endpoint == "/repos/octocat/Hello-World"
        assert row.status_code == 200

    def test_stores_response_body_as_json(self, db: TestResultDB):
        """Verify response_body is serialised and stored.

        Setup: Fresh database.
        Action: Insert a record with a dict response_body.
        Assertions: The stored text is the JSON-serialised body.
        """
        # Setup
        body = {"id": 1296269, "name": "Hello-World"}

        # Action
        db.record_test_run(
            test_name="test_schema",
            endpoint="/repos/octocat/Hello-World",
            status_code=200,
            response_body=body,
        )

        # Assertions
        with db._session_factory() as session:
            row = session.query(TestRun).first()
        import json
        assert json.loads(row.response_body) == body

    def test_stores_duration_ms(self, db: TestResultDB):
        """Verify duration_ms is stored correctly.

        Setup: Fresh database.
        Action: Insert a record with duration_ms=250.
        Assertions: The stored row has duration_ms=250.
        """
        # Action
        db.record_test_run(
            test_name="test_timing",
            endpoint="/users/octocat",
            status_code=200,
            duration_ms=250,
        )

        # Assertions
        with db._session_factory() as session:
            row = session.query(TestRun).first()
        assert row.duration_ms == 250

    def test_null_response_body_stored_as_none(self, db: TestResultDB):
        """Verify that omitting response_body stores NULL.

        Setup: Fresh database.
        Action: Insert a record without response_body.
        Assertions: The stored row has response_body=None.
        """
        # Action
        db.record_test_run(
            test_name="test_no_body",
            endpoint="/users/octocat",
            status_code=204,
        )

        # Assertions
        with db._session_factory() as session:
            row = session.query(TestRun).first()
        assert row.response_body is None

    def test_multiple_records_accumulate(self, db: TestResultDB):
        """Verify multiple record_test_run calls all persist.

        Setup: Fresh database.
        Action: Insert 5 records.
        Assertions: get_test_run_count returns 5.
        """
        # Action
        for i in range(5):
            db.record_test_run(
                test_name=f"test_{i}",
                endpoint=f"/endpoint/{i}",
                status_code=200,
            )

        # Assertions
        assert db.get_test_run_count() == 5


@pytest.mark.test_database
class TestSaveSnapshot:
    """Tests for TestResultDB.save_snapshot."""

    def test_inserts_snapshot(self, db: TestResultDB):
        """Verify save_snapshot inserts an APISnapshot row.

        Setup: Fresh database.
        Action: Call save_snapshot with a valid endpoint, body, and hash.
        Assertions: The snapshot can be retrieved via get_latest_snapshot.
        """
        # Setup
        endpoint = "/repos/octocat/Hello-World"
        body = {"id": 1296269, "name": "Hello-World"}
        response_hash = "abc123def456" * 4  # 48 chars, just for test

        # Action
        db.save_snapshot(endpoint=endpoint, response_body=body, response_hash=response_hash)

        # Assertions
        snapshot = db.get_latest_snapshot(endpoint)
        assert snapshot is not None
        assert snapshot.endpoint == endpoint
        assert snapshot.response_hash == response_hash

    def test_snapshot_body_stored_as_json(self, db: TestResultDB):
        """Verify the snapshot response body is JSON-serialised.

        Setup: Fresh database.
        Action: Save a snapshot with a dict body.
        Assertions: Retrieved snapshot body is the JSON of the original dict.
        """
        # Setup
        endpoint = "/users/octocat"
        body = {"login": "octocat", "id": 583231}

        # Action
        db.save_snapshot(endpoint=endpoint, response_body=body, response_hash="aabbcc" * 8)

        # Assertions
        snapshot = db.get_latest_snapshot(endpoint)
        import json
        assert json.loads(snapshot.response_body) == body


@pytest.mark.test_database
class TestGetLatestSnapshot:
    """Tests for TestResultDB.get_latest_snapshot."""

    def test_returns_none_when_no_snapshot(self, db: TestResultDB):
        """Verify get_latest_snapshot returns None for an unseen endpoint.

        Setup: Fresh database.
        Action: Query an endpoint that has no saved snapshot.
        Assertions: Result is None.
        """
        # Action
        result = db.get_latest_snapshot("/repos/nonexistent/repo")

        # Assertions
        assert result is None

    def test_returns_most_recent_snapshot(self, db: TestResultDB):
        """Verify the most recently saved snapshot is returned when multiple exist.

        Setup: Two snapshots for the same endpoint with different hashes.
        Action: Call get_latest_snapshot.
        Assertions: The hash of the returned snapshot matches the second (latest) save.
        """
        # Setup
        endpoint = "/repos/octocat/Hello-World"
        body1 = {"stars": 1000}
        body2 = {"stars": 1001}
        hash1 = "first" + "0" * 59
        hash2 = "secon" + "d" * 59

        # Action
        db.save_snapshot(endpoint=endpoint, response_body=body1, response_hash=hash1)
        db.save_snapshot(endpoint=endpoint, response_body=body2, response_hash=hash2)
        snapshot = db.get_latest_snapshot(endpoint)

        # Assertions
        assert snapshot.response_hash == hash2


@pytest.mark.test_database
class TestGetTestRunCount:
    """Tests for TestResultDB.get_test_run_count."""

    def test_returns_zero_when_empty(self, db: TestResultDB):
        """Verify an empty database returns count zero.

        Setup: Fresh database with no records.
        Action: Call get_test_run_count.
        Assertions: Returns 0.
        """
        # Action
        count = db.get_test_run_count()

        # Assertions
        assert count == 0

    def test_returns_correct_count_after_inserts(self, db: TestResultDB):
        """Verify the count reflects all inserted records.

        Setup: Fresh database.
        Action: Insert 3 records then call get_test_run_count.
        Assertions: Returns 3.
        """
        # Action
        for i in range(3):
            db.record_test_run(
                test_name=f"t{i}",
                endpoint="/test",
                status_code=200,
            )

        # Assertions
        assert db.get_test_run_count() == 3
