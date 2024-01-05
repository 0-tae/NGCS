from flask import Flask, request, redirect
from urllib import parse
import json
import requests
import slackbot_base.slackbot_info as sb_info
import slackbot_base.slackbot_sender as sender
import copy
from google_calendar_module.google_calendar_api import calendar
import google_calendar_module.block_builder_for_google_calendar as block_builder


CHANNEL_ID = sb_info.get_channel_id('slack-bot')

app = Flask(__name__)

class AppHomeComponent:
    __base_view__ = None

    def publish(self, view):
        header = sb_info.get_header()
        user_list = sb_info.get_user_list()

        # 모든 유저에 대해 app_home 출력
        for user in user_list:
            data = {"user_id": user["user_id"], "view": view}
            response = requests.post("https://slack.com/api/views.publish", headers = header, json = data)
            print("user_id:",user["user_id"], response)

    def init_app_home(self):
        init_view = self.get_base_view()
        self.publish(init_view)

    # 초기 app_home 구성
    def get_base_view(self):
        if self.__base_view__ is None:
            print("Get initial View")
            initial_block_list = [
                {
                    "type":"section",
                    "text":{
                        "type":"mrkdwn",
                        "text":"안녕하세요. 구글캘린더 봇입니다!:smile:"
                    }
                },
                {
                    "type":"actions",
                    "elements":[block_builder.create_button("새로 고침:arrows_counterclockwise:","calendar-refresh"),
                                block_builder.create_button("오늘 휴가:basketball:","calendar-today_vacation"),
                                block_builder.create_button("오늘 일정:basketball:","calendar-today_event"),
                                block_builder.create_button("이번 달 휴가자:basketball:","calendar-month_vacation") ]
                }
            ]
            
            self.base_view = {
                "type":"home",
                "blocks": initial_block_list
            }

        return self.__base_view__
    

    def refresh_view(self):
        # deepcopy를 해야 하는 게 맞겠죠..?
        compose_view = copy.deepcopy(self.get_base_view())
        compose_view_block = compose_view["blocks"]

        compose_view_block.append(block_builder.create_block_divider())
        compose_view_block.append(self.get_today_vacation_view())
        compose_view_block.append(self.get_today_common_event_view())

        # view publish
        self.publish(compose_view)


    def get_today_vacation_view(self):
        view = None
        event_list = calendar.get_vacation_list(option = "today")
        blocks = block_builder.make_block_list(event_list = event_list, action_type="today_vacation",  day_option="today")

        view.append(block_builder.create_block_divider())

        for block in blocks:
            view.append(block)
        
        return view

    def get_today_common_event_view(self):
        view = None
        event_list = calendar.get_common_event_list(option = "today")
        blocks = block_builder.make_block_list(event_list = event_list, action_type="today_event",  day_option="today")

        view["blocks"].append(block_builder.create_block_divider())

        for block in blocks:
            view["blocks"].append(block)
        
        return view

def create_forward_path(request_body):
    # 액션이 발생한 interactivity의 action_id를 가져옴
    # channel_id가 user_id라면 DM으로 보낸다.
    action = request_body['actions'][0]
    action_id = action['action_id']
    channel_id = request_body["user"]["id"]

    # action_id는 [service]-[event_type] 으로 구분된다.
    # 이벤트에 해당하는 path로 리다이렉트
    action_service = action_id.split("-")[0]
    action_type = action_id.split("-")[-1]
    
    # TODO: default path 정하기

    action_path_dict = {
        "refresh":         f"/calendar/refresh",
        "today_vacation":  f"/calendar/today_vacation/{channel_id}",
        "today_event":     f"/calendar/today_event/{channel_id}",
    }

    return action_path_dict[action_type]

@app.route('/interaction', methods = ['POST'])
def interactivity_controll():
    # Slack이 Content-Type이 x-from-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = request.get_data(as_text=True)
    request_body = json.loads(parse.unquote(url_encoded_data).split("payload=")[-1])

    forward_path = create_forward_path(request_body)

    return redirect(forward_path)

@app.route('/calendar/refresh')
def calendar_refresh():
    apphome.refresh_view()
    return "ok", 200

@app.route('/calendar/<action_type>/<channel_id>')
def calendar_message_handling(action_type, channel_id):
    action_func_dict = {
        "today_vacation": calendar.get_vacation_list,
        "today_event": calendar.get_common_event_list
    }

    event_list = action_func_dict[action_type](option = "today")

    blocks = block_builder.make_block_list(event_list = event_list, action_type=action_type,  day_option="today")
    return sender.post_message(channel_id, f"calendar-{action_type}", blocks)

apphome = AppHomeComponent()
apphome.init_app_home()