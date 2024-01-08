from flask import Flask, request
from urllib import parse
import json
import datetime
import base64
import slackbot_module.slackbot_api as slackAPI
from google_calendar_module.google_calendar_api import calendarAPI
from google_calendar_module.google_calendar_block_builder import block_builder
from google_calendar_module.google_calendar_modal_builder import modal_builder
from google_calendar_module.google_calendar_apphome import apphome

app = Flask(__name__)


@app.route("/interaction", methods=["POST"])
def interactivity_controll():
    # Slack이 Content-Type이 x-from-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = request.get_data(as_text=True)
    request_body = json.loads(parse.unquote(url_encoded_data).split("payload=")[-1])

    print(json_prettier(request_body))

    # 핸들링에 필요한 액션 처리
    action = request_body["actions"][0]
    action_id = action["action_id"]
    action_service = action_id.split("-")[0]
    action_type = action_id.split("-")[-1]

    handling_func = ACTION_DICT[action_service][action_type]

    return handling_func(request_body, action_type)


def get_value_from_action(action_dict):
    action_type_dict = {
        "timepicker": action_dict["selected_time"],
        "datepicker": action_dict["selected_date"],
        "static_select": action_dict["selected_option"]["text"]["text"],
        "users_select": action_dict["selected_user"],
    }

    return action_type_dict[action_dict["type"]]


def vacation_modal_submit(request_body):
    # +기호 이슈로 인한 디코딩 코드 추가
    view = UTFToKoreanJSON(request_body["view"])

    value_dict = dict()
    request = dict()

    for block in view["state"]["values"].values():
        for action_id, action_dict in block.items():
            value_dict[action_id] = get_value_from_action(action_dict)

    # google_calendar api 표준 : Dict {summary, start, end, all-day}
    # d

    now = datetime.datetime.now()

    # 왜 now로 했지.. 휴가는 특정 일자에 넣는건데 .....
    # 1. 휴가 일정 입력 수정 (반차, 시간연차 시간만 -> 일자, 시간) -> 완료 ㅋㅋ
    # 2. 구글캘린더 API에 all-day랑 start, end time 어떻게 입력할건지 고민
    start_time = value_dict["update_modal-modal_vacation_start_time"].split(":")
    end_time = value_dict["update_modal-modal_vacation_end_time"].split(":")

    request["summary"] = value_dict["update_calendar-modal_member_select"]
    request["start"] = datetime.datetime(
        year=now.year(),
        month=now.month(),
        day=now.day(),
        hour=start_time[0],
        minute=start_time[-1],
    )
    request["end"] = datetime.datetime(
        year=now.year(),
        month=now.month(),
        day=now.day(),
        hour=end_time[0],
        minute=end_time[-1],
    )
    request["all-day"] = None


def vacation_type_selected(request_body, action_name):
    # +기호 이슈로 인한 디코딩 코드 추가
    view = UTFToKoreanJSON(request_body["view"])
    view_id = view["id"]

    occured_action = request_body["actions"][0]
    action_id = occured_action["action_id"]
    block_id = occured_action["block_id"]

    selected_option = view["state"]["values"][block_id][action_id]["selected_option"]

    vacation_type = selected_option["value"]

    updated_view = modal_builder.update_vacation_insert_modal(
        orginal_view=view, vacation_type=vacation_type
    )

    slackAPI.modal_update(view=updated_view, view_id=view_id)

    return "ok", 200


def vacation_modal_open(request_body, action_name):
    # Required Argument
    trigger_id = request_body["trigger_id"]
    modal_type = action_name.split("_")[-1]

    modal_view = modal_builder.get_modal(modal_name=f"{modal_type}")
    slackAPI.modal_open(view=modal_view, trigger_id=trigger_id)

    return "ok", 200


def calendar_refresh(request_body, action_name):
    # Required Argument
    user_id = request_body["user"]["id"]

    apphome.refresh_app_home(user_id=user_id)

    return "ok", 200


def UTFToKorean(text):
    return text.encode("UTF-8").decode("UTF-8").replace("+", " ")


def UTFToKoreanJSON(data):
    converted_data = json.dumps(data).replace("+", " ")
    return json.loads(converted_data)


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)


ACTION_DICT = {
    "read_calendar": {
        "refresh": calendar_refresh,
        "today_vacation": None,
        "today_event": None,
    },
    "update_calendar": {
        "modal_open_vacation": vacation_modal_open,
        "modal_open_event": vacation_modal_open,
        "modal_submit": None,
        "modal_member_select": None,
        "modal_vacation_type_select": vacation_type_selected,
    },
}


# # 현재 쓰고있지 않음
# def calendar_message_handling(action_type, channel_id):
#     action_func_dict = {
#         "today_vacation": calendarAPI.get_vacation_list,
#         "today_event": calendarAPI.get_common_event_list,
#     }

#     event_list = action_func_dict[action_type](option="today")

#     blocks = block_builder.make_block_list(
#         event_list=event_list, action_type=action_type, day_option="today"
#     )
#     return slackAPI.post_message(channel_id, f"read_calendar-{action_type}", blocks)


# 알림
# 무엇을 알림?
# 슬랙의 특정 사용자에 대한 일정을 알림!
# 애매해서 우선 순위를 뒤로 두자
# @app.route('/calendar/alert')
