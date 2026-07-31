from collections.abc import Generator
from secrets import token_urlsafe

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from opspilot.api.auth import create_dev_token
from opspilot.config import get_settings
from opspilot.db.base import Base
from opspilot.db.seed import seed_users
from opspilot.db.session import get_db
from opspilot.main import create_app


@pytest.fixture(autouse=True)
def development_settings(monkeypatch):
    monkeypatch.setenv("OPSPILOT_ENV", "development")
    monkeypatch.setenv("OPSPILOT_DEV_TOKEN_SECRET", token_urlsafe(32))
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    with TestingSession() as session:
        seed_users(session)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app = create_app(initialize_database=False)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def auth_headers():
    return lambda user_id: {"Authorization": f"Bearer {create_dev_token(user_id)}"}
