import slack_packages.slack_api as slackAPI
import time
import json
import os

BOT_TOKEN = os.environ["SLACKBOT_TOKEN"]
USER_LIST = []
query = "슬랙 봇 테스트"


def get_oauth_url():
    return get_host() + "/link"


def get_host():
    return "https://d681-221-158-214-203.ngrok-free.app"


def get_header():
    header = {
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": "Bearer " + BOT_TOKEN,
    }
    return header


def get_user_list():
    if len(USER_LIST) < 1:
        __fetch_user_list__()

    return USER_LIST


def __fetch_user_list__():
    # 유저 목록 초기화
    USER_LIST.clear()

    # api Tier가 높아, 응답을 가져오지 못하는 현상
    tried = 0
    while tried < 3:
        response = slackAPI.get_users_list()
        if response["ok"]:
            break
        print("Retry for user list..")
        time.sleep(3)

    # 유저 목록 갱신
    for member in response["members"]:
        if not (member["deleted"] or member["is_bot"] or member["id"] == "USLACKBOT"):
            USER_LIST.append(
                {
                    "user_id": member["id"],
                    "real_name": member["real_name"],
                    "name": member["name"],
                    "email": member["profile"]["email"],
                }
            )


def get_user_info(user_id, info):
    return list(filter(lambda user: user["user_id"] == user_id, USER_LIST))[0].get(info)


def get_token():
    return os.environ["SLACKBOT_TOKEN"]


def get_channel_id(channel_name):
    response = slackAPI.get_channels_list()

    # 채널 정보들 불러오기
    channels = response["channels"]

    # 채널 명과 일치하는 채널 id 추출
    for channel in channels:
        if channel["name"] == channel_name:
            return channel["id"]

    return None


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)
