from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import nonebot
from fastapi import Body, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from nonebot import require
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.inspection import inspect as sa_inspect

require("nonebot_plugin_orm")
require("lingchu_bot")

if TYPE_CHECKING:
    from nonebot_plugin_orm import Model

from ..database import client
from ..database.model.models import (
    ChatConfig,
    ChatList,
    GlobalAdminUser,
    GlobalChatConfig,
    GlobalConfig,
    GlobalGroupConfig,
    GroupConfig,
    GroupList,
    LoginInfo,
    UiConfig,
)

app = nonebot.get_asgi()


app.openapi_tags = [
    {
        "name": "db",
        "description": "通用数据库 CRUD 接口（按模型名路由）",
    },
    {
        "name": "health",
        "description": "健康检查/可用性探测",
    },
]


MAX_LIMIT = 1000


class APIResponseBase(BaseModel):
    """标准化响应。

    - `status`: success/error
    - `data`: 成功时为数据，失败时为错误详情
    - `message`: 人类可读信息
    """

    status: Literal["success", "error"] = Field(
        default="success",
        description="响应状态",
        examples=["success"],
    )
    message: str = Field(
        default="ok",
        description="提示信息",
        examples=["ok"],
    )


class ErrorDetail(BaseModel):
    """错误详情"""

    error: str = Field(description="错误码", examples=["validation_error"])
    msg: str | None = Field(default=None, description="错误信息")
    where: str | None = Field(default=None, description="发生位置")
    fields: list[str] | None = Field(default=None, description="相关字段")
    model: str | None = Field(default=None, description="相关模型")
    field: str | None = Field(default=None, description="相关单字段")
    available: list[str] | None = Field(default=None, description="可用项")
    details: Any | None = Field(default=None, description="附加详情")


class APIErrorResponse(APIResponseBase):
    data: ErrorDetail = Field(description="错误详情")


class ModelsResponse(APIResponseBase):
    data: list[str] = Field(description="模型名称列表")


class RecordResponse(APIResponseBase):
    data: dict[str, Any] | None = Field(description="单条记录（或 None）")


class RecordListResponse(APIResponseBase):
    data: list[dict[str, Any]] = Field(description="记录列表")


class CountResponse(APIResponseBase):
    data: int = Field(description="记录数量", examples=[0, 1, 123])


class AffectedResponse(APIResponseBase):
    data: dict[str, int] = Field(
        description="受影响行数",
        examples=[{"updated": 1}, {"deleted": 3}],
    )


class HealthResponse(APIResponseBase):
    data: dict[str, Any] = Field(description="健康检查结果")


@app.exception_handler(HTTPException)
async def _http_exception_handler(
    _request: Request,
    exc: HTTPException,
) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        message = str(detail.get("msg") or detail.get("error") or "http_error")
        payload = APIErrorResponse(
            status="error",
            message=message,
            data=ErrorDetail(
                error=str(detail.get("error") or "http_error"),
                msg=detail.get("msg"),
                where=detail.get("where"),
                fields=detail.get("fields"),
                model=detail.get("model"),
                field=detail.get("field"),
                available=detail.get("available"),
                details={
                    k: v
                    for k, v in detail.items()
                    if k
                    not in {
                        "error",
                        "msg",
                        "where",
                        "fields",
                        "model",
                        "field",
                        "available",
                    }
                },
            ),
        )
    else:
        msg = str(detail) if detail else "http_error"
        payload = APIErrorResponse(
            status="error",
            message=msg,
            data=ErrorDetail(error="http_error", msg=msg),
        )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    payload = APIErrorResponse(
        status="error",
        message="validation_error",
        data=ErrorDetail(
            error="validation_error",
            details=exc.errors(),
        ),
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"description": "Bad Request", "model": APIErrorResponse},
    404: {"description": "Not Found", "model": APIErrorResponse},
    409: {"description": "Conflict", "model": APIErrorResponse},
    422: {"description": "Validation Error", "model": APIErrorResponse},
    500: {"description": "Internal Server Error", "model": APIErrorResponse},
}


MODEL_REGISTRY: dict[str, type[Model]] = {
    "LoginInfo": LoginInfo,
    "UiConfig": UiConfig,
    "GlobalAdminUser": GlobalAdminUser,
    "GlobalConfig": GlobalConfig,
    "GlobalGroupConfig": GlobalGroupConfig,
    "GlobalChatConfig": GlobalChatConfig,
    "GroupList": GroupList,
    "GroupConfig": GroupConfig,
    "ChatList": ChatList,
    "ChatConfig": ChatConfig,
}


def _get_model(model_name: str) -> type[Model]:
    model = MODEL_REGISTRY.get(model_name)
    if model is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "unknown_model",
                "model": model_name,
                "available": sorted(MODEL_REGISTRY.keys()),
            },
        )
    return model


