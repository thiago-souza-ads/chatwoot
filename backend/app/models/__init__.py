# Import all models here so that Base has them before being
# imported by Alembic or used by init_db
from app.db.base_class import Base  # noqa
from .empresa import Empresa  # noqa
from .usuario import Usuario  # noqa
from .crm import Board, Coluna, Card, Tag  # noqa
from .instancia_evolution import InstanciaEvolution  # noqa

