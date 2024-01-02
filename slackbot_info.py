from flask import Flask, request, make_response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import json
import os


BOT_TOKEN = os.environ['SLACKBOT_TOKEN']
slackAPI = WebClient(token = BOT_TOKEN)
user_name = "choiyt3465"
query = "슬랙 봇 테스트"
text =  '''
        *자동 생성 문구 테스트*
        '''


def get_header():
      header = {"Content-Type": "application/json;charset=UTF-8",
                 "Authorization": "Bearer "+BOT_TOKEN}

      return header

def get_token():
     
     return os.environ['SLACKBOT_TOKEN']

def get_channel_id(channel_name):
    """
    슬랙 채널ID 조회
    """

    header = get_header()
    response = requests.get("https://slack.com/api/conversations.list", headers = header).json()
    print(response)
    # 채널 정보들 불러오기
    channels = response['channels']

    # 채널 명과 일치하는 채널 id 추출
    for channel in channels:
          if channel['name'] == channel_name:
                return channel['id']

    return None