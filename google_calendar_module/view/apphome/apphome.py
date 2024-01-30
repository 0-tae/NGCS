from domain.slack.slack_api import slackAPI
from view.util.block_builder import block_builder
from domain.google.google_calendar_api import calendarAPI
from domain.google.google_auth import google_auth
import copy

OAUTH_URL = google_auth.get_auth_url()


class AppHomeComponent:
    __base_view__ = None

    def publish(self, view, user_id):
        slackAPI.app_home_publish(user_id=user_id, view=view)

    def refresh_single_app_home(self, user_id):
        view = None
        if not google_auth.is_certificated(user_id=user_id):
            view = self.get_non_user_view()
        else:
            view = self.get_recently_event_view(user_id)

        self.publish(view=view, user_id=user_id)

    def refresh(self, request_body):
        user_id = request_body["user"]["id"]
        apphome.refresh_single_app_home(user_id=user_id)
        return {"ok": True}

    def init_app_home(self):
        user_list = slackAPI.get_user_list()
        for user in user_list:
            user_id = user["user_id"]
            if not google_auth.is_certificated(user_id=user_id):
                init_view = self.get_non_user_view()
            else:
                init_view = self.get_recently_event_view(user_id)
            self.publish(view=init_view, user_id=user_id)

    # 초기 app_home 구성
    def get_base_view(self):
        print("Get initial View")

        initial_block_list = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "안녕하세요. 구글 캘린더 봇입니다! :smile:"},
            },
            {
                "type": "actions",
                "elements": [
                    block_builder.create_button(
                        text="새로 고침 :arrows_counterclockwise:",
                        action_id="apphome-refresh",
                    ),
                    block_builder.create_button(
                        text="휴가 등록", action_id="vacation_insert-modal_open_vacation"
                    ),
                    block_builder.create_button(
                        text="일정 등록", action_id="event_insert-modal_open_event"
                    ),
                    block_builder.create_button(
                        text="내 일정 전파하기", action_id="event_spread-modal_open_spread"
                    ),
                ],
            },
        ]

        self.__base_view__ = {"type": "home", "blocks": initial_block_list}

        return self.__base_view__

    def get_non_user_view(self):
        non_user_block_list = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "안녕하세요. 구글캘린더 봇입니다! :smile:"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "먼저, *구글 캘린더를 Slack에 연동* 해주세요"},
            },
            {
                "type": "actions",
                "elements": [
                    block_builder.create_url_button(
                        text="구글 캘린더에 연동하기",
                        action_id="access_calendar-register",
                        url=OAUTH_URL,
                    ),
                ],
            },
        ]

        self.__base_view__ = {
            "type": "home",
            "blocks": non_user_block_list,
        }

        return self.__base_view__

    # 앱 홈에 띄울 연차, 휴가자 목록
    def get_recently_event_view(self, user_id):
        # deepcopy를 해야 하는 게 맞겠죠..?
        composed_view = copy.deepcopy(self.get_base_view())
        composed_view_block = composed_view["blocks"]

        composed_view_block.extend(self.get_today_vacation_block(user_id))
        composed_view_block.extend(self.get_today_common_event_block(user_id))

        return composed_view

    def get_today_vacation_block(self, user_id):
        addr_blocks = []
        day_option = "today"
        event_list = calendarAPI.get_vacation_list(user_id, day_option=day_option)
        block_list = block_builder.make_event_block_list(
            event_list=event_list, action_type="today_vacation", day_option=day_option
        )

        addr_blocks.append(block_builder.create_block_divider())
        addr_blocks.extend(block_list)

        return addr_blocks

    def get_today_common_event_block(self, user_id):
        addr_blocks = []
        day_option = "today"
        event_list = calendarAPI.get_common_event_list(user_id, day_option=day_option)
        block_list = block_builder.make_event_block_list(
            event_list=event_list, action_type="today_event", day_option=day_option
        )

        addr_blocks.append(block_builder.create_block_divider())
        addr_blocks.extend(block_list)

        return addr_blocks


apphome = AppHomeComponent()
apphome.init_app_home()
