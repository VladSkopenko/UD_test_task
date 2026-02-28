from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.app.infrastructure.websocket.manager import ws_lot_manager

router = APIRouter()


@router.websocket("/ws/lots/{lot_id}")
async def websocket_lot(websocket: WebSocket, lot_id: int):
    await ws_lot_manager.connect(websocket, lot_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_lot_manager.disconnect(websocket, lot_id)
