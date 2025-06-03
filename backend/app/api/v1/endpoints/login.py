from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas, models # Add models import here
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.usuario.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.usuario.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Include user info in the token subject for easier access later
    token_subject = {
        "sub": user.email,
        "empresa_id": user.empresa_id,
        "is_superuser": user.is_superuser,
        "user_id": user.id
    }

    return {
        "access_token": security.create_access_token(
            token_subject, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

# Example endpoint to test authentication
@router.post("/login/test-token", response_model=schemas.Usuario)
def test_token(
    current_user: models.Usuario = Depends(deps.get_current_user)
) -> Any:
    """
    Test access token
    """
    return current_user

