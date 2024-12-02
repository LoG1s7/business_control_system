
from src.models.position import PositionModel
from src.utils.repository import SqlAlchemyRepository


class PositionRepository(SqlAlchemyRepository):
    model = PositionModel
