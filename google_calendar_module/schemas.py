from pydantic import BaseModel
from typing import Dict
import util.common_util as util
from datetime import datetime


# 응답 데이터를 정의하는 Pydantic 모델


class SlackOk:
    slack_ok: bool = True


class HttpBaseResponse(BaseModel):
    ok: bool
    status_code: int
    message: str


class HttpResponse(HttpBaseResponse):
    ok: bool
    body: Dict[str, str]
    status_code: int
    message: str


class HttpErrorResponse(HttpBaseResponse):
    ok: bool = False
    message: str = "unexpected error"


class SlackModalSubmitResponse(BaseModel):
    response_action: str = "clear"


class MediaApprovalRequest(BaseModel):
    pass


class EmailResponse(BaseModel):
    ok: bool
    message: str


class BaseSchema(BaseModel):
    # 객체 생성 날짜
    created_at: datetime = util.now()

    # 객체 소멸 날짜
    deleted_at: datetime = None
