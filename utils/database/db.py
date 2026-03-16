"""SQLite-backed test result tracker.

Provides a lightweight database for storing API response snapshots,
test run metadata, and regression baselines. Mirrors the pattern of
the production framework's PostgreSQL-backed verification layer.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class TestRun(Base):
    """Record of a single test execution."""

    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(String(500), nullable=False)
    endpoint = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_body = Column(Text)
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration_ms = Column(Integer)


class APISnapshot(Base):
    """Snapshot of an API response for regression comparison."""

    __tablename__ = "api_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(500), nullable=False, index=True)
    response_hash = Column(String(64), nullable=False)
    response_body = Column(Text, nullable=False)
    captured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TestResultDB:
    """Facade for test-result database operations."""

    def __init__(self, db_path: str = "data/test_results.db") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self._session_factory = sessionmaker(bind=self.engine)
        logger.info("TestResultDB initialized: %s", db_path)

    def record_test_run(
        self,
        test_name: str,
        endpoint: str,
        status_code: int,
        response_body: dict | list | None = None,
        duration_ms: int | None = None,
    ) -> None:
        """Insert a test-run record."""
        with self._session_factory() as session:
            run = TestRun(
                test_name=test_name,
                endpoint=endpoint,
                status_code=status_code,
                response_body=json.dumps(response_body) if response_body else None,
                duration_ms=duration_ms,
            )
            session.add(run)
            session.commit()

    def save_snapshot(self, endpoint: str, response_body: dict | list, response_hash: str) -> None:
        """Save an API response snapshot for regression testing."""
        with self._session_factory() as session:
            snapshot = APISnapshot(
                endpoint=endpoint,
                response_hash=response_hash,
                response_body=json.dumps(response_body),
            )
            session.add(snapshot)
            session.commit()

    def get_latest_snapshot(self, endpoint: str) -> APISnapshot | None:
        """Retrieve the most recent snapshot for an endpoint."""
        with self._session_factory() as session:
            return (
                session.query(APISnapshot)
                .filter_by(endpoint=endpoint)
                .order_by(APISnapshot.captured_at.desc())
                .first()
            )

    def get_test_run_count(self) -> int:
        """Return total number of recorded test runs."""
        with self._session_factory() as session:
            return session.query(TestRun).count()
