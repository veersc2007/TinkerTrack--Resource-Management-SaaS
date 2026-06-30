import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "🏢 TinkerTrack"
    assert response.json()["status"] == "running"


def test_docs():
    """Test API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc():
    """Test ReDoc documentation is available"""
    response = client.get("/redoc")
    assert response.status_code == 200
