from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from pydantic import ValidationError
import jwt
from typing import Any

from src.auth.security import decode_token
from src.ws.connection_manager import manager

router = APIRouter(tags=["websockets"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)) -> None:
    try:
        payload = decode_token(token)
        user_id = str(payload.get("sub"))
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except (jwt.PyJWTError, ValidationError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # ping/pong keepalive automatically handled natively by uvicorn/websockets
            # we just wait for data here. If client drops, it will raise WebSocketDisconnect
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
