"""
数据库CRUD函数
提供通用的ORM模型的增删查改（CRUD）操作，基于SQLAlchemy和nonebot_plugin_orm。
"""

from nonebot import require

require("nonebot_plugin_orm")
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from nonebot_plugin_orm import Model, get_session
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression

if TYPE_CHECKING:
    from sqlalchemy.engine import CursorResult


def _conds[T: Model](
    model: type[T],
    filters: dict[str, Any] | None,
) -> list[ColumnElement[bool]]:
    """
    构造SQLAlchemy的条件表达式列表。
    参数：
        model: ORM模型类
        filters: 字段名到值的映射，支持None、单值、序列
    返回：
        SQLAlchemy条件表达式列表
    """
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
    """
    构造SQLAlchemy的排序表达式列表。
    参数：
        model: ORM模型类
        order_by: 排序字段名序列，支持"-字段"降序
    返回：
        SQLAlchemy排序表达式列表
    """
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


# 单条操作
async def create[T: Model](model: type[T], **fields: Any) -> T:
    """
    创建一条新记录。
    参数：
        model: ORM模型类
        **fields: 字段名及其值
    返回：
        新创建的模型对象
    """
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
    """
    获取符合条件的单条记录。
    参数：
        model: ORM模型类
        filters: 字段名到值的映射
    返回：
        查询到的模型对象或None
    """
    async with get_session() as s:
        stmt = select(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        return res.scalar_one_or_none()


async def get_or_create[T: Model](
    model: type[T],
    defaults: dict[str, Any] | None = None,
    **filters: Any,
) -> tuple[T, bool]:
    """
    获取或创建一条记录。
    若存在则返回，不存在则新建。
    参数：
        model: ORM模型类
        defaults: 默认字段值
        **filters: 查找条件
    返回：
        (对象, 是否新建)
    """
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


async def update_or_create[T: Model](
    model: type[T],
    filters: dict[str, Any],
    defaults: dict[str, Any] | None = None,
) -> tuple[T, bool]:
    """
    更新或创建一条记录。
    若存在则更新，不存在则创建。
    参数：
        model: ORM模型类
        filters: 查找条件
        defaults: 默认字段值
    返回：
        (对象, 是否新建)
    """
    async with get_session() as s:
        cs = _conds(model, filters)
        stmt = select(model)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        obj = res.scalar_one_or_none()
        if obj is not None:
            update_values = defaults or {}
            if update_values:
                stmt_update = sqlalchemy_update(model)
                if cs:
                    stmt_update = stmt_update.where(*cs)
                stmt_update = stmt_update.values(**update_values)
                try:
                    await s.execute(stmt_update)
                    await s.commit()
                    await s.refresh(obj)
                except SQLAlchemyError:
                    await s.rollback()
                    raise
            return obj, False
        data = dict(filters)
        if defaults:
            data.update(defaults)
        obj = model(**data)
        s.add(obj)
        try:
            await s.commit()
            await s.refresh(obj)
        except SQLAlchemyError:
            await s.rollback()
            raise
        return obj, True


async def update[T: Model](
    model: type[T],
    filters: dict[str, Any],
    values: dict[str, Any],
) -> int:
    """
    更新符合条件的记录。
    参数：
        model: ORM模型类
        filters: 筛选条件
        values: 要更新的字段及其值
    返回：
        受影响的行数
    """
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
    """
    删除符合条件的记录。
    参数：
        model: ORM模型类
        filters: 筛选条件
    返回：
        删除的行数
    """
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


async def exists[T: Model](model: type[T], filters: dict[str, Any]) -> bool:
    """
    判断是否存在符合条件的记录。
    参数：
        model: ORM模型类
        filters: 筛选条件
    返回：
        存在返回True，否则False
    """
    async with get_session() as s:
        stmt = select(1).select_from(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        stmt = stmt.limit(1)
        res = await s.execute(stmt)
        return res.scalar_one_or_none() is not None


# 批量操作
async def bulk_create[T: Model](
    model: type[T], objs: list[dict[str, Any]], *, commit: bool = True
) -> list[T]:
    """
    批量创建多条记录。
    参数：
        model: ORM模型类
        objs: 字段字典列表
        commit: 是否立即提交事务
    返回：
        新创建的模型对象列表
    """
    async with get_session() as s:
        instances = [model(**fields) for fields in objs]
        s.add_all(instances)
        if commit:
            try:
                await s.commit()
                for obj in instances:
                    await s.refresh(obj)
            except SQLAlchemyError:
                await s.rollback()
                raise
        return instances


async def list_items[T: Model](
    model: type[T],
    filters: dict[str, Any] | None = None,
    order_by: Sequence[str] | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[T]:
    """
    获取符合条件的多条记录列表。
    参数：
        model: ORM模型类
        filters: 字段名到值的映射
        order_by: 排序字段
        offset: 偏移量
        limit: 限制条数
    返回：
        查询到的模型对象列表
    """
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
    """
    统计符合条件的记录数量。
    参数：
        model: ORM模型类
        filters: 字段名到值的映射
    返回：
        记录数
    """
    async with get_session() as s:
        stmt = select(func.count()).select_from(model)
        cs = _conds(model, filters)
        if cs:
            stmt = stmt.where(*cs)
        res = await s.execute(stmt)
        return int(res.scalar_one())
