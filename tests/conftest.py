"""
Pytest configuration and fixtures for amendment system tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.app.database import Base
from backend.app import models


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite database engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_amendment_data():
    """Sample data for creating an amendment"""
    return {
        "amendment_reference": "AMN-2024-001",
        "amendment_type": models.AmendmentType.FEATURE,
        "description": "Test amendment description",
        "amendment_status": models.AmendmentStatus.OPEN,
        "development_status": models.DevelopmentStatus.NOT_STARTED,
        "priority": models.Priority.MEDIUM,
        "reported_by": "Test User",
        "assigned_to": "Developer 1",
        "date_reported": datetime(2024, 1, 1, 10, 0, 0),
    }


@pytest.fixture
def sample_amendment(test_session, sample_amendment_data):
    """Create and return a sample amendment"""
    amendment = models.Amendment(**sample_amendment_data)
    test_session.add(amendment)
    test_session.commit()
    test_session.refresh(amendment)
    return amendment
