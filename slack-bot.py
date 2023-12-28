from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import json
import os


post_request_header = {
        "token": "<verification token>",
        "team_id": "T123ABC456",
        "team_domain": "my-team",
        "channel_id": "C123ABC456",
        "channel_name": "test",
        "user_id" : "U123ABC456",
        "user_name": "mattjones",
        "response_url":"https://slack.com/callback/123xyz",
        "type": "video"
    }

class SlackAPI:
    """
    슬랙 API 핸들러
    """
    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token = token)


    def get_user_id(self, member_name):
        """
        슬랙 채널ID 조회
        """
        result = self.client.users_list()

        members = result.data['members']

        # 중복된 이름 아직 고려 X
        member = list(filter(lambda m: m["name"] == member_name, members))[0]

        member_id = member["id"]

        return member_id

    def get_channel_id(self, channel_name):
        """
        슬랙 채널ID 조회
        """
        # conversations_list() 메서드 호출
        result = self.client.conversations_list()
        # 채널 정보 딕셔너리 리스트
        channels = result.data['channels']
        # 채널 명이 'test'인 채널 딕셔너리 쿼리
        channel = list(filter(lambda c: c["name"] == channel_name, channels))[0]
        # 채널ID 파싱
        channel_id = channel["id"]

        print('channel_id:',channel_id)

        return channel_id

    def get_message_ts(self, channel_id, query):
        """
        슬랙 채널 내 메세지 조회
        """
        # conversations_history() 메서드 호출
        result = self.client.conversations_history(channel=channel_id)
        # 채널 내 메세지 정보 딕셔너리 리스트
        messages = result.data['messages']
        # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
        message_list = list(filter(lambda m: m["text"]==query, messages))

        message_ts = None

        if len(message_list) > 0:
            message_ts = message_list[0]["ts"]
            print('message_ts:',message_ts)
        else:
            print("Message Not Found")
        

        return message_ts

    def post_thread_message(self, channel_id, message_ts, text):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text = text,
            thread_ts = message_ts
        )
        return result

    def post_message(self, channel_id, text):
        """
        슬랙 채널에 메세지 보내기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text = "슬랙채널 메시지",
            attachments = [
        {
            "text": "Choose a game to play",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "game",
                    "text": "Chess",
                    "type": "button",
                    "value": "chess"
                },
                {
                    "name": "game",
                    "text": "Falken's Maze",
                    "type": "button",
                    "value": "maze"
                },
                {
                    "name": "game",
                    "text": "Thermonuclear War",
                    "style": "danger",
                    "type": "button",
                    "value": "war",
                    "confirm": {
                        "title": "Are you sure?",
                        "text": "Wouldn't you prefer a good game of chess?",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                }
            ]
        }
    ]
        )

        print('result:', result)

        return result

    def post_message_user(self, channel_id, user_id):
        response = self.client.chat_postEphemeral(
            channel=channel_id,
            text="안녕하세요 :tada:",
            user=user_id

        )

    def get_modal(self):
        response = self.client.client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "view_4",
                "title": {"type": "plain_text", "text": "견적서 출력"},
                "submit": {"type": "plain_text", "text": "견적서 생성하기"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "making_estimate1",
                        "element": {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "인입 경로를 선택해주세요.",
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "1회",
                                    },
                                    "value": "1회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2회",
                                    },
                                    "value": "2회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3회",
                                    },
                                    "value": "3회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "4회",
                                    },
                                    "value": "4회",
                                },
                            ],
                            "action_id": "input_request_route",
                        },
                        "label": {"type": "plain_text", "text": "인입 경로"},
                    },
                    {
                        "type": "input",
                        "block_id": "making_estimate2",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "input_company_name",
                        },
                        "label": {"type": "plain_text", "text": "회사명/고객명"},
                    },
                    {
                        "type": "input",
                        "block_id": "making_estimate3",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "input_company_email",
                        },
                        "label": {"type": "plain_text", "text": "회사 이메일(없으면 '-'라고 적기)"},
                    },
                    {
                        "type": "input",
                        "block_id": "making_estimate4",
                        "element": {
                            "type": "radio_buttons",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "매주",
                                    },
                                    "value": "매주",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "격주",
                                    },
                                    "value": "격주",
                                },
                            ],
                            "action_id": "input_week_period",
                        },
                        "label": {"type": "plain_text", "text": "매주/격주 여부"},
                    },
                    {
                        "type": "input",
                        "block_id": "making_estimate5",
                        "element": {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "주당 횟수를 선택해주세요.",
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "1회",
                                    },
                                    "value": "1회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2회",
                                    },
                                    "value": "2회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3회",
                                    },
                                    "value": "3회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "4회",
                                    },
                                    "value": "4회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "5회",
                                    },
                                    "value": "5회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "6회",
                                    },
                                    "value": "6회",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "7회",
                                    },
                                    "value": "7회",
                                },
                            ],
                            "action_id": "input_times_per_week",
                        },
                        "label": {"type": "plain_text", "text": "주당 청소 횟수"},
                    },
                    {
                        "type": "input",
                        "block_id": "making_estimate6",
                        "element": {
                            "type": "radio_buttons",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2시간",
                                    },
                                    "value": "2시간",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3시간",
                                    },
                                    "value": "3시간",
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "4시간",
                                    },
                                    "value": "4시간",
                                },
                            ],
                            "action_id": "input_times_per_service",
                        },
                        "label": {"type": "plain_text", "text": "1회당 청소 시간"},
                    },
                ],
            },
        )


token = os.environ['SLACKBOT_TOKEN']
slack = SlackAPI(token)

channel_name = "slack-bot" 
user_name = "choiyt3465"
query = "슬랙 봇 테스트"
text =  '''
        *자동 생성 문구 테스트*
        '''

try:
    workspace_id = "T06B4PUFFL7"
    channel_id = slack.get_channel_id(channel_name = channel_name)
    # user_id = slack.get_user_id(user_name)
    message_ts = slack.get_message_ts(channel_id = channel_id, query = query)
    
    # 수행
    slack.post_thread_message(channel_id, message_ts, text)
    slack.post_message(channel_id, text)
    slack.get_modal()
    # slack.post_message_user(channel_id = channel_id, user_id = user_id)

except SlackApiError as e:
    print(f"Error is.. : {e}")