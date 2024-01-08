import slackbot_module.slackbot_info as sb_info
import slackbot_module.slackbot_api as slackAPI
from google_calendar_module.google_calendar_block_builder import block_builder
from google_calendar_module.google_calendar_api import calendarAPI
import copy


class AppHomeComponent:
    __base_view__ = None

    def publish(self, view, user_id):
        slackAPI.app_home_publish(user_id=user_id, view=view)

    def init_app_home(self):
        init_view = self.get_recently_event_view()
        user_list = sb_info.get_user_list()

        for user in user_list:
            self.publish(view=init_view, user_id=user["user_id"])

    def refresh_app_home(self, user_id):
        view = self.get_recently_event_view()
        self.publish(view=view, user_id=user_id)

    # 초기 app_home 구성
    def get_base_view(self):
        if self.__base_view__ is None:
            print("Get initial View")
            initial_block_list = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "안녕하세요. 구글캘린더 봇입니다!:smile:"},
                },
                {
                    "type": "actions",
                    "elements": [
                        block_builder.create_button(
                            "새로 고침:arrows_counterclockwise:", "read_calendar-refresh"
                        ),
                        block_builder.create_button(
                            "휴가 등록", "update_calendar-modal_open_vacation"
                        ),
                        block_builder.create_button(
                            "일정 등록", "update_calendar-modal_open_event"
                        ),
                    ],
                },
            ]

            self.__base_view__ = {"type": "home", "blocks": initial_block_list}

        return self.__base_view__

    # 앱 홈에 띄울 연차, 휴가자 목록
    def get_recently_event_view(self):
        # deepcopy를 해야 하는 게 맞겠죠..?
        composed_view = copy.deepcopy(self.get_base_view())
        composed_view_block = composed_view["blocks"]

        composed_view_block.extend(self.get_today_vacation_block())
        composed_view_block.extend(self.get_today_common_event_block())

        return composed_view

    def get_today_vacation_block(self):
        addr_blocks = []
        day_option = "today"
        event_list = calendarAPI.get_vacation_list(day_option=day_option)
        block_list = block_builder.make_block_list(
            event_list=event_list, action_type="today_vacation", day_option=day_option
        )

        addr_blocks.append(block_builder.create_block_divider())
        addr_blocks.extend(block_list)

        return addr_blocks

    def get_today_common_event_block(self):
        addr_blocks = []
        day_option = "today"
        event_list = calendarAPI.get_common_event_list(day_option=day_option)
        block_list = block_builder.make_block_list(
            event_list=event_list, action_type="today_event", day_option=day_option
        )

        addr_blocks.append(block_builder.create_block_divider())
        addr_blocks.extend(block_list)

        return addr_blocks


apphome = AppHomeComponent()
apphome.init_app_home()
