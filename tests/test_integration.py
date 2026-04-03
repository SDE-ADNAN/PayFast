from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
def test_prometheus_metrics() -> None:
    response = client.get("/metrics")
    # Prometheus text format payload comes back
    assert response.status_code == 200
    assert "http_requests" in response.text or "python_gc" in response.text
    
def test_redoc_available() -> None:
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()
    
def test_docs_available() -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
