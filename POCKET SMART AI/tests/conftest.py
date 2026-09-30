import os


os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

os.environ["SECRET_KEY"] = "test-secret"


from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client