from view.util.block_builder import block_builder
from domain.slack.slack_auth import slack_auth

ACTION_GROUP = "invite"


class Invite:
    def get_invite_blocks(user_id):
        return block_builder.compose(
            blocks=(
                block_builder.create_block_header("당신을 초대합니다"),
                block_builder.create_single_block_section(
                    "이 슬랙봇을 설치해서 구글 캘린더를 슬랙과 연동하세요"
                ),
                block_builder.create_single_block_section(
                    text="설치하기: " + slack_auth.get_auth_redirection_url(user_id),
                ),
            )
        )


invite = Invite
