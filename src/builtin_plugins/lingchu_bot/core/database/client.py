"""数据库CRUD函数"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from nonebot import require
from nonebot_plugin_orm import Model, get_session
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression

if TYPE_CHECKING:
    from sqlalchemy.engine import CursorResult

require("nonebot_plugin_orm")


def _conds[T: Model](
    model: type[T],
    filters: dict[str, Any] | None,
) -> list[ColumnElement[bool]]:
    if not filters:
        return []
    c: list[ColumnElement[bool]] = []
    for k, v in filters.items():
        col = getattr(model, k, None)
        if col is None:
            continue
        if v is None:
            c.append(col.is_(None))
        elif isinstance(v, Sequence) and not isinstance(v, (str, bytes)):
            c.append(col.in_(list(v)))
        else:
            c.append(col == v)
    return c


def _orders[T: Model](
    model: type[T],
    order_by: Sequence[str] | None,
) -> list[UnaryExpression[Any]]:
    if not order_by:
        return []
    o: list[UnaryExpression[Any]] = []
    for key in order_by:
        if key.startswith("-"):
            col = getattr(model, key[1:], None)
            if col is not None:
                o.append(col.desc())
        else:
            col = getattr(model, key, None)
            if col is not None:
                o.append(col.asc())
    return o


async def create[T: Model](model: type[T], **fields: Any) -> T:
    async with get_session() as s:
        obj = model(**fields)
        s.add(obj)
        try:
            await s.commit()
            await s.refresh(obj)
        except SQLAlchemyError:
            await s.rollback()
            raise
        return obj


async def get_one[T: Model](model: type[T], filters: dict[str, Any]) -> T | None:
    async with get_session() as s:
        stmt = select(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        return res.scalar_one_or_none()


async def list_items[T: Model](
    model: type[T],
    filters: dict[str, Any] | None = None,
    order_by: Sequence[str] | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[T]:
    async with get_session() as s:
        stmt = select(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        os = _orders(model, order_by)
        if os:
            stmt = stmt.order_by(*os)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        res = await s.execute(stmt)
        return list(res.scalars().all())


async def count[T: Model](model: type[T], filters: dict[str, Any] | None = None) -> int:
    async with get_session() as s:
        stmt = select(func.count()).select_from(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        res = await s.execute(stmt)
        return int(res.scalar_one())


async def update[T: Model](
    model: type[T],
    filters: dict[str, Any],
    values: dict[str, Any],
) -> int:
    async with get_session() as s:
        update_values = {k: v for k, v in values.items() if getattr(model, k, None)}
        if not update_values:
            return 0

        stmt = sqlalchemy_update(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.values(**update_values)

        try:
            result = cast("CursorResult[Any]", await s.execute(stmt))
            await s.commit()
            rowcount = result.rowcount
            return int(rowcount) if rowcount is not None else 0
        except SQLAlchemyError:
            await s.rollback()
            raise


async def delete[T: Model](model: type[T], filters: dict[str, Any]) -> int:
    async with get_session() as s:
        stmt = sqlalchemy_delete(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)

        try:
            result = cast("CursorResult[Any]", await s.execute(stmt))
            await s.commit()
            rowcount = result.rowcount
            return int(rowcount) if rowcount is not None else 0
        except SQLAlchemyError:
            await s.rollback()
            raise


async def get_or_create[T: Model](
    model: type[T],
    defaults: dict[str, Any] | None = None,
    **filters: Any,
) -> tuple[T, bool]:
    async with get_session() as s:
        cs = _conds(model, filters)
        stmt = select(model)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        obj = res.scalar_one_or_none()
        if obj is not None:
            return obj, False

        data = dict(filters)
        if defaults:
            data.update(defaults)
        obj = model(**data)
        s.add(obj)
        try:
            await s.commit()
            await s.refresh(obj)
        except IntegrityError:
            await s.rollback()
            res2 = await s.execute(stmt)
            obj2 = res2.scalar_one_or_none()
            if obj2 is None:
                raise
            return obj2, False
        except SQLAlchemyError:
            await s.rollback()
            raise
        else:
            return obj, True


async def exists[T: Model](model: type[T], filters: dict[str, Any]) -> bool:
    async with get_session() as s:
        stmt = select(1).select_from(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        return res.scalar_one_or_none() is not None
