from flask import Flask, request, redirect
from urllib import parse
import json
import slackbot_module.slackbot_api as slackAPI
from google_calendar_module.google_calendar_api import calendarAPI
from google_calendar_module.google_calendar_block_builder import block_builder
from google_calendar_module.google_calendar_modal_builder import modal_builder
from google_calendar_module.google_calendar_apphome import apphome

app = Flask(__name__)


def create_forward_path(request_body):
    # 액션이 발생한 interactivity의 action_id를 가져옴
    # channel_id가 user_id라면 DM으로 보낸다.
    action = request_body["actions"][0]
    action_id = action["action_id"]
    trigger_id = request_body["trigger_id"]
    channel_id = request_body["user"]["id"]

    # action_id는 [service]-[event_type] 으로 구분된다.
    # 이벤트에 해당하는 path로 리다이렉트
    action_service = action_id.split("-")[0]
    action_type = action_id.split("-")[-1]

    # TODO: default path 정하기

    action_path_dict = {
        "refresh": f"/read_calendar/refresh/{channel_id}",
        "today_vacation": f"/read_calendar/today_vacation/{channel_id}",
        "today_event": f"/read_calendar/today_event/{channel_id}",
        "modal_open": f"/update_calendar/modal_open/{channel_id}/{trigger_id}",
        "modal_submit": f"/update_calendar/modal_submit/{channel_id}",
    }

    return action_path_dict[action_type]


@app.route("/interaction", methods=["POST"])
def interactivity_controll():
    # Slack이 Content-Type이 x-from-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = request.get_data(as_text=True)
    request_body = json.loads(parse.unquote(url_encoded_data).split("payload=")[-1])

    print(request_body)
    forward_path = create_forward_path(request_body)

    return redirect(forward_path)


@app.route("/update_calendar/modal_open/<user_id>/<trigger_id>")
def insert_event(user_id, trigger_id):
    # 휴가자 추가 모달 이전에 선택하는 모달이 나와야함
    # 일단..
    modal_view = modal_builder.get_modal(modal_name="insert_vaction")
    slackAPI.modal_open(view=modal_view, trigger_id=trigger_id)

    return "ok", 200


@app.route("/read_calendar/refresh/<user_id>")
def calendar_refresh(user_id):
    apphome.refresh_app_home(user_id=user_id)
    return "ok", 200


# 현재 쓰고있지 않음
@app.route("/read_calendar/<action_type>/<channel_id>")
def calendar_message_handling(action_type, channel_id):
    action_func_dict = {
        "today_vacation": calendarAPI.get_vacation_list,
        "today_event": calendarAPI.get_common_event_list,
    }

    event_list = action_func_dict[action_type](option="today")

    blocks = block_builder.make_block_list(
        event_list=event_list, action_type=action_type, day_option="today"
    )
    return slackAPI.post_message(channel_id, f"read_calendar-{action_type}", blocks)


# 알림
# 무엇을 알림?
# 슬랙의 특정 사용자에 대한 일정을 알림!
# 애매해서 우선 순위를 뒤로 두자
# @app.route('/calendar/alert')
