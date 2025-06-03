from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import asc, func

from app.crud.base import CRUDBase
from app.models.crm import Card
from app.schemas.crm import CardCreate, CardUpdate

class CRUDCard(CRUDBase[Card, CardCreate, CardUpdate]):
    def get_multi_by_coluna(
        self, db: Session, *, coluna_id: int, skip: int = 0, limit: int = 100
    ) -> List[Card]:
        return (
            db.query(self.model)
            .filter(Card.coluna_id == coluna_id)
            .order_by(asc(Card.ordem))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_coluna_empresa(
        self, db: Session, *, obj_in: CardCreate, coluna_id: int, empresa_id: int
    ) -> Card:
        # Calculate next order value for the new card within the column
        max_order = db.query(func.max(Card.ordem)).filter(Card.coluna_id == coluna_id).scalar()
        next_order = (max_order or 0) + 1

        obj_in_data = obj_in.dict()
        obj_in_data["coluna_id"] = coluna_id
        obj_in_data["empresa_id"] = empresa_id # Ensure empresa_id is set
        obj_in_data["ordem"] = next_order
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Optional: Add method to update card order within or between columns

card = CRUDCard(Card)

