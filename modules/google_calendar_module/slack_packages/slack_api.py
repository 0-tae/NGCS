import requests
import slack_packages.slack_info as sb_info
import slack_packages.slack_utils as util
import json

HEADER = sb_info.get_header()


def oauth_v2_access(code, client_id, client_secret):
    data = {"code": code, "client_id": client_id, "client_secret": client_secret}
    response = requests.post("https://slack.com/api/oauth.v2.access", data=data)

    return response.text


# 슬랙 채널에 메세지 보내기
def post_message(channel_id, text, blocks):
    data = {"channel": channel_id, "text": text, "blocks": blocks}
    response = requests.post(
        "https://slack.com/api/chat.postMessage", headers=HEADER, json=data
    )

    return response.text


def modal_open(view, trigger_id):
    data = {"trigger_id": trigger_id, "view": view}

    response = requests.post(
        "https://slack.com/api/views.open", headers=HEADER, json=data
    )

    return response.json()


def modal_update(view, view_id, response_action):
    data = {"view": view, "view_id": view_id, "response_action": response_action}

    response = requests.post(
        "https://slack.com/api/views.update", headers=HEADER, json=data
    )

    return response.text


def app_home_publish(user_id, view):
    data = {"user_id": user_id, "view": view}
    response = requests.post(
        "https://slack.com/api/views.publish", headers=HEADER, json=data
    )

    return response.text


def get_users_list():
    response = requests.get("https://slack.com/api/users.list", headers=HEADER)
    return response.json()


def get_channels_list():
    response = requests.get("https://slack.com/api/conversations.list", headers=HEADER)
    return response.text
