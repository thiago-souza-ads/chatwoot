from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.crud.base import CRUDBase
from app.models.crm import Board
from app.schemas.crm import BoardCreate, BoardUpdate

class CRUDBoard(CRUDBase[Board, BoardCreate, BoardUpdate]):
    def get_multi_by_empresa(
        self, db: Session, *, empresa_id: int, skip: int = 0, limit: int = 100
    ) -> List[Board]:
        return (
            db.query(self.model)
            .filter(Board.empresa_id == empresa_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

board = CRUDBoard(Board)

