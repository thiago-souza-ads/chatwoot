from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.empresa import Empresa
from app.schemas import EmpresaCreate, EmpresaUpdate

class CRUDEmpresa(CRUDBase[Empresa, EmpresaCreate, EmpresaUpdate]):
    def get_by_nome(self, db: Session, *, nome: str) -> Optional[Empresa]:
        return db.query(Empresa).filter(Empresa.nome == nome).first()

    # Add other specific CRUD methods for Empresa if needed

empresa = CRUDEmpresa(Empresa)

