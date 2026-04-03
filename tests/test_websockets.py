from fastapi.testclient import TestClient
from src.main import app

def test_websocket_missing_token() -> None:
    client = TestClient(app)
    # The websocket route expects ?token=...
    # Without it, or with an invalid one, it should immediately close with WS_1008_POLICY_VIOLATION
    with client.websocket_connect("/ws?token=invalid_token") as websocket:
        try:
            websocket.receive_text()
            assert False, "Should have disconnected"
        except Exception as e:
            assert "1008" in str(e) or "close" in str(e).lower()
