from flask import Flask, request, make_response, jsonify, redirect
from urllib import parse
from threading import Thread
import json
import requests
import slackbot_base.slackbot_info as sb_info
import slackbot_base.slackbot_sender as sender
from google_calendar_api_module.google_calender import calendar
from datetime import datetime



CHANNEL_ID = sb_info.get_channel_id('slack-bot')

app = Flask(__name__)

class AppHomeComponent:
    view = None

    def publish(self):
        view = self.get_view()
        
        header = sb_info.get_header()
        user_list = sb_info.get_user_list()

        for user in user_list:
            data = {"user_id": user["user_id"], "view": view}
            response = requests.post("https://slack.com/api/views.publish", headers = header, json = data)
            print("user_id:",user["user_id"], response)


    def init_app_home(self):
        view = self.get_view()
        view.

        self.publish()

    # 초기 app_home 구성
    def get_view(self):
        if self.view is None:
            initial_block_list = [
                {
                    "type":"section",
                    "text":{
                        "type":"mrkdwn",
                        "text":"안녕하세요. 구글캘린더 봇입니다:smile:"
                    }
                },
                {
                    "type":"actions",
                    "elements":[self.get_button("오늘 휴가자:basketball:","calendar-today_vacation"),
                                self.get_button("오늘 일정:basketball:","calendar-today_event"),
                                self.get_button("이번 달 휴가자:basketball:","calendar-month_vacation") ]
                }
            ]
            
            self.view = {
                "type":"home",
                "blocks": initial_block_list
            }

        return self.view
    

    def get_today_vacation_view(self):
        addr_blocks = None
        event_list = calendar.get_vacation_list(option = "today")
        blocks = make_block_list(event_list = event_list, action_type="today_vacation",  day_option="today")

        addr_blocks.append(create_block_divider())

        for block in blocks:
            addr_blocks.append(block)
        
        return addr_blocks

    def get_today_common_event_view(self):
        view = None
        event_list = calendar.get_common_event_list(option = "today")
        blocks = make_block_list(event_list = event_list, action_type="today_event",  day_option="today")
        

        view["blocks"].append(create_block_divider())

        for block in blocks:
            view["blocks"].append(block)
        
        retrun view

    def get_button(self, text, action_id):
        return {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": text,
                    "emoji": True
                },
                "value": action_id,
                "action_id": action_id
            }


@app.route('/interaction', methods = ['POST'])
def interactivity_controll():
    # Slack이 Content-Type이 x-from-included-data인 request를 보냄
    # request가 url encoded 되어 있기 때문에 url decoding 실행
    url_encoded_data = request.get_data(as_text=True)
    request_body = json.loads(parse.unquote(url_encoded_data).split("payload=")[-1])

    # 액션이 발생한 interactivity의 action_id를 가져옴
    # channel_id가 user_id라면 DM으로 보낸다.
    action = request_body['actions'][0]
    action_id = action['action_id']

    channel_id = request_body["user"]["id"]

    # action_id는 [service]-[event_type] 으로 구분된다.
    # 이벤트에 해당하는 path로 리다이렉트
    service_path = action_id.split("-")[0]
    event_type_path = action_id.split("-")[-1]


    return redirect(f"/{service_path}/{event_type_path}/{channel_id}")

@app.route('/calendar/<action_type>/<channel_id>')
def calendar_handling(action_type, channel_id):
    action_func_dict = {
        "today_vacation": calendar.get_vacation_list,
        "today_event": calendar.get_common_event_list
    }

    event_list = action_func_dict[action_type](option = "today")

    blocks = make_block_list(event_list = event_list, action_type=action_type,  day_option="today")
    return sender.post_message(channel_id, f"calendar-{action_type}", blocks)


# TODO: 블럭 빌드 작업을 따로 분리해야 함
#       코드를 줄일 수 있을 것 같은데..

# 블록 헤더 만들기
def create_block_header(text):
    block = {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": text,
                }
		    }
    
    return block

def create_block_section(text):
    block = {
                "type": "section", 
                "text": { 
                    "type": "mrkdwn",
                    "text": text
                }
            }
    
    return block

def create_block_section_vacation(event):
    # ex. event["summary"] = "최용태-오전 반차"
    name = event["summary"].split("-")[0]
    vacation_type = event["summary"].split("-")[-1]

    event_summary = "연차"

    # 연차일 경우 시간 설명 생략
    # 그 이외는 시간 설명
    if not event["all-day"] :
        time_range = datetime.fromisoformat(event["start"]).strftime("%H:%M")+ \
                     "~"+datetime.fromisoformat(event["end"]).strftime("%H:%M")
            
        event_summary =  f"{vacation_type} ({time_range})"

    # ex) 최용태 님 오늘 09:00~12:00 오전 반차
    # ex) 최용태 님 오늘 연차
    return  f"{text_bold(name)} 님 {event_summary}"

def create_block_section_common_event(event):
    event_summary = event["summary"]

    # 하루 종일 일 경우, 시간 설명 생략
    # 그 이외는 시간 설명
    if not event["all-day"]:
        time_range = datetime.fromisoformat(event["start"]).strftime("%H:%M")+ \
                     "~"+datetime.fromisoformat(event["end"]).strftime("%H:%M")
            
        event_summary += f" ({time_range})"

    return  f"{event_summary}"

def create_block_divider():
    block = {
            "type": "divider"
            }
    return block

# TODO: day_option(오늘, 특정 일자) 구현
def make_block_list(event_list, action_type, day_option):
    action_type_dict = {
        "today_vacation": {
                "section_text": create_block_section_vacation,
                "block_header": "오늘 휴가자 목록:smile:"
            },
        "today_event": {
                "section_text": create_block_section_common_event,
                "block_header": "오늘 일정 목록:saluting_face:"
        }
    }

    block_list = []
    action = action_type_dict[action_type]

    block_header = action.get("block_header")
    block_list.append(create_block_header(text = block_header))

    for event in event_list: 
        section_text = action.get("section_text")(event = event)
        block = create_block_section(section_text)
        block_list.append(block)
    
    return block_list

def text_bold(text):
    return f"*{text}*"

def is_allday_event(event):
    event["start"]

apphome = AppHomeComponent()
apphome.init_app_home()