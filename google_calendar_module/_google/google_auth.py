import json
import os
from _slack.slack_auth import slack_auth
from requests_oauthlib import OAuth2Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
HOST = slack_auth.get_from_credential("host")
PREFIX = "_google/tokens"


class GoogleAuth:
    def __init__(
        self,
        __temp_user__=None,
        __temp_state__=None,
    ):
        self.__temp_user__ = __temp_user__
        self.__temp_state__ = __temp_state__

    def get_auth_url(self):
        with open(f"{PREFIX}/credentials.json", "r") as file:
            credentials = json.load(file)["web"]

        client_config = {
            "token_url": credentials["token_uri"],
            "client_secret": credentials["client_secret"],
            "auth_uri": credentials["auth_uri"],
            "client_id": credentials["client_id"],
        }

        oauth2_session = OAuth2Session(
            client_id=client_config["client_id"],
            scope=SCOPES,
            redirect_uri=self.get_redirect_url(),
        )

        authorization_url, state = oauth2_session.authorization_url(
            client_config["auth_uri"],
            # offline for refresh token
            # force to always make user click authorize
            access_type="offline",
            prompt="select_account",
        )

        # 유저 상태 임시저장
        self.set_temp_state(state)
        print("request state:", state)
        return authorization_url

    def user_register(self, auth_response_url, user_id):
        with open(f"{PREFIX}/credentials.json", "r") as file:
            credentials = json.load(file)["web"]

        client_config = {
            "token_url": credentials["token_uri"],
            "client_secret": credentials["client_secret"],
            "auth_uri": credentials["auth_uri"],
            "client_id": credentials["client_id"],
        }

        google = OAuth2Session(
            client_config["client_id"],
            redirect_uri=self.get_redirect_url(),
            state=self.get_temp_state(),
        )

        token = google.fetch_token(
            client_config["token_url"],
            client_secret=client_config["client_secret"],
            authorization_response=auth_response_url,
        )

        token_dict = dict()

        token_dict.update({"client_id": client_config["client_id"]})
        token_dict.update({"client_secret": client_config["client_secret"]})

        for key, value in token.items():
            token_dict.update({key: value})

        with open(f"{PREFIX}/{user_id}-token.json", "w") as new_token:
            new_token.write(json.dumps(token_dict))

    def is_certificated(self, user_id):
        return True if self.get_credentials(user_id=user_id) != None else False

    # 유저가 한 번 인증하면 서버에 유저 이름으로 PREFIX를 가진 Token을 저장
    def get_credentials(self, user_id):
        current_creds = None

        if os.path.exists(f"{PREFIX}/{user_id}-token.json"):
            current_creds = Credentials.from_authorized_user_file(
                f"{PREFIX}/{user_id}-token.json", SCOPES
            )

        if not current_creds:
            return None

        # If there are no (valid) credentials available, let the user log in.
        if not current_creds.valid:
            if current_creds and current_creds.expired and current_creds.refresh_token:
                current_creds.refresh(Request())
            # Save the credentials for the next run
            self.write_token(credential=current_creds, user_id=user_id)

        return current_creds

    def write_token(self, credential, user_id):
        with open(f"{PREFIX}/{user_id}-token.json", "w") as token:
            token.write(credential.to_json())

    # 버튼 -> google 로그인 -> redirect 로 인한 user_id 정보 손실 방지 임시 방편
    def set_temp_state(self, state):
        self.__temp_state__ = state

    def get_temp_state(self):
        return self.__temp_state__

    def set_temp_user(self, user_id):
        self.__temp_user__ = user_id

    def get_temp_user(self):
        return self.__temp_user__

    def get_redirect_url(self):
        return HOST + "/api/auth/google/callback"

    def get_prefix():
        return PREFIX

    def get_scopes():
        return SCOPES


google_auth = GoogleAuth()
