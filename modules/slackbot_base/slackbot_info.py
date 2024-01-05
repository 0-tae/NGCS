from flask import Flask, request, make_response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import time
import json
import os

BOT_TOKEN = os.environ['SLACKBOT_TOKEN']
USER_LIST = []
query = "슬랙 봇 테스트"

def get_user_list():
     if len(USER_LIST) < 1 :
      __fetch_user_list__()

      return USER_LIST

def __fetch_user_list__():
      # 유저 목록 초기화
      USER_LIST.clear()
      
      header = get_header()
      
      # api Tier가 높아, 응답을 가져오지 못하는 현상
      
      tried = 0
      while tried < 3:
            response = requests.get("https://slack.com/api/users.list", headers = header).json()
            if response['ok']: break
            print("Retry for user list..")
            time.sleep(3)
      
      # 유저 목록 갱신
      for member in response['members']:
           USER_LIST.append({"user_id": member["id"], "name": member["name"]})
      

def get_header():
      header = {"Content-Type": "application/json;charset=UTF-8",
                 "Authorization": "Bearer "+BOT_TOKEN}
      return header

def get_token():
     return os.environ['SLACKBOT_TOKEN']

def get_channel_id(channel_name):
    header = get_header()
    response = requests.get("https://slack.com/api/conversations.list", headers = header).json()
    
    # 채널 정보들 불러오기
    channels = response['channels']

    # 채널 명과 일치하는 채널 id 추출
    for channel in channels:
          if channel['name'] == channel_name:
                return channel['id']

    return None

def json_prettier(data):
      return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)