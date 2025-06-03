from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Schema base para usuário
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_supervisor: Optional[bool] = False
    empresa_id: Optional[int] = None

# Schema para criação de usuário
class UsuarioCreate(UsuarioBase):
    password: str

# Schema para atualização de usuário
class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_supervisor: Optional[bool] = None
    empresa_id: Optional[int] = None

# Schema para resposta de usuário
class Usuario(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Schema para usuário no banco de dados
class UsuarioInDB(Usuario):
    hashed_password: str
