# Adiciona os imports necessários para expor os schemas
from .token import Token, TokenData
from .empresa import Empresa, EmpresaCreate, EmpresaUpdate, EmpresaInDB
from .usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioInDB
from .crm import Board, BoardCreate, BoardUpdate, Coluna, ColunaCreate, ColunaUpdate, Card, CardCreate, CardUpdate, Tag, TagCreate, TagUpdate
from .instancia_evolution import InstanciaEvolution, InstanciaEvolutionCreate, InstanciaEvolutionUpdate, InstanciaQRCode, SendMessagePayload

# Exemplo de como usar BaseModel e Field (se necessário em outros schemas)
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Schemas Base --- (Já definidos em arquivos individuais, mas mostrando exemplo)
# class ItemBase(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None

# class ItemCreate(ItemBase):
#     title: str

# class ItemUpdate(ItemBase):
#     pass

# class ItemInDBBase(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         from_attributes = True # Renamed from orm_mode in Pydantic v2

# --- Schemas Completos --- (Já definidos em arquivos individuais)
# class Item(ItemInDBBase):
#     pass

# class ItemInDB(ItemInDBBase):
#     pass

# --- Schemas de Usuário (Exemplo já em usuario.py) ---
# class UsuarioBase(BaseModel):
#     email: Optional[EmailStr] = None
#     is_active: Optional[bool] = True
#     is_superuser: bool = False
#     nome: Optional[str] = None
#     empresa_id: Optional[int] = None
#     perfil: Optional[str] = "agente" # agente, supervisor, admin

# --- Schemas de Empresa (Exemplo já em empresa.py) ---
# class EmpresaBase(BaseModel):
#     nome: Optional[str] = None
#     plano: Optional[str] = "basico"
#     data_expiracao_plano: Optional[datetime] = None
#     configuracoes: Optional[dict] = {}
