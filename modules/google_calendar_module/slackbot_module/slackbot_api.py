import requests
import slackbot_module.slackbot_info as sb_info
import json

HEADER = sb_info.get_header()


def get_message_ts(channel_id, query):
    """
    슬랙 채널 내 메세지 조회
    """
    # conversations_history() 메서드 호출
    result = self.client.conversations_history(channel=channel_id)
    # 채널 내 메세지 정보 딕셔너리 리스트
    messages = result.data["messages"]
    # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
    message_list = list(filter(lambda m: m["text"] == query, messages))

    message_ts = None

    if len(message_list) > 0:
        message_ts = message_list[0]["ts"]
        print("message_ts:", message_ts)
    else:
        print("Message Not Found")

    return message_ts


def post_thread_message(channel_id, message_ts, text):
    """
    슬랙 채널 내 메세지의 Thread에 댓글 달기
    """
    # chat_postMessage() 메서드 호출
    result = self.client.chat_postMessage(
        channel=channel_id, text=text, thread_ts=message_ts
    )
    return result


def post_message_user(channel_id, user_id, text, blocks):
    data = {"channel": channel_id, "text": text, "blocks": blocks}
    response = requests.post(
        "https://slack.com/api/chat.postEphemeral", headers=HEADER, json=data
    )

    return response.text


# 슬랙 채널에 메세지 보내기
def post_message(channel_id, text, blocks):
    data = {"channel": channel_id, "text": text, "blocks": blocks}
    response = requests.post(
        "https://slack.com/api/chat.postMessage", headers=HEADER, json=data
    )
    print(json_prettier(response.json()))
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
    return response.json()


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)
