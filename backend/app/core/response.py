from enum import Enum
from typing import Optional, Any, List, Dict

from pydantic import BaseModel


class ReturnStatus(Enum):
    SUCCESS = "success"
    FAIL = "fail"


class ResponseBaseModel(BaseModel):
    status: str


class ResponseModel(ResponseBaseModel):
    content: Optional[Any]
    info: str


class SearchResponseModel(ResponseBaseModel):
    count: int = 0
    count_all: Optional[Dict]
    data: Optional[List[Any]]
    page: Optional[int]
    page_size: Optional[int]


class ResponseException(Exception):
    def __init__(self, code: int, info: str):
        self.code = code
        self.info = info
