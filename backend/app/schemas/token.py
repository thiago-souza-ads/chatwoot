from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject (usually user email or ID)
    empresa_id: Optional[int] = None
    is_superuser: Optional[bool] = False
    user_id: Optional[int] = None

# Renaming TokenData to TokenPayload to avoid potential confusion
# If TokenData was used elsewhere, ensure consistency or adjust
# Keeping TokenData for compatibility if it was used in deps.py
class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    empresa_id: Optional[int] = None
    is_superuser: Optional[bool] = False
    user_id: Optional[int] = None

