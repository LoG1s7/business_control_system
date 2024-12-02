from src.models import PositionAssignmentModel
from src.utils.repository import SqlAlchemyRepository


class PositionAssignmentRepository(SqlAlchemyRepository):
    model = PositionAssignmentModel
