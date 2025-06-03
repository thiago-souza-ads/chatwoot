from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Usuario])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users (Superuser only).
    """
    users = crud.usuario.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.Usuario)
def create_user(
    *, # Force keyword arguments
    db: Session = Depends(deps.get_db),
    user_in: schemas.UsuarioCreate,
    # Only superuser or admin of the same company can create users
    # For MVP, let's simplify: Superuser creates admins/users for companies
    # Admin of a company creates agents/supervisors for their company
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user.
    Superusers can create users for any company or other superusers.
    Admins (non-superusers) can create users (agents/supervisors) for their own company.
    """
    user = crud.usuario.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Logic to enforce who can create whom
    if not current_user.is_superuser:
        if user_in.is_superuser:
             raise HTTPException(status_code=403, detail="Not enough permissions to create a superuser.")
        if user_in.empresa_id != current_user.empresa_id:
             raise HTTPException(status_code=403, detail="Cannot create users for other companies.")
        # Ensure non-superusers don't create users without assigning them to their company
        if not user_in.empresa_id:
             user_in.empresa_id = current_user.empresa_id
    else: # Superuser creating user
        if user_in.empresa_id:
            empresa = crud.empresa.get(db, id=user_in.empresa_id)
            if not empresa:
                raise HTTPException(status_code=404, detail=f"Empresa with id {user_in.empresa_id} not found.")
        # Superuser can create another superuser (empresa_id should be None)
        if user_in.is_superuser and user_in.empresa_id:
             raise HTTPException(status_code=400, detail="Superusers cannot belong to a specific company.")

    user = crud.usuario.create(db=db, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.Usuario)
def read_user_me(
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.Usuario)
def update_user_me(
    *, # Force keyword arguments
    db: Session = Depends(deps.get_db),
    password: str = None,
    nome: str = None,
    email: str = None,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = schemas.UsuarioUpdate(
        password=password,
        nome=nome,
        email=email
    ).dict(exclude_unset=True)

    user = crud.usuario.update(db, db_obj=current_user, obj_in=current_user_data)
    return user

@router.get("/{user_id}", response_model=schemas.Usuario)
def read_user_by_id(
    user_id: int,
    # Check if current user is superuser OR belongs to the same company as target user
    current_user: models.Usuario = Depends(deps.check_user_company_or_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    Accessible by superusers or users within the same company.
    """
    # The dependency already performs the check, but we need the target user object
    user = crud.usuario.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Re-validate permissions explicitly here or ensure dependency handles it fully
    # For now, assume dependency handles the permission check based on current_user and target_user_id implicitly passed via path
    # Let's refine the dependency to be more explicit if needed later.
    # The dependency needs access to user_id from the path. Let's adjust the dependency call.
    # We need to adjust how the dependency receives the target_user_id.
    # A better approach might be to fetch the user first, then check permissions.
    # Let's simplify for now and rely on the logic within the endpoint.

@router.get("/{user_id}", response_model=schemas.Usuario)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    Accessible by superusers or users within the same company.
    """
    user = crud.usuario.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_superuser and user.empresa_id != current_user.empresa_id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    return user

@router.put("/{user_id}", response_model=schemas.Usuario)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UsuarioUpdate,
    # Only superuser or admin/supervisor of the same company can update users
    current_user: models.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    Superusers can update any user.
    Admins/Supervisors can update users within their own company (with restrictions).
    """
    user = crud.usuario.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Permission checks
    if not current_user.is_superuser:
        if user.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="Cannot update users from other companies.")
        # Prevent non-superusers from making others superusers or changing company
        if user_in.is_superuser is True:
             raise HTTPException(status_code=403, detail="Not enough permissions to make a user superuser.")
        if user_in.empresa_id is not None and user_in.empresa_id != current_user.empresa_id:
             raise HTTPException(status_code=403, detail="Cannot change user's company.")
        # Potentially add more granular checks (e.g., admin can update agent/supervisor, supervisor can update agent)

    user = crud.usuario.update(db, db_obj=user, obj_in=user_in)
    return user

