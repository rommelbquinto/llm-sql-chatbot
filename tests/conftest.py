import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

@pytest.fixture
def client():
    """Returns a TestClient instance for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def token():
    """Generates a JWT token with a fleet_id claim"""
    import jwt
    secret = os.getenv('JWT_SECRET', 'your_jwt_secret')
    return jwt.encode({'fleet_id': 'GBM6296G'}, secret, algorithm='HS256')
