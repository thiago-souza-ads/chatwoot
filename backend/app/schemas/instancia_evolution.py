from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
from datetime import datetime

# --- InstanciaEvolution Schemas ---
class InstanciaEvolutionBase(BaseModel):
    nome_instancia: str
    api_key: Optional[str] = None
    api_endpoint: Optional[HttpUrl] = None # Validate URL format
    is_active: Optional[bool] = True

class InstanciaEvolutionCreate(InstanciaEvolutionBase):
    empresa_id: int # Must be specified on creation
    # Maybe get api_key/endpoint from user input or config?

class InstanciaEvolutionUpdate(BaseModel): # Allow partial updates
    nome_instancia: Optional[str] = None
    api_key: Optional[str] = None
    api_endpoint: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    status_conexao: Optional[str] = None
    qr_code_base64: Optional[str] = None
    last_webhook_received: Optional[datetime] = None

class InstanciaEvolutionInDBBase(InstanciaEvolutionBase):
    id: int
    empresa_id: int
    status_conexao: str
    qr_code_base64: Optional[str] = None
    last_webhook_received: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Atualizado de orm_mode para from_attributes

# Schema for returning InstanciaEvolution in API
class InstanciaEvolution(InstanciaEvolutionInDBBase):
    pass

# Schema for QR Code response
class InstanciaQRCode(BaseModel):
    qr_code: Optional[str] = None
    status: str

# Schema for sending message via Evolution
class SendMessagePayload(BaseModel):
    number: str
    textMessage: Dict[str, str]
    # Add other message types as needed (media, etc.)
