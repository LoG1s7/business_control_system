from src.models import PositionInSubdivisionModel
from src.utils.repository import SqlAlchemyRepository


class PositionInSubdivisionRepository(SqlAlchemyRepository):
    model = PositionInSubdivisionModel
