from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import asc, func

from app.crud.base import CRUDBase
from app.models.crm import Coluna
from app.schemas.crm import ColunaCreate, ColunaUpdate

class CRUDColuna(CRUDBase[Coluna, ColunaCreate, ColunaUpdate]):
    def get_multi_by_board(
        self, db: Session, *, board_id: int, skip: int = 0, limit: int = 100
    ) -> List[Coluna]:
        return (
            db.query(self.model)
            .filter(Coluna.board_id == board_id)
            .order_by(asc(Coluna.ordem))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_board(self, db: Session, *, obj_in: ColunaCreate, board_id: int) -> Coluna:
        # Calculate next order value for the new column within the board
        max_order = db.query(func.max(Coluna.ordem)).filter(Coluna.board_id == board_id).scalar()
        next_order = (max_order or 0) + 1

        obj_in_data = obj_in.dict()
        obj_in_data['board_id'] = board_id
        obj_in_data['ordem'] = next_order
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

coluna = CRUDColuna(Coluna)

