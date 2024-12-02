from collections.abc import Sequence
from typing import Any

from sqlalchemy import Result, Row, select, text

from src.models.subdivision import SubdivisionModel
from src.utils.repository import SqlAlchemyRepository


class SubdivisionRepository(SqlAlchemyRepository):
    model = SubdivisionModel

    async def get_all_path_of_parent(self, parent: str) -> type(model) | None:
        query = select(self.model.path).where(self.model.name == parent)
        path: Result | None = await self.session.execute(query)
        return path.scalar_one_or_none()

    async def get_children_paths(
        self, subdivision_name: str,
    ) -> Sequence[Row[tuple[Any, ...] | Any]]:
        query = text(
            'SELECT id, name, path '
            'FROM subdivision '
            'WHERE path <@ '
            '(SELECT path '
            'FROM subdivision '
            'WHERE name = :node_name)',
        ).params(node_name=subdivision_name)
        result: Result = await self.session.execute(query)
        child_nodes = result.fetchall()
        return child_nodes

    async def change_children_paths(
        self, child_nodes: Sequence[Row[tuple[Any, ...] | Any]],
    ) -> None:
        node_name = child_nodes[0][1]
        for child in child_nodes[1:]:
            _child_id, child_name, child_path = child
            new_path = child_path.replace(f'{node_name}.', '')
            stmt = text(
                'UPDATE subdivision SET path = :new_path WHERE name = :child_name',
            ).params({'new_path': new_path, 'child_name': child_name})
            await self.session.execute(stmt)

    async def update_children_paths(
        self, child_nodes: Sequence[Row[tuple[Any, ...] | Any]], new_path_name: str,
    ) -> None:
        node_name = child_nodes[0][1]
        for child in child_nodes:
            _child_id, child_name, child_path = child
            new_path = child_path.replace(f'{node_name}', f'{new_path_name}')
            stmt = text(
                'UPDATE subdivision SET path = :new_path WHERE name = :child_name',
            ).params({'new_path': new_path, 'child_name': child_name})
            await self.session.execute(stmt)
