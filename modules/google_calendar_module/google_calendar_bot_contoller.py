from flask import Flask, request, make_response, render_template, redirect, session
from urllib import parse
import json
from datetime import datetime
import slackbot_module.slackbot_api as slackAPI
import slackbot_module.slackbot_info as slackInfo
import slackbot_module.slackbot_utils as util
from google_calendar_api import calendarAPI
from google_calendar_apphome import apphome
from scheduler import scheduler
from service.event_spread import spread_service
from service.event_insert import event_insert_service
from service.vacation_insert import vacation_insert_service

# 맨 아래에 임의로 구현한 곳에서 사용
from views.util.block_builder import block_builder

# import logging
# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


@app.route("/interaction", methods=["POST"])
def interactivity_controll():
    # Slack이 Content-Type이 x-from-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = request.get_data(as_text=True)
    request_body = json.loads(parse.unquote(url_encoded_data).split("payload=")[-1])
    __temp_request_body__ = request_body

    # 핸들링에 필요한 액션 처리
    (action_service, action_type) = get_action_info(request_body=request_body)

    handling_func = ACTION_DICT[action_service][action_type]

    if handling_func == None:
        return "this action have no function", 200

    return handling_func(request_body)


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


# 파라미터로 state, code등의 정보를 가져옴
# 토큰을 생성
@app.route("/api/auth/callback/google", methods=["GET"])
def handling_oauth2():
    response_url = request.url
    print("response state:", request.args.get("state"))
    user_id = calendarAPI.get_temp_user()
    calendarAPI.user_register(
        auth_response_url=response_url.replace("http", "https"), user_id=user_id
    )

    apphome.refresh_single_app_home(user_id=user_id)
    return render_template("ok.html")


# 연동하기 버튼에 작성된 URL
# auth_url 생성하여 리다이렉트
@app.route("/link", methods=["GET"])
def redirect_auth_url():
    auth_url = calendarAPI.get_auth_url()
    return redirect(auth_url)


# 링크가 클릭된 이후 버튼 action이 실행된다.
def link(request_body):
    calendarAPI.set_temp_user(user_id=request_body["user"]["id"])
    print(request_body["user"]["id"])
    return "ok", 200


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
}


# TODO: 이건 어디에 구현해야 할까..
def today_events_post_all():
    users = slackInfo.get_user_list()

    for user in users:
        user_id = user["user_id"]
        user_name = util.get_user_name(user_id)
        common_event_list = calendarAPI.get_common_event_list(user_id=user_id)
        vacation_list = calendarAPI.get_vacation_list(user_id=user_id)

        composed_blocks = list()

        hello_text = f"{user_name}님 오늘의 일정 알려 드립니다.:blush:"

        hello_block = block_builder.create_single_block_section(hello_text)
        date_block = block_builder.create_block_header(
            f"{datetime.now().year}년 {datetime.now().month}월 {datetime.now().day}일"
        )
        vacation_blocks = block_builder.make_event_block_list(
            event_list=vacation_list, action_type="today_vacation", day_option="today"
        )
        commmon_event_blocks = block_builder.make_event_block_list(
            event_list=common_event_list, action_type="today_event", day_option="today"
        )

        composed_blocks = block_builder.compose(
            blocks=(
                block_builder.create_single_block_section(hello_text),
                block_builder.create_block_header(
                    f"{datetime.now().year}년 {datetime.now().month}월 {datetime.now().day}일"
                ),
                block_builder.make_event_block_list(
                    event_list=vacation_list,
                    action_type="today_vacation",
                    day_option="today",
                ),
                block_builder.make_event_block_list(
                    event_list=common_event_list,
                    action_type="today_event",
                    day_option="today",
                ),
            )
        )

        slackAPI.post_message(
            channel_id=user_id, text=hello_text, blocks=composed_blocks
        )

    return


scheduler.add_cron_scheduler("alert_event", today_events_post_all, hour=17, minute=30)
scheduler.execute()
