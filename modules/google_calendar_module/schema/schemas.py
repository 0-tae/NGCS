from pydantic import BaseModel
from typing import List


# 응답 데이터를 정의하는 Pydantic 모델
class SlackResponse(BaseModel):
    ok: bool
    response_action: str = "default"
