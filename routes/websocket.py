from fastapi import APIRouter, Body, WebSocket, WebSocketDisconnect
from websocket_manager import manager
from db.connection import get_connection
from pydantic import BaseModel


router = APIRouter()



@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(user_id)