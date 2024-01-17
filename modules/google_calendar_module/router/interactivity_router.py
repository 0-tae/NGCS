from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from urllib import parse
import json
from view.apphome.apphome import apphome
import _slack.slack_utils as util
from _google.google_auth import google_auth
from domain.event_spread import spread_service
from domain.event_insert import event_insert_service
from domain.vacation_insert import vacation_insert_service
from schema.schemas import SlackResponse

# import logging
# logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/api/interaction",
    response_model=SlackResponse,
    response_model_exclude_defaults=True,
)
async def interactivity_controll(request: Request):
    # Slack이 Content-Type이 x-form-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = await request.body()

    request_body = json.loads(
        parse.unquote_plus(url_encoded_data.decode("utf-8")).split("payload=")[-1]
    )

    print(request_body)
    # 핸들링에 필요한 액션 처리
    (action_service, action_type) = get_action_info(request_body=request_body)

    handling_func = ACTION_DICT[action_service][action_type]

    if handling_func == None:
        return make_response({"ok": True})

    result = handling_func(request_body)
    return make_response(result)


def make_response(data: dict):
    ok = data.get("ok")
    response_action = data.setdefault("response_action", "default")
    return SlackResponse(ok=ok, response_action=response_action)


def get_action_info(request_body):
    action = request_body.get("actions")
    # view_submission 일 때
    if not action:
        callback_id = request_body["view"].get("callback_id").split("-")
        action_service = callback_id[0]
        action_type = callback_id[1]

    else:  # 그 이외 action 일 때
        action_id = action[0].get("action_id").split("-")
        action_service = action_id[0]
        action_type = action_id[1]

    return (action_service, action_type)


# TODO: 어디에 구현해야 할까..
# 연동하기 버튼을 누르면 브라우저 출력 이후, interactivity로 발생한 action에 대해 요청한다.
# 이 함수는 브라우저 출력 이후의 동작 함수이다.
def link(request_body):
    google_auth.set_temp_user(user_id=request_body["user"]["id"])
    return {"ok": True}


ACTION_DICT = {
    "apphome": {"refresh": apphome.refresh},
    "vacation_insert": {
        "modal_open_vacation": vacation_insert_service.modal_open,
        "modal_vacation_member_select": None,
        "modal_vacation_start_time": None,
        "modal_vacation_end_time": None,
        "modal_vacation_start_date": None,
        "modal_vacation_end_date": None,
        "modal_vacation_type_select": vacation_insert_service.vacation_type_selected,
        "modal_submit_vacation": vacation_insert_service.modal_vacation_submit,
    },
    "event_insert": {
        "modal_open_event": event_insert_service.modal_open,
        "modal_event_summary": None,
        "modal_event_date": None,
        "modal_event_start_time": None,
        "modal_event_end_time": None,
        "modal_event_description": None,
        "modal_event_allday": event_insert_service.allday_changed,
        "modal_submit_event": event_insert_service.modal_event_submit,
    },
    "access_calendar": {"register": link},
    "event_spread": {
        "modal_open_spread": spread_service.modal_open,
        "modal_submit_spread": spread_service.modal_spread_submit,
        "modal_spread_date_select": spread_service.spread_date_selected,
        "modal_spread_event_select": spread_service.spread_event_selected,
        "modal_spread_type_select": spread_service.spread_type_selected,
        "modal_spread_users_select": None,
        "modal_spread_channels_select": None,
        "insert_event": spread_service.insert_event,
    },
    "invite": {"invite": None},
}
