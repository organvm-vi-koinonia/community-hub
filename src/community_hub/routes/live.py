"""WebSocket live salon rooms — real-time discussion during active salons."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class RoomManager:
    """In-process room manager — maps room IDs to sets of active WebSocket connections."""

    def __init__(self):
        self._rooms: dict[str, set[WebSocket]] = {}

    def _room(self, room_id: str) -> set[WebSocket]:
        if room_id not in self._rooms:
            self._rooms[room_id] = set()
        return self._rooms[room_id]

    async def connect(self, room_id: str, ws: WebSocket):
        await ws.accept()
        self._room(room_id).add(ws)
        count = len(self._rooms[room_id])
        logger.info("WebSocket joined room %s (%d connected)", room_id, count)
        await self.broadcast(room_id, {
            "type": "system",
            "text": f"A participant joined. {count} connected.",
            "count": count,
        })

    async def disconnect(self, room_id: str, ws: WebSocket):
        room = self._rooms.get(room_id)
        if room:
            room.discard(ws)
            count = len(room)
            if count == 0:
                del self._rooms[room_id]
                logger.info("Room %s empty, removed", room_id)
            else:
                logger.info("WebSocket left room %s (%d remaining)", room_id, count)
                await self.broadcast(room_id, {
                    "type": "system",
                    "text": f"A participant left. {count} connected.",
                    "count": count,
                })

    async def broadcast(self, room_id: str, data: dict):
        room = self._rooms.get(room_id, set())
        dead = []
        message = json.dumps(data)
        for ws in room:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            room.discard(ws)

    def participant_count(self, room_id: str) -> int:
        return len(self._rooms.get(room_id, set()))


manager = RoomManager()


@router.get("/salons/{session_id}/live")
async def salon_live(request: Request, session_id: int):
    """Render the live salon room page."""
    templates = request.app.state.templates
    count = manager.participant_count(str(session_id))
    return templates.TemplateResponse("salons/live.html", {
        "request": request,
        "session_id": session_id,
        "participant_count": count,
    })


@router.websocket("/ws/salons/{session_id}")
async def salon_ws(websocket: WebSocket, session_id: int):
    """WebSocket endpoint for live salon participation."""
    room_id = str(session_id)
    await manager.connect(room_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue
            await manager.broadcast(room_id, {
                "type": "message",
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)
