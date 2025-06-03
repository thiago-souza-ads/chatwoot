from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

# Dependency to check if the user belongs to the company of the board
def get_board_empresa_user(
    board_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> models.Board:
    board = crud.board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this board")
    return board

@router.get("/", response_model=List[schemas.Board])
def read_boards(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve boards for the user's company.
    Superusers can see all boards (consider adding a filter for this).
    """
    if current_user.is_superuser:
        # Decide if superuser should see all boards or needs a filter
        # For now, let's restrict to their non-existent company or require filter
        # Or maybe return all boards? Let's return all for now.
        boards = crud.board.get_multi(db, skip=skip, limit=limit)
    elif current_user.empresa_id:
        boards = crud.board.get_multi_by_empresa(
            db, empresa_id=current_user.empresa_id, skip=skip, limit=limit
        )
    else:
        boards = [] # User without company (shouldn't happen unless superuser)
    return boards

@router.post("/", response_model=schemas.Board)
def create_board(
    *,
    db: Session = Depends(deps.get_db),
    board_in: schemas.BoardCreate,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new board for the user's company.
    Superusers can specify empresa_id, others use their own.
    """
    if not current_user.is_superuser:
        if not current_user.empresa_id:
             raise HTTPException(status_code=400, detail="User does not belong to a company")
        # Force board to be created for the user's company
        board_in.empresa_id = current_user.empresa_id
    else:
        # Superuser must specify empresa_id
        if not board_in.empresa_id:
            raise HTTPException(status_code=400, detail="Superuser must specify empresa_id to create a board")
        # Verify company exists
        empresa = crud.empresa.get(db, id=board_in.empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail=f"Empresa with id {board_in.empresa_id} not found.")

    board = crud.board.create(db=db, obj_in=board_in)
    return board

@router.get("/{board_id}", response_model=schemas.Board)
def read_board(
    board: models.Board = Depends(get_board_empresa_user),
) -> Any:
    """
    Get board by ID. Access controlled by dependency.
    """
    return board

@router.put("/{board_id}", response_model=schemas.Board)
def update_board(
    *,
    db: Session = Depends(deps.get_db),
    board: models.Board = Depends(get_board_empresa_user), # Ensures user has access
    board_in: schemas.BoardUpdate,
    # Add check: Only admin/supervisor of the company or superuser can update?
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Update a board. Requires supervisor/superuser privileges within the company.
    """
    # Extra check: ensure the supervisor/superuser belongs to the board's company if not superuser
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions for this board")

    board = crud.board.update(db, db_obj=board, obj_in=board_in)
    return board

@router.delete("/{board_id}", response_model=schemas.Board)
def delete_board(
    *,
    db: Session = Depends(deps.get_db),
    board: models.Board = Depends(get_board_empresa_user), # Ensures user has access
    # Add check: Only admin/supervisor of the company or superuser can delete?
    current_user: models.Usuario = Depends(deps.get_current_active_supervisor_or_superuser),
) -> Any:
    """
    Delete a board. Requires supervisor/superuser privileges within the company.
    """
    # Extra check: ensure the supervisor/superuser belongs to the board's company if not superuser
    if not current_user.is_superuser and board.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions for this board")

    board = crud.board.remove(db, id=board.id)
    return board

