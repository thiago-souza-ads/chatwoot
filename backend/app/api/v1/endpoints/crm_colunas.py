from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.v1.endpoints.crm_boards import get_board_empresa_user # Reuse dependency

router = APIRouter()

# Dependency to check if the user belongs to the company of the column's board
def get_coluna_empresa_user(
    coluna_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> models.Coluna:
    coluna = crud.coluna.get(db, id=coluna_id)
    if not coluna:
        raise HTTPException(status_code=404, detail="Coluna not found")
    # Check access via the board
    board = crud.board.get(db, id=coluna.board_id)
    if not board:
         raise HTTPException(status_code=404, detail="Board associated with coluna not found") # Should not happen
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this column's board")
    return coluna

@router.get("/by_board/{board_id}", response_model=List[schemas.Coluna])
def read_colunas_by_board(
    board: models.Board = Depends(get_board_empresa_user), # Use board dependency to check access
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve colunas for a specific board. Access controlled by board access.
    """
    colunas = crud.coluna.get_multi_by_board(db, board_id=board.id, skip=skip, limit=limit)
    return colunas

@router.post("/", response_model=schemas.Coluna)
def create_coluna(
    *,
    db: Session = Depends(deps.get_db),
    coluna_in: schemas.ColunaCreate,
    # Ensure user has access to the board they are adding a column to
    board: models.Board = Depends(lambda coluna_in=coluna_in: get_board_empresa_user(board_id=coluna_in.board_id)),
    # Check if user has permission to modify the board (e.g., supervisor/admin)
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Create new coluna for a specific board. Requires supervisor/superuser privileges for the board.
    """
     # Extra check: ensure the supervisor/superuser belongs to the board's company if not superuser
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions for this board")

    coluna = crud.coluna.create_with_board(db=db, obj_in=coluna_in, board_id=board.id)
    return coluna

@router.get("/{coluna_id}", response_model=schemas.Coluna)
def read_coluna(
    coluna: models.Coluna = Depends(get_coluna_empresa_user), # Checks access
) -> Any:
    """
    Get coluna by ID. Access controlled by dependency.
    """
    return coluna

@router.put("/{coluna_id}", response_model=schemas.Coluna)
def update_coluna(
    *,
    db: Session = Depends(deps.get_db),
    coluna: models.Coluna = Depends(get_coluna_empresa_user), # Checks access
    coluna_in: schemas.ColunaUpdate,
    # Check if user has permission to modify the board (e.g., supervisor/admin)
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Update a coluna. Requires supervisor/superuser privileges for the board.
    """
    # Extra check: ensure the supervisor/superuser belongs to the board's company if not superuser
    board = crud.board.get(db, id=coluna.board_id) # Get board for company check
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions for this board")

    coluna = crud.coluna.update(db, db_obj=coluna, obj_in=coluna_in)
    return coluna

@router.delete("/{coluna_id}", response_model=schemas.Coluna)
def delete_coluna(
    *,
    db: Session = Depends(deps.get_db),
    coluna: models.Coluna = Depends(get_coluna_empresa_user), # Checks access
    # Check if user has permission to modify the board (e.g., supervisor/admin)
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Delete a coluna. Requires supervisor/superuser privileges for the board.
    """
     # Extra check: ensure the supervisor/superuser belongs to the board's company if not superuser
    board = crud.board.get(db, id=coluna.board_id) # Get board for company check
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions for this board")

    coluna = crud.coluna.remove(db, id=coluna.id)
    return coluna

