from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Empresa])
def read_empresas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve empresas (Superuser only).
    """
    empresas = crud.empresa.get_multi(db, skip=skip, limit=limit)
    return empresas

@router.post("/", response_model=schemas.Empresa)
def create_empresa(
    *,
    db: Session = Depends(deps.get_db),
    empresa_in: schemas.EmpresaCreate,
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new empresa (Superuser only).
    """
    # Optional: Check if empresa name already exists
    # empresa = crud.empresa.get_by_nome(db, nome=empresa_in.nome)
    # if empresa:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Empresa with this name already exists.",
    #     )
    empresa = crud.empresa.create(db=db, obj_in=empresa_in)
    return empresa

@router.get("/{empresa_id}", response_model=schemas.Empresa)
def read_empresa_by_id(
    empresa_id: int,
    db: Session = Depends(deps.get_db),
    # Allow superuser or any user belonging to that company to view company details
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific empresa by id.
    Accessible by superusers or users belonging to the company.
    """
    empresa = crud.empresa.get(db, id=empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    if not current_user.is_superuser and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return empresa

@router.put("/{empresa_id}", response_model=schemas.Empresa)
def update_empresa(
    *,
    db: Session = Depends(deps.get_db),
    empresa_id: int,
    empresa_in: schemas.EmpresaUpdate,
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an empresa (Superuser only).
    """
    empresa = crud.empresa.get(db, id=empresa_id)
    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="The empresa with this id does not exist in the system",
        )
    empresa = crud.empresa.update(db, db_obj=empresa, obj_in=empresa_in)
    return empresa

