from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.Usuario:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenData(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.usuario.get_by_email(db, email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: models.Usuario = Depends(get_current_user),
) -> models.Usuario:
    if not crud.usuario.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: models.Usuario = Depends(get_current_active_user),
) -> models.Usuario:
    if not crud.usuario.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

# Dependency to check if the user belongs to the same company or is a superuser
def check_user_company_or_superuser(
    current_user: models.Usuario = Depends(get_current_active_user),
    target_user_id: int = None, # Placeholder, actual ID will come from path param usually
    db: Session = Depends(get_db)
) -> models.Usuario:
    if crud.usuario.is_superuser(current_user):
        return current_user # Superuser can access any user

    if target_user_id:
        target_user = crud.usuario.get(db, id=target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        if current_user.empresa_id != target_user.empresa_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # If no target_user_id is provided, it might be a general check or handled elsewhere
    # For now, just return the current user if not superuser
    return current_user

# Dependency to check if the user is a supervisor or superuser
def get_current_active_supervisor_or_superuser(
    current_user: models.Usuario = Depends(get_current_active_user),
) -> models.Usuario:
    if not (current_user.is_supervisor or current_user.is_superuser):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges (supervisor or superuser required)"
        )
    return current_user

