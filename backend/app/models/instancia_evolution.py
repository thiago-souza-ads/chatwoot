from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class InstanciaEvolution(Base):
    __tablename__ = "instancias_evolution"

    id = Column(Integer, primary_key=True, index=True)
    nome_instancia = Column(String(100), unique=True, index=True, nullable=False) # Unique name for the instance
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    api_key = Column(String(255), nullable=True) # Store API Key provided by Evolution API
    api_endpoint = Column(String(255), nullable=True) # Store the base URL for this instance
    status_conexao = Column(String(50), default="disconnected") # e.g., disconnected, connected, connecting, qr_code_needed
    qr_code_base64 = Column(Text, nullable=True) # Store the QR code if needed
    last_webhook_received = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean(), default=True)

    empresa = relationship("Empresa") # Add back_populates in Empresa model if needed

