# app/utils/responses.py
from typing import Optional, TypeVar, Generic
from fastapi import status
from app.schemas.response import ApiResponse
from app.core.constants import MSG_SUCCESS, MSG_INTERNAL_ERROR

T = TypeVar("T")

def ok(data: T = None, message: str = MSG_SUCCESS, code: int = status.HTTP_200_OK) -> ApiResponse[T]:
    return ApiResponse[T](success=True, code=code, message=message, data=data)

def fail(message: str, code: int) -> ApiResponse[None]:
    return ApiResponse[None](success=False, code=code, message=message, data=None)
