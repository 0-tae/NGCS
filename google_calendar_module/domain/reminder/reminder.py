from datetime import datetime
import _slack.slack_api as slackAPI
import _slack.slack_utils as util
from _google.google_calendar_api import calendarAPI
from domain.reminder.scheduler import scheduler
from view.util.block_builder import block_builder


# 오늘의 이벤트를 알림
def today_events_post_all():
    users = slackAPI.get_user_list()

    for user in users:
        user_id = user["user_id"]
        user_name = util.get_user_name(user_id)
        common_event_list = calendarAPI.get_common_event_list(user_id=user_id)
        vacation_list = calendarAPI.get_vacation_list(user_id=user_id)

        composed_blocks = list()

        hello_text = f"{user_name}님 오늘의 일정 알려 드립니다.:blush:"

        hello_block = block_builder.create_single_block_section(hello_text)
        date_block = block_builder.create_block_header(
            f"{datetime.now().year}년 {datetime.now().month}월 {datetime.now().day}일"
        )
        vacation_blocks = block_builder.make_event_block_list(
            event_list=vacation_list, action_type="today_vacation", day_option="today"
        )
        commmon_event_blocks = block_builder.make_event_block_list(
            event_list=common_event_list, action_type="today_event", day_option="today"
        )

        composed_blocks = block_builder.compose(
            blocks=(
                block_builder.create_single_block_section(hello_text),
                block_builder.create_block_header(
                    f"{datetime.now().year}년 {datetime.now().month}월 {datetime.now().day}일"
                ),
                block_builder.make_event_block_list(
                    event_list=vacation_list,
                    action_type="today_vacation",
                    day_option="today",
                ),
                block_builder.make_event_block_list(
                    event_list=common_event_list,
                    action_type="today_event",
                    day_option="today",
                ),
            )
        )

        slackAPI.post_message(
            channel_id=user_id, text=hello_text, blocks=composed_blocks
        )

    return {"ok":True}


scheduler.add_cron_scheduler("alert_event", today_events_post_all, hour=17, minute=30)
scheduler.execute()
