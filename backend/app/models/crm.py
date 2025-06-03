from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

# --- CRM Models ---

class Board(Base):
    __tablename__ = "crm_boards"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    colunas = relationship("Coluna", back_populates="board", cascade="all, delete-orphan")

class Coluna(Base):
    __tablename__ = "crm_colunas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    ordem = Column(Integer, default=0) # To define column order within a board
    board_id = Column(Integer, ForeignKey("crm_boards.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    board = relationship("Board", back_populates="colunas")
    cards = relationship("Card", back_populates="coluna", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = "crm_cards"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    ordem = Column(Integer, default=0) # To define card order within a column
    coluna_id = Column(Integer, ForeignKey("crm_colunas.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False) # Denormalized for easier filtering
    # Link to conversation (optional, can be added later)
    # conversa_id = Column(Integer, ForeignKey("conversas.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    coluna = relationship("Coluna", back_populates="cards")
    # tags = relationship("Tag", secondary=card_tags, back_populates="cards") # Many-to-many for tags

# Optional: Tag model and association table for MVP
class Tag(Base):
    __tablename__ = "crm_tags"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, index=True, nullable=False)
    cor = Column(String(7), default="#FFFFFF") # Hex color code
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Association Table for Card-Tag Many-to-Many relationship
# card_tags = Table(
#     "crm_card_tags",
#     Base.metadata,
#     Column("card_id", Integer, ForeignKey("crm_cards.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("crm_tags.id"), primary_key=True),
# )

