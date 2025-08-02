from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, bool]


class ServicesListResponse(BaseModel):
    services: list[str]
    routes: Dict[str, str]
    urls: Dict[str, str]


class ErrorResponse(BaseModel):
    detail: str
    error_code: str = "GATEWAY_ERROR"
    timestamp: datetime = datetime.utcnow()
