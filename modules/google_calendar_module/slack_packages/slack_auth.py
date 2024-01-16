import slack_packages.slack_info as sb_info
import os
import json
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "app_mentions:read",
    "channels:history",
    "channels:read",
    "chat:write",
    "chat:write.customize",
    "chat:write.public",
    "commands",
    "groups:history",
    "groups:read",
    "im:history",
    "im:read",
    "im:write",
    "incoming-webhook",
    "links:write",
    "mpim:history",
    "mpim:read",
    "users:read",
    "users:read.email",
    "users:write",
]
PREFIX = "slack_packages/tokens"
HOST = sb_info.get_host()


class SlackAuth:
    def __init__(self, __credential__=None):
        with open(f"{PREFIX}/credentials.json", "r") as file:
            self.__credential__ = json.load(file)

    def get_client_id(self):
        return self.__credential__.get("client_id")

    def get_client_secret(self):
        return self.__credential__.get("client_secret")

    def get_auth_redirection_url(self, user_id):
        scope = ",".join(map(str, SCOPES))
        state = user_id + datetime.now().isoformat()
        client_id = self.get_client_id()
        return f"https://slack.com/oauth/v2/authorize?scope={scope}&client_id={client_id}&state={state}"


slack_auth = SlackAuth()