def _model_column_keys(model: type[Model]) -> set[str]:
    mapper = sa_inspect(model).mapper
    return {attr.key for attr in mapper.column_attrs}


def _validate_known_keys(model: type[Model], data: dict, *, where: str) -> None:
    allowed = _model_column_keys(model)
    unknown = sorted([k for k in data if k not in allowed])
    if unknown:
        raise HTTPException(
            status_code=400,
            detail={"error": "unknown_field", "where": where, "fields": unknown},
        )


def _validate_filters(model: type[Model], filters: dict[str, Any]) -> None:
    _validate_known_keys(model, filters, where="filters")


def _validate_filters_optional(
    model: type[Model],
    filters: dict[str, Any] | None,
) -> None:
    if filters is None:
        return
    _validate_filters(model, filters)


def _clean_fields(model: type[Model], data: dict) -> dict:
    allowed = _model_column_keys(model)
    return {k: v for k, v in data.items() if k in allowed}


def _clean_fields_strict(model: type[Model], data: dict, *, where: str) -> dict:
    _validate_known_keys(model, data, where=where)
    return _clean_fields(model, data)


def _validate_order_by(
    model: type[Model],
    order_by: list[str] | None,
) -> list[str] | None:
    if not order_by:
        return None
    allowed = _model_column_keys(model)
    validated: list[str] = []
    for key in order_by:
        if not isinstance(key, str) or not key:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_order_by", "field": key},
            )
        field_name = key.removeprefix("-")
        if field_name not in allowed:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_order_by", "field": field_name},
            )
        validated.append(key)
    return validated


def _to_dict(obj: Model) -> dict:
    mapper = sa_inspect(type(obj)).mapper
    out: dict[str, object] = {}
    for attr in mapper.column_attrs:
        key = attr.key
        out[key] = getattr(obj, key)
    return out


class CreateReq(BaseModel):
    data: dict[str, Any] = Field(
        description="要创建的字段键值对（只允许模型列字段）",
        examples=[{"bot_id": 123, "bot_name": "test", "core_version": "0.1.0"}],
    )


class GetOneReq(BaseModel):
    filters: dict[str, Any] = Field(
        description="过滤条件（键为列名，值可为标量/列表/None）",
        examples=[{"id": 1}],
    )


class ListReq(BaseModel):
    filters: dict[str, Any] | None = Field(
        default=None,
        description="过滤条件（可选）",
        examples=[{"bot_status": 0}],
    )
    order_by: list[str] | None = Field(
        default=None,
        description="排序字段列表，例如 ['id', '-created_at']；前缀 '-' 表示倒序",
        examples=[["id"], ["-id"]],
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="偏移量（从 0 开始）",
        examples=[0],
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=MAX_LIMIT,
        description=f"分页大小（1~{MAX_LIMIT}）",
        examples=[100],
    )


class UpdateReq(BaseModel):
    filters: dict[str, Any] = Field(
        description="过滤条件（键为列名）",
        examples=[{"id": 1}],
    )
    values: dict[str, Any] = Field(
        description="要更新的字段键值对（只允许模型列字段）",
        examples=[{"bot_status": 1}],
    )


class DeleteReq(BaseModel):
    filters: dict[str, Any] = Field(
        description="过滤条件（键为列名）",
        examples=[{"id": 1}],
    )


@app.get(
    "/api/v1/db/models",
    tags=["db"],
    summary="获取模型列表",
    response_model=ModelsResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def list_models() -> ModelsResponse:
    """获取所有可用的数据模型列表。"""
    return ModelsResponse(
        status="success",
        data=sorted(MODEL_REGISTRY.keys()),
        message="ok",
    )


@app.get(
    "/api/v1/db/health",
    tags=["health"],
    summary="数据库健康检查",
    response_model=HealthResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def health_check() -> HealthResponse:
    """数据库连接健康检查（轻量）。"""
    try:
        _, status = await client.count(UiConfig, filters=None)
        if not status:
            raise HTTPException(
                status_code=500,
                detail={"error": "database_unavailable", "msg": "数据库不可用"},
            )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "database_unavailable", "msg": "数据库不可用"},
        ) from e
    return HealthResponse(
        status="success",
        data={"database": "connected"},
        message="healthy",
    )


@app.post(
    "/api/v1/db/{model_name}/create",
    tags=["db"],
    summary="创建记录",
    response_model=RecordResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_create(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: CreateReq = Body(...),
) -> RecordResponse:
    """创建一条记录。

    - `model_name`: 模型名称（见 `/api/db/models`）
    - `payload.data`: 字段键值
    """
    model = _get_model(model_name)
    fields = _clean_fields_strict(model, payload.data, where="data")
    try:
        obj, status = await client.create(model, **fields)
        if not status or obj is None:
            raise HTTPException(
                status_code=500,
                detail={"error": "database_error", "msg": "创建失败"},
            )
    except IntegrityError as e:
        error_msg = str(getattr(e, "orig", None) or "数据完整性约束冲突")
        raise HTTPException(
            status_code=409,
            detail={"error": "integrity_error", "msg": error_msg},
        ) from e
    except TypeError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_fields", "msg": str(e)},
        ) from e
    except SQLAlchemyError as e:
        msg = "数据库操作失败"
        if isinstance(e, OperationalError):
            msg = "数据库连接问题"
        raise HTTPException(
            status_code=500,
            detail={"error": "database_error", "msg": msg},
        ) from e
    return RecordResponse(status="success", data=_to_dict(obj), message="created")


