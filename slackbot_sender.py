import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import slackbot_info as sb_info
from apscheduler.schedulers.background import BackgroundScheduler

CHANNEL_ID = sb_info.get_channel_id('slack-bot')

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


def post_message_user(self, channel_id, user_id):
        response = self.client.chat_postEphemeral(
            channel=channel_id,
            text="안녕하세요 :tada:",
            user=user_id
        )


def post_message(channel_id, text, blocks):
        """
        슬랙 채널에 메세지 보내기
        """
        # chat_postMessage() 메서드 호출
        header = sb_info.get_header()
        data = {"channel":channel_id, "text":text, "blocks":blocks}
        response = requests.post("https://slack.com/api/chat.postMessage", headers = header, json = data)
        print('result:', response.text)

        return response.text