from fastapi import APIRouter, Request
from domain.slack.slack_auth import slack_auth
from domain.slack.slack_api import slackAPI
from domain.invite import invite
from schemas import HttpResponse


router = APIRouter()


@router.post("/api/auth/slack/invite")
def handling_invite(reqeust: Request):
    data = {
        d.split("=")[0]: d.split("=")[1]
        for d in reqeust.body().decode("utf-8").split("&")
    }

    user_id = data.get("user_id")

    invite_block = invite.get_invite_blocks(user_id)

    return {"response_type": "in_channel", "blocks": invite_block}


@router.get(
    "/api/auth/slack/callback",
    response_model=HttpResponse,
    response_model_exclude_none=True,
)
def handling_oauth2(request: Request):
    response_url = request.url
    code = request.get("code")
    status = request.get("status")
    client_id = slack_auth.get_client_id()
    client_secret = slack_auth.get_client_secret()
    slackAPI.oauth_v2_access(
        code=code, client_id=client_id, client_secret=client_secret
    )
    return HttpResponse(ok=True)
