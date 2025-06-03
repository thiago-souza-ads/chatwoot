from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.crm import Tag
from app.schemas.crm import TagCreate, TagUpdate

class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    def get_by_nome_and_empresa(
        self, db: Session, *, nome: str, empresa_id: int
    ) -> Optional[Tag]:
        return (
            db.query(self.model)
            .filter(Tag.nome == nome, Tag.empresa_id == empresa_id)
            .first()
        )

    def get_multi_by_empresa(
        self, db: Session, *, empresa_id: int, skip: int = 0, limit: int = 100
    ) -> List[Tag]:
        return (
            db.query(self.model)
            .filter(Tag.empresa_id == empresa_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

tag = CRUDTag(Tag)

