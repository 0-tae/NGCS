import requests
import time
from domain.slack.slack_auth import slack_auth

HEADER = slack_auth.get_header()
USER_LIST = []


class SlackAPI:
    def oauth_v2_access(self, code, client_id, client_secret):
        data = {"code": code, "client_id": client_id, "client_secret": client_secret}
        response = requests.post("https://slack.com/api/oauth.v2.access", data=data)

        return response.text

    # 슬랙 채널에 메세지 보내기
    def post_message(self, channel_id, text, blocks):
        data = {"channel": channel_id, "text": text, "blocks": blocks}
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=HEADER,
            json=data,
        )

        return response.text

    def modal_open(self, view, trigger_id):
        data = {"trigger_id": trigger_id, "view": view}

        response = requests.post(
            "https://slack.com/api/views.open", headers=HEADER, json=data
        )

        return response.json()

    def modal_update(self, view, view_id, response_action):
        data = {"view": view, "view_id": view_id, "response_action": response_action}

        response = requests.post(
            "https://slack.com/api/views.update",
            headers=HEADER,
            json=data,
        )

        return response.text

    def app_home_publish(self, user_id, view):
        data = {"user_id": user_id, "view": view}
        response = requests.post(
            "https://slack.com/api/views.publish",
            headers=HEADER,
            json=data,
        )

        return response.text

    def get_users_list(self):
        response = requests.get("https://slack.com/api/users.list", headers=HEADER)
        return response.json()

    def get_channels_list(self):
        response = requests.get(
            "https://slack.com/api/conversations.list", headers=HEADER
        )
        return response.text

    def get_user_list(self):
        if len(USER_LIST) < 1:
            self.__fetch_user_list__()

        return USER_LIST

    def __fetch_user_list__(self):
        # 유저 목록 초기화
        USER_LIST.clear()

        # api Tier가 높아, 응답을 가져오지 못하는 현상
        tried = 0
        while tried < 5:
            response = slackAPI.get_users_list()
            if response["ok"]:
                break
            print("Retry for user list..")
            time.sleep(3)
            tried += 1

        if not response["ok"]:
            raise RuntimeError("UserList를 가져오지 못함")
        # 유저 목록 갱신
        for member in response["members"]:
            if not (
                member["deleted"] or member["is_bot"] or member["id"] == "USLACKBOT"
            ):
                USER_LIST.append(
                    {
                        "user_id": member["id"],
                        "real_name": member["real_name"],
                        "name": member["name"],
                        "email": member["profile"]["email"],
                    }
                )

    def __get_header__(self):
        return self.__header__

    def get_user_info(self, user_id, info):
        return list(filter(lambda user: user["user_id"] == user_id, USER_LIST))[0].get(
            info
        )


slackAPI = SlackAPI()
