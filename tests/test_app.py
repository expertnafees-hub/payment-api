import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test /health endpoint returns 200 and healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "payment-api"

def test_payment_success(client):
    """Test valid payment transaction returns 201 APPROVED"""
    response = client.post("/api/v1/payments", json={"amount": 100.0, "currency": "USD"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "APPROVED"
    assert "transaction_id" in data

def test_payment_invalid_amount(client):
    """Test invalid payment amount returns 400 Bad Request"""
    response = client.post("/api/v1/payments", json={"amount": -10.0, "currency": "USD"})
    assert response.status_code == 400
