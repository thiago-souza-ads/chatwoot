from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.services.websocket_manager import manager
from app.api import deps
from app import models, schemas

router = APIRouter()

@router.websocket("/ws/{empresa_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    empresa_id: int,
    user_id: int,
    # Optional: Add token validation to the WebSocket connection
    # token: str = Query(...),
    # db: Session = Depends(deps.get_db) # If needed for validation
):
    # Optional: Validate token and user access here before connecting
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    #     token_data = schemas.TokenData(**payload)
    #     if token_data.empresa_id != empresa_id or token_data.user_id != user_id:
    #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #         return
    #     user = crud.usuario.get(db, id=user_id)
    #     if not user or not crud.usuario.is_active(user):
    #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #         return
    # except (JWTError, ValidationError):
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return

    await manager.connect(websocket, empresa_id, user_id)
    # Notify others in the company (optional)
    # await manager.broadcast_to_empresa(json.dumps({"type": "user_connect", "user_id": user_id}), empresa_id, exclude_user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process received message (e.g., chat message)
            # For MVP, we might just broadcast or handle specific commands
            message_data = json.loads(data)
            # Example: Broadcasting a chat message to the same company
            if message_data.get("type") == "chat_message":
                await manager.broadcast_to_empresa(
                    json.dumps({
                        "type": "chat_message",
                        "sender_id": user_id,
                        "content": message_data.get("content", "")
                    }),
                    empresa_id,
                    # exclude_user_id=user_id # Don't exclude sender if they need to see their own message
                )
            else:
                 # Send confirmation back to sender or handle other types
                 await manager.send_personal_message(f"Message received: {data}", empresa_id, user_id)

    except WebSocketDisconnect:
        manager.disconnect(empresa_id, user_id)
        # Notify others (optional)
        # await manager.broadcast_to_empresa(json.dumps({"type": "user_disconnect", "user_id": user_id}), empresa_id)

