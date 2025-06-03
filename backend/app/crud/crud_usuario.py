from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        db_obj = Usuario(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            nome=obj_in.nome,
            is_superuser=obj_in.is_superuser,
            is_supervisor=obj_in.is_supervisor,
            empresa_id=obj_in.empresa_id,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Usuario, obj_in: Union[UsuarioUpdate, Dict[str, Any]]
    ) -> Usuario:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[Usuario]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: Usuario) -> bool:
        return user.is_active

    def is_superuser(self, user: Usuario) -> bool:
        return user.is_superuser

usuario = CRUDUsuario(Usuario)

