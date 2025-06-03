from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Shared properties
class EmpresaBase(BaseModel):
    nome: Optional[str] = None
    plano: Optional[str] = "basico" # Ex: basico, pro, enterprise
    data_expiracao_plano: Optional[datetime] = None
    configuracoes: Optional[Dict[str, Any]] = {}
    is_active: Optional[bool] = True

# Properties to receive on item creation
class EmpresaCreate(EmpresaBase):
    nome: str

# Properties to receive on item update
class EmpresaUpdate(EmpresaBase):
    pass

# Properties shared by models stored in DB
class EmpresaInDBBase(EmpresaBase):
    id: int
    nome: str
    is_active: bool

    class Config:
        from_attributes = True # Pydantic v2 replacement for orm_mode

# Properties to return to client
class Empresa(EmpresaInDBBase):
    pass

# Properties properties stored in DB
class EmpresaInDB(EmpresaInDBBase):
    pass

