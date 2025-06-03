from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False) # Superadmin da plataforma
    is_supervisor = Column(Boolean(), default=False) # Supervisor dentro da empresa
    # is_admin - implicitamente, o primeiro usuário criado para uma empresa ou um usuário com permissões elevadas

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True) # Nullable para superadmin
    empresa = relationship("Empresa", back_populates="usuarios")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

