from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        # Structure: {empresa_id: {user_id: websocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, empresa_id: int, user_id: int):
        await websocket.accept()
        if empresa_id not in self.active_connections:
            self.active_connections[empresa_id] = {}
        self.active_connections[empresa_id][user_id] = websocket

    def disconnect(self, empresa_id: int, user_id: int):
        if empresa_id in self.active_connections and user_id in self.active_connections[empresa_id]:
            del self.active_connections[empresa_id][user_id]
            if not self.active_connections[empresa_id]: # Remove empresa_id if no users left
                del self.active_connections[empresa_id]

    async def send_personal_message(self, message: str, empresa_id: int, user_id: int):
        if empresa_id in self.active_connections and user_id in self.active_connections[empresa_id]:
            websocket = self.active_connections[empresa_id][user_id]
            await websocket.send_text(message)

    async def broadcast_to_empresa(self, message: str, empresa_id: int, exclude_user_id: int = None):
        if empresa_id in self.active_connections:
            for user_id, websocket in self.active_connections[empresa_id].items():
                if exclude_user_id is None or user_id != exclude_user_id:
                    await websocket.send_text(message)

manager = ConnectionManager()

