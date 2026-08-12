import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Maps channel type (e.g. "chat", "agent", "notifications") to conversation/user IDs and their sockets
        self.active_connections: Dict[str, Dict[str, List[WebSocket]]] = {
            "chat": {},         # conversation_id -> List[WebSocket]
            "agent": {},        # agent_id -> List[WebSocket]
            "notifications": {} # user_id -> List[WebSocket]
        }

    async def connect(self, websocket: WebSocket, channel: str, identifier: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = {}
        
        if identifier not in self.active_connections[channel]:
            self.active_connections[channel][identifier] = []
            
        self.active_connections[channel][identifier].append(websocket)
        logger.info(f"WebSocket connected: [{channel}] {identifier}")

    def disconnect(self, websocket: WebSocket, channel: str, identifier: str):
        if channel in self.active_connections and identifier in self.active_connections[channel]:
            if websocket in self.active_connections[channel][identifier]:
                self.active_connections[channel][identifier].remove(websocket)
                if not self.active_connections[channel][identifier]:
                    del self.active_connections[channel][identifier]
                logger.info(f"WebSocket disconnected: [{channel}] {identifier}")

    async def broadcast_to_channel(self, channel: str, identifier: str, message: dict):
        if channel in self.active_connections and identifier in self.active_connections[channel]:
            for connection in self.active_connections[channel][identifier]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to websocket on channel {channel}: {e}")

websocket_manager = WebSocketManager()
