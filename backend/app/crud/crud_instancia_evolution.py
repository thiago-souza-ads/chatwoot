from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.instancia_evolution import InstanciaEvolution
from app.schemas.instancia_evolution import InstanciaEvolutionCreate, InstanciaEvolutionUpdate

class CRUDInstanciaEvolution(CRUDBase[InstanciaEvolution, InstanciaEvolutionCreate, InstanciaEvolutionUpdate]):
    def get_by_nome_instancia(self, db: Session, *, nome_instancia: str) -> Optional[InstanciaEvolution]:
        return db.query(self.model).filter(InstanciaEvolution.nome_instancia == nome_instancia).first()

    def get_multi_by_empresa(
        self, db: Session, *, empresa_id: int, skip: int = 0, limit: int = 100
    ) -> List[InstanciaEvolution]:
        return (
            db.query(self.model)
            .filter(InstanciaEvolution.empresa_id == empresa_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Add methods to update status, qr_code etc.
    def update_status(self, db: Session, *, db_obj: InstanciaEvolution, status: str) -> InstanciaEvolution:
        update_data = {"status_conexao": status}
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def update_qr_code(self, db: Session, *, db_obj: InstanciaEvolution, qr_code: Optional[str]) -> InstanciaEvolution:
        update_data = {"qr_code_base64": qr_code}
        return super().update(db, db_obj=db_obj, obj_in=update_data)

instancia_evolution = CRUDInstanciaEvolution(InstanciaEvolution)

