from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Tag Schemas ---
class TagBase(BaseModel):
    nome: str
    cor: Optional[str] = "#FFFFFF"

class TagCreate(TagBase):
    empresa_id: int # Must be specified on creation

class TagUpdate(TagBase):
    nome: Optional[str] = None
    cor: Optional[str] = None

class TagInDBBase(TagBase):
    id: int
    empresa_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Tag(TagInDBBase):
    pass

# --- Card Schemas ---
class CardBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    ordem: Optional[int] = 0

class CardCreate(CardBase):
    coluna_id: int
    empresa_id: int # Must be specified on creation

class CardUpdate(CardBase):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    ordem: Optional[int] = None
    coluna_id: Optional[int] = None # Allow moving card between columns

class CardInDBBase(CardBase):
    id: int
    coluna_id: int
    empresa_id: int
    created_at: datetime
    updated_at: datetime
    # tags: List[Tag] = [] # Add if implementing tag association in MVP

    class Config:
        orm_mode = True

class Card(CardInDBBase):
    pass

# --- Coluna Schemas ---
class ColunaBase(BaseModel):
    nome: str
    ordem: Optional[int] = 0

class ColunaCreate(ColunaBase):
    board_id: int

class ColunaUpdate(ColunaBase):
    nome: Optional[str] = None
    ordem: Optional[int] = None

class ColunaInDBBase(ColunaBase):
    id: int
    board_id: int
    created_at: datetime
    updated_at: datetime
    cards: List[Card] = [] # Include cards in column response

    class Config:
        orm_mode = True

class Coluna(ColunaInDBBase):
    pass

# --- Board Schemas ---
class BoardBase(BaseModel):
    nome: str

class BoardCreate(BoardBase):
    empresa_id: int # Must be specified on creation

class BoardUpdate(BoardBase):
    nome: Optional[str] = None

class BoardInDBBase(BoardBase):
    id: int
    empresa_id: int
    created_at: datetime
    updated_at: datetime
    colunas: List[Coluna] = [] # Include columns in board response

    class Config:
        orm_mode = True

class Board(BoardInDBBase):
    pass

