import logging

from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from app.db.base import Base
from app.db.session import engine

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

logger = logging.getLogger(__name__)

# Initial data: First superuser
FIRST_SUPERUSER_EMAIL = settings.FIRST_SUPERUSER
FIRST_SUPERUSER_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    Base.metadata.create_all(bind=engine)

    user = crud.usuario.get_by_email(db, email=FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.UsuarioCreate(
            email=FIRST_SUPERUSER_EMAIL,
            password=FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            nome="Super Admin"
            # Superuser does not belong to any empresa, so empresa_id is None
        )
        user = crud.usuario.create(db, obj_in=user_in)
        logger.info(f"Created first superuser: {FIRST_SUPERUSER_EMAIL}")
    else:
        logger.info(f"Superuser {FIRST_SUPERUSER_EMAIL} already exists in database.")

