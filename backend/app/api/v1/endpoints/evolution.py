from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
import requests # To interact with Evolution API
import json
import logging

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.services.websocket_manager import manager # To potentially notify frontend

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to check if the user belongs to the company of the instancia
def get_instancia_empresa_user(
    instancia_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> models.InstanciaEvolution:
    instancia = crud.instancia_evolution.get(db, id=instancia_id)
    if not instancia:
        raise HTTPException(status_code=404, detail="Instancia Evolution not found")
    if not current_user.is_superuser and instancia.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this instancia")
    return instancia

@router.get("/", response_model=List[schemas.InstanciaEvolution])
def read_instancias(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve instancias Evolution for the user's company.
    """
    if current_user.is_superuser:
        # Decide if superuser should see all instancias or needs a filter
        instancias = crud.instancia_evolution.get_multi(db, skip=skip, limit=limit)
    elif current_user.empresa_id:
        instancias = crud.instancia_evolution.get_multi_by_empresa(
            db, empresa_id=current_user.empresa_id, skip=skip, limit=limit
        )
    else:
        instancias = [] # User without company
    return instancias

@router.post("/", response_model=schemas.InstanciaEvolution)
def create_instancia(
    *,
    db: Session = Depends(deps.get_db),
    instancia_in: schemas.InstanciaEvolutionCreate,
    # Only admin/supervisor or superuser can create instances
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Create new Instancia Evolution for the user's company.
    Requires supervisor/superuser privileges.
    """
    if not current_user.is_superuser:
        if not current_user.empresa_id:
             raise HTTPException(status_code=400, detail="User does not belong to a company")
        # Force instancia to be created for the user's company
        instancia_in.empresa_id = current_user.empresa_id
    else:
        # Superuser must specify empresa_id
        if not instancia_in.empresa_id:
            raise HTTPException(status_code=400, detail="Superuser must specify empresa_id to create an instancia")
        empresa = crud.empresa.get(db, id=instancia_in.empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail=f"Empresa with id {instancia_in.empresa_id} not found.")

    # Check if name is unique (optional, but recommended)
    existing = crud.instancia_evolution.get_by_nome_instancia(db, nome_instancia=instancia_in.nome_instancia)
    if existing:
        raise HTTPException(status_code=400, detail="Instancia with this name already exists.")

    # Here you might want to immediately try to connect to the Evolution API
    # instance based on the provided endpoint/key, or wait for user action.
    # For MVP, let's just create the record.
    instancia = crud.instancia_evolution.create(db=db, obj_in=instancia_in)
    return instancia

@router.get("/{instancia_id}", response_model=schemas.InstanciaEvolution)
def read_instancia(
    instancia: models.InstanciaEvolution = Depends(get_instancia_empresa_user), # Checks access
) -> Any:
    """
    Get instancia by ID. Access controlled by dependency.
    """
    return instancia

@router.put("/{instancia_id}", response_model=schemas.InstanciaEvolution)
def update_instancia(
    *,
    db: Session = Depends(deps.get_db),
    instancia: models.InstanciaEvolution = Depends(get_instancia_empresa_user), # Checks access
    instancia_in: schemas.InstanciaEvolutionUpdate,
    # Only admin/supervisor or superuser can update
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Update an instancia. Requires supervisor/superuser privileges.
    """
    # Check if name is being changed and if it conflicts
    if instancia_in.nome_instancia and instancia_in.nome_instancia != instancia.nome_instancia:
        existing = crud.instancia_evolution.get_by_nome_instancia(db, nome_instancia=instancia_in.nome_instancia)
        if existing:
            raise HTTPException(status_code=400, detail="Instancia with this name already exists.")

    instancia = crud.instancia_evolution.update(db, db_obj=instancia, obj_in=instancia_in)
    return instancia

@router.delete("/{instancia_id}", response_model=schemas.InstanciaEvolution)
def delete_instancia(
    *,
    db: Session = Depends(deps.get_db),
    instancia: models.InstanciaEvolution = Depends(get_instancia_empresa_user), # Checks access
    # Only admin/supervisor or superuser can delete
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Delete an instancia. Requires supervisor/superuser privileges.
    (Consider disconnecting from Evolution API first if connected)
    """
    # Optional: Add logic to disconnect from Evolution API before deleting
    instancia = crud.instancia_evolution.remove(db, id=instancia.id)
    return instancia

# --- Evolution API Interaction Endpoints ---

@router.post("/{instancia_id}/connect", response_model=schemas.InstanciaEvolutionQRCode)
def connect_instancia(
    *,
    db: Session = Depends(deps.get_db),
    instancia: models.InstanciaEvolution = Depends(get_instancia_empresa_user),
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Initiate connection to Evolution API instance and get QR Code if needed.
    Requires supervisor/superuser privileges.
    """
    if not instancia.api_endpoint or not instancia.api_key:
        raise HTTPException(status_code=400, detail="API Endpoint or API Key not configured for this instancia.")

    # Update status locally
    crud.instancia_evolution.update_status(db, db_obj=instancia, status="connecting")
    crud.instancia_evolution.update_qr_code(db, db_obj=instancia, qr_code=None) # Clear old QR

    # Call Evolution API to create/connect instance
    evolution_url = f"{str(instancia.api_endpoint).rstrip('/')}/instance/connect/{instancia.nome_instancia}"
    headers = {"apikey": instancia.api_key}

    try:
        response = requests.post(evolution_url, headers=headers, timeout=30)
        response.raise_for_status() # Raise exception for bad status codes
        data = response.json()

        qr_code = data.get("base64")
        status = "qr_code_needed" if qr_code else "connected" # Assume connected if no QR

        # Update local status and QR code
        crud.instancia_evolution.update_status(db, db_obj=instancia, status=status)
        crud.instancia_evolution.update_qr_code(db, db_obj=instancia, qr_code=qr_code)

        # Notify frontend via WebSocket (optional)
        # await manager.broadcast_to_empresa(json.dumps({"type": "instance_status", "instance_id": instancia.id, "status": status, "qr_code": qr_code}), instancia.empresa_id)

        return {"qr_code": qr_code, "status": status}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Evolution API for instance {instancia.nome_instancia}: {e}")
        crud.instancia_evolution.update_status(db, db_obj=instancia, status="connection_error")
        raise HTTPException(status_code=503, detail=f"Failed to connect to Evolution API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Evolution connection for instance {instancia.nome_instancia}: {e}")
        crud.instancia_evolution.update_status(db, db_obj=instancia, status="error")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/{instancia_id}/send", status_code=202) # Accepted
def send_message(
    *,
    db: Session = Depends(deps.get_db),
    instancia: models.InstanciaEvolution = Depends(get_instancia_empresa_user),
    payload: schemas.SendMessagePayload,
    current_user: models.Usuario = Depends(deps.get_current_active_user), # Any active user can send
) -> Any:
    """
    Send a message using the specified Evolution API instance.
    """
    if not instancia.api_endpoint or not instancia.api_key or instancia.status_conexao != "connected":
        raise HTTPException(status_code=400, detail="Instancia not configured or not connected.")

    evolution_url = f"{str(instancia.api_endpoint).rstrip('/')}/message/sendText/{instancia.nome_instancia}"
    headers = {"apikey": instancia.api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(evolution_url, headers=headers, json=payload.dict(), timeout=15)
        response.raise_for_status()
        # Log success or handle response if needed
        logger.info(f"Message sent via instance {instancia.nome_instancia} to {payload.number}")
        return {"status": "Message sent request accepted"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message via Evolution API for instance {instancia.nome_instancia}: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to send message via Evolution API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending message for instance {instancia.nome_instancia}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# --- Webhook Endpoint ---
# This endpoint should be configured in the Evolution API instance settings
@router.post("/webhook/{instancia_nome}", include_in_schema=False) # Hide from OpenAPI docs
async def evolution_webhook(
    instancia_nome: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle incoming webhooks from a specific Evolution API instance.
    """
    payload = await request.json()
    logger.info(f"Webhook received for instance {instancia_nome}: {json.dumps(payload)}")

    # Find the corresponding instancia in our DB
    instancia = crud.instancia_evolution.get_by_nome_instancia(db, nome_instancia=instancia_nome)
    if not instancia:
        logger.error(f"Webhook received for unknown instance: {instancia_nome}")
        # Return 200 to Evolution so it doesn't retry, but log the error
        return {"status": "Instance not found"}

    # Update last webhook received time
    crud.instancia_evolution.update(db, db_obj=instancia, obj_in={"last_webhook_received": datetime.utcnow()})

    # Process the webhook payload based on its type
    event_type = payload.get("event")

    if event_type == "connection.update":
        new_status = payload.get("data", {}).get("state", "disconnected")
        crud.instancia_evolution.update_status(db, db_obj=instancia, status=new_status)
        crud.instancia_evolution.update_qr_code(db, db_obj=instancia, qr_code=None) # Clear QR on status update
        logger.info(f"Instance {instancia_nome} status updated to: {new_status}")
        # Notify frontend via WebSocket
        await manager.broadcast_to_empresa(json.dumps({
            "type": "instance_status",
            "instance_id": instancia.id,
            "status": new_status
        }), instancia.empresa_id)

    elif event_type == "qrcode.updated":
        qr_code = payload.get("data", {}).get("qrcode", {}).get("base64")
        crud.instancia_evolution.update_status(db, db_obj=instancia, status="qr_code_needed")
        crud.instancia_evolution.update_qr_code(db, db_obj=instancia, qr_code=qr_code)
        logger.info(f"Instance {instancia_nome} QR code updated.")
        # Notify frontend via WebSocket
        await manager.broadcast_to_empresa(json.dumps({
            "type": "instance_status",
            "instance_id": instancia.id,
            "status": "qr_code_needed",
            "qr_code": qr_code
        }), instancia.empresa_id)

    elif event_type == "messages.upsert":
        messages = payload.get("data", [])
        for message in messages:
            # Process incoming message
            # 1. Identify sender number (e.g., message.get('key', {}).get('remoteJid'))
            # 2. Get message content (e.g., message.get('message', {}).get('conversation'))
            # 3. Find or create contact in CRM
            # 4. Create new conversation or append to existing one
            # 5. Store the message in the database
            # 6. Notify relevant agents via WebSocket
            logger.info(f"Received message for instance {instancia_nome}: {message.get('key', {}).get('remoteJid')} - {message.get('message', {}).get('conversation')}")
            # --- Placeholder for message processing logic --- #
            sender_jid = message.get('key', {}).get('remoteJid')
            content = message.get('message', {}).get('conversation')
            if sender_jid and content:
                await manager.broadcast_to_empresa(json.dumps({
                    "type": "new_message",
                    "instance_id": instancia.id,
                    "sender": sender_jid,
                    "content": content
                    # Add more message details as needed
                }), instancia.empresa_id)
            # --- End Placeholder --- #

    # Add handling for other event types as needed (e.g., message acknowledgements)

    return {"status": "Webhook received"}

