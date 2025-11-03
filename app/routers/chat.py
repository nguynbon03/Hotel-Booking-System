from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.websocket_manager import ws_manager
from app.core.redis import publish_message
from app.core.logger import logger

router = APIRouter(prefix="/ws", tags=["chat"])

@router.websocket("/support")
async def ws_support(websocket: WebSocket, room: str = Query("lobby")):
    await ws_manager.connect(websocket, room)
    try:
        await ws_manager.broadcast(room, "🟢 A user joined the chat")
        while True:
            text = await websocket.receive_text()
            await ws_manager.broadcast(room, text)
            publish_message(f"chat:{room}", text)  # nếu muốn pub/sub
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room)
        await ws_manager.broadcast(room, "🔴 A user left")
        logger.info("WS disconnected")
