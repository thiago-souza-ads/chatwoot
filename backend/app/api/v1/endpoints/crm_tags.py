from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

# Dependency to check if the user belongs to the company of the tag
def get_tag_empresa_user(
    tag_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> models.Tag:
    tag = crud.tag.get(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if not current_user.is_superuser and tag.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this tag")
    return tag

@router.get("/", response_model=List[schemas.Tag])
def read_tags(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tags for the user's company.
    """
    if current_user.is_superuser:
        # Superusers likely shouldn't manage tags directly, or need a filter
        # Returning empty list for now, adjust if needed.
        tags = []
        # Or get all tags: tags = crud.tag.get_multi(db, skip=skip, limit=limit)
    elif current_user.empresa_id:
        tags = crud.tag.get_multi_by_empresa(
            db, empresa_id=current_user.empresa_id, skip=skip, limit=limit
        )
    else:
        tags = [] # User without company
    return tags

@router.post("/", response_model=schemas.Tag)
def create_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag_in: schemas.TagCreate,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new tag for the user's company.
    """
    if not current_user.is_superuser:
        if not current_user.empresa_id:
             raise HTTPException(status_code=400, detail="User does not belong to a company")
        # Force tag to be created for the user's company
        tag_in.empresa_id = current_user.empresa_id
    else:
        # Superuser must specify empresa_id
        if not tag_in.empresa_id:
            raise HTTPException(status_code=400, detail="Superuser must specify empresa_id to create a tag")
        # Verify company exists
        empresa = crud.empresa.get(db, id=tag_in.empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail=f"Empresa with id {tag_in.empresa_id} not found.")

    # Check if tag name already exists for the company
    existing_tag = crud.tag.get_by_nome_and_empresa(db, nome=tag_in.nome, empresa_id=tag_in.empresa_id)
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists for this company")

    tag = crud.tag.create(db=db, obj_in=tag_in)
    return tag

@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(
    tag: models.Tag = Depends(get_tag_empresa_user), # Checks access
) -> Any:
    """
    Get tag by ID. Access controlled by dependency.
    """
    return tag

@router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag: models.Tag = Depends(get_tag_empresa_user), # Checks access
    tag_in: schemas.TagUpdate,
    # Any active user in the company can update tags
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a tag. User must belong to the company.
    """
    # Dependency get_tag_empresa_user already checks company access
    # Check for name conflict if name is being changed
    if tag_in.nome and tag_in.nome != tag.nome:
        existing_tag = crud.tag.get_by_nome_and_empresa(db, nome=tag_in.nome, empresa_id=tag.empresa_id)
        if existing_tag:
            raise HTTPException(status_code=400, detail="Tag with this name already exists for this company")

    tag = crud.tag.update(db, db_obj=tag, obj_in=tag_in)
    return tag

@router.delete("/{tag_id}", response_model=schemas.Tag)
def delete_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag: models.Tag = Depends(get_tag_empresa_user), # Checks access
    # Any active user in the company can delete tags
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a tag. User must belong to the company.
    """
    # Dependency get_tag_empresa_user already checks company access
    # Optional: Check if tag is associated with any cards before deleting?
    tag = crud.tag.remove(db, id=tag.id)
    return tag

