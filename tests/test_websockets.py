from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from src.main import app
import pytest

def test_websocket_missing_token() -> None:
    client = TestClient(app)
    # The websocket route expects ?token=...
    # Without it, or with an invalid one, it should immediately close with WS_1008_POLICY_VIOLATION 
    # and Starlette's TestClient actively throws WebSocketDisconnect.
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token=invalid_token"):
            pass
    assert exc_info.value.code == 1008
