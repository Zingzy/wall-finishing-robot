from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.app import app
from src.models.trajectory import get_session
import pytest
from fastapi.testclient import TestClient


# Create test database
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    # Mock in-memory sqlite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with test database session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