@app.post(
    "/api/v1/db/{model_name}/get_one",
    tags=["db"],
    summary="查询单条记录",
    response_model=RecordResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_get_one(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: GetOneReq = Body(...),
) -> RecordResponse:
    """按条件查询单条记录（最多返回 1 条）。"""
    model = _get_model(model_name)
    _validate_filters(model, payload.filters)
    obj, status = await client.get_one(model, payload.filters)
    return RecordResponse(
        status="success" if status else "error",
        data=None if obj is None else _to_dict(obj),
        message="ok" if status else "not found",
    )


@app.post(
    "/api/v1/db/{model_name}/list",
    tags=["db"],
    summary="查询列表",
    response_model=RecordListResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_list(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: ListReq | None = Body(None),
) -> RecordListResponse:
    """查询记录列表。

    支持：`filters`、`order_by`、`offset`、`limit`。
    """
    model = _get_model(model_name)
    payload = payload or ListReq()
    _validate_filters_optional(model, payload.filters)
    payload.order_by = _validate_order_by(model, payload.order_by)
    items, status = await client.list_items(
        model,
        filters=payload.filters,
        order_by=payload.order_by,
        offset=payload.offset,
        limit=payload.limit,
    )
    return RecordListResponse(
        status="success" if status else "error",
        data=[_to_dict(x) for x in items],
        message="ok" if status else "query failed",
    )


@app.post(
    "/api/v1/db/{model_name}/count",
    tags=["db"],
    summary="统计数量",
    response_model=CountResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_count(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: ListReq | None = Body(None),
) -> CountResponse:
    """按条件统计记录数量。"""
    model = _get_model(model_name)
    payload = payload or ListReq()
    _validate_filters_optional(model, payload.filters)
    total, status = await client.count(model, filters=payload.filters)
    return CountResponse(
        status="success" if status else "error",
        data=total,
        message="ok" if status else "count failed",
    )


@app.post(
    "/api/v1/db/{model_name}/update",
    tags=["db"],
    summary="更新记录",
    response_model=AffectedResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_update(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: UpdateReq = Body(...),
) -> AffectedResponse:
    """按条件更新记录。

    - `payload.filters`: 过滤条件
    - `payload.values`: 更新字段
    """
    model = _get_model(model_name)
    _validate_filters(model, payload.filters)
    values = _clean_fields_strict(model, payload.values, where="values")
    try:
        updated, status = await client.update(model, payload.filters, values)
        if not status:
            raise HTTPException(
                status_code=500,
                detail={"error": "database_error", "msg": "更新失败"},
            )
    except IntegrityError as e:
        error_msg = str(getattr(e, "orig", None) or "数据完整性约束冲突")
        raise HTTPException(
            status_code=409,
            detail={"error": "integrity_error", "msg": error_msg},
        ) from e
    except SQLAlchemyError as e:
        msg = "数据库操作失败"
        if isinstance(e, OperationalError):
            msg = "数据库连接问题"
        raise HTTPException(
            status_code=500,
            detail={"error": "database_error", "msg": msg},
        ) from e
    return AffectedResponse(
        status="success",
        data={"updated": updated},
        message="updated",
    )


@app.post(
    "/api/v1/db/{model_name}/delete",
    tags=["db"],
    summary="删除记录",
    response_model=AffectedResponse,
    responses=COMMON_ERROR_RESPONSES,
)
async def api_delete(
    model_name: str = Path(
        ...,
        description="模型名称（见 /api/db/models）",
        openapi_examples={
            "BotConfig": {
                "summary": "示例模型名",
                "value": "BotConfig",
            }
        },
    ),
    payload: DeleteReq = Body(...),
) -> AffectedResponse:
    """按条件删除记录。"""
    model = _get_model(model_name)
    _validate_filters(model, payload.filters)
    try:
        deleted, status = await client.delete(model, payload.filters)
        if not status:
            raise HTTPException(
                status_code=500,
                detail={"error": "database_error", "msg": "删除失败"},
            )
    except SQLAlchemyError as e:
        msg = "数据库操作失败"
        if isinstance(e, OperationalError):
            msg = "数据库连接问题"
        raise HTTPException(
            status_code=500,
            detail={"error": "database_error", "msg": msg},
        ) from e
    return AffectedResponse(
        status="success",
        data={"deleted": deleted},
        message="deleted",
    )
