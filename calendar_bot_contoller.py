from flask import Flask, request, make_response
import requests
import slackbot_info as sb_info
import slackbot_sender as sender

CHANNEL_ID = sb_info.get_channel_id('slack-bot')

app = Flask(__name__)

class AppHomeComponent:
    def publish_app_home(self):
        view = self.get_init_view()

        header = sb_info.get_header()

        user_list = sb_info.get_user_list()

        for user in user_list:
            data = {"user_id": user["user_id"], "view": view}
            response = requests.post("https://slack.com/api/views.publish", headers = header, json = data)
            print("user_id:",user["user_id"], response)

    # 초기 app_home 구성
    def get_init_view(self):
        view = {
        "type":"home",
        "blocks":[
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
    ]}

        return view

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
    request_body = request.get_json()
    sender.post_message(CHANNEL_ID, request_body, None)
    request_body

apphome = AppHomeComponent()
apphome.publish_app_home()