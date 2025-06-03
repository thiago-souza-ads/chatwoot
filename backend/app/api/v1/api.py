from fastapi import APIRouter

from app.api.v1.endpoints import (
    login,
    usuarios,
    empresas,
    websocket,
    crm_boards,
    crm_colunas,
    crm_cards,
    crm_tags,
    evolution # Add evolution
)

api_router = APIRouter()

# Core
api_router.include_router(login.router, tags=["login"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(empresas.router, prefix="/empresas", tags=["empresas"])

# WebSocket
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# CRM
api_router.include_router(crm_boards.router, prefix="/crm/boards", tags=["crm-boards"])
api_router.include_router(crm_colunas.router, prefix="/crm/colunas", tags=["crm-colunas"])
api_router.include_router(crm_cards.router, prefix="/crm/cards", tags=["crm-cards"])
api_router.include_router(crm_tags.router, prefix="/crm/tags", tags=["crm-tags"])

# Integrations
api_router.include_router(evolution.router, prefix="/evolution", tags=["evolution-api"]) # Include Evolution API router

