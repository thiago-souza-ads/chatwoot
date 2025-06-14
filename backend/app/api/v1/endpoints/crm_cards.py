from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.v1.endpoints.crm_colunas import get_coluna_empresa_user # Reuse dependency

router = APIRouter()

# Dependency to check if the user belongs to the company of the card's column/board
def get_card_empresa_user(
    card_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> models.Card:
    card = crud.card.get(db, id=card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    # Check access via the coluna -> board
    coluna = crud.coluna.get(db, id=card.coluna_id)
    if not coluna:
         raise HTTPException(status_code=404, detail="Coluna associated with card not found") # Should not happen
    board = crud.board.get(db, id=coluna.board_id)
    if not board:
         raise HTTPException(status_code=404, detail="Board associated with card's coluna not found") # Should not happen

    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this card's board")
    return card

@router.get("/by_coluna/{coluna_id}", response_model=List[schemas.Card])
def read_cards_by_coluna(
    coluna: models.Coluna = Depends(get_coluna_empresa_user), # Use coluna dependency to check access
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve cards for a specific coluna. Access controlled by coluna access.
    """
    cards = crud.card.get_multi_by_coluna(db, coluna_id=coluna.id, skip=skip, limit=limit)
    return cards

@router.post("/", response_model=schemas.Card)
def create_card(
    *,
    db: Session = Depends(deps.get_db),
    card_in: schemas.CardCreate,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new card for a specific coluna. User must belong to the company.
    """
    # Obter a coluna primeiro para verificar permissões
    coluna = crud.coluna.get(db, id=card_in.coluna_id)
    if not coluna:
        raise HTTPException(status_code=404, detail="Coluna not found")
        
    # Obter o board para verificar a empresa
    board = crud.board.get(db, id=coluna.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board associated with coluna not found")
        
    # Verificar se o usuário tem acesso ao board/coluna
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this column's board")

    # Ensure the empresa_id in the input matches the board's company
    if card_in.empresa_id != board.empresa_id:
        raise HTTPException(status_code=400, detail="Card empresa_id must match the board's empresa_id")

    card = crud.card.create_with_coluna_empresa(
        db=db, obj_in=card_in, coluna_id=coluna.id, empresa_id=board.empresa_id
    )
    return card

@router.get("/{card_id}", response_model=schemas.Card)
def read_card(
    card: models.Card = Depends(get_card_empresa_user), # Checks access
) -> Any:
    """
    Get card by ID. Access controlled by dependency.
    """
    return card

@router.put("/{card_id}", response_model=schemas.Card)
def update_card(
    *,
    db: Session = Depends(deps.get_db),
    card: models.Card = Depends(get_card_empresa_user), # Checks access
    card_in: schemas.CardUpdate,
    # Any active user in the company can update a card they can access
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a card. User must belong to the company.
    Handles moving cards between columns if coluna_id is provided.
    """
    # Dependency get_card_empresa_user already checks company access

    # If moving the card, check access to the target column
    if card_in.coluna_id and card_in.coluna_id != card.coluna_id:
        target_coluna = crud.coluna.get(db, id=card_in.coluna_id)
        if not target_coluna:
            raise HTTPException(status_code=404, detail="Target coluna not found")
        target_board = crud.board.get(db, id=target_coluna.board_id)
        if not target_board:
             raise HTTPException(status_code=404, detail="Board for target coluna not found")
        if not current_user.is_superuser and target_board.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Not enough permissions for the target column's board")
        # Ensure card stays within the same company
        if target_board.empresa_id != card.empresa_id:
             raise HTTPException(status_code=400, detail="Cannot move card to a column in a different company's board")

    card = crud.card.update(db, db_obj=card, obj_in=card_in)
    return card

@router.delete("/{card_id}", response_model=schemas.Card)
def delete_card(
    *,
    db: Session = Depends(deps.get_db),
    card: models.Card = Depends(get_card_empresa_user), # Checks access
    # Any active user in the company can delete a card they can access
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a card. User must belong to the company.
    """
    # Dependency get_card_empresa_user already checks company access
    card = crud.card.remove(db, id=card.id)
    return card
