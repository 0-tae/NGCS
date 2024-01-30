from _slack.slack_api import slackAPI
from _google.google_calendar_api import calendarAPI
import _slack.slack_utils as util
from view.util.modal_manager import modal_manager
from datetime import datetime


ACTION_GROUP = "event_insert"


class EventInsert:
    def modal_event_submit(self, request_body):
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        data = dict()

        for block in view["state"]["values"].values():
            for action_id, action_dict in block.items():
                data[action_id] = util.get_value_from_action(action_dict)

        request = self.make_google_calendar_api_event_insert_request(data=data)

        # 캘린더에 업데이트
        calendarAPI.insert_event(event_request=request, user_id=user_id)

        return {"response_action": "clear"}

    def allday_changed(self, request_body):
        # +기호 이슈로 인한 디코딩 코드 추가
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]
        user_id = request_body["user"]["id"]

        selected_checkbox = view["state"]["values"][block_id][action_id][
            "selected_options"
        ]

        # 선택된 체크박스의 갯수가 1개 이상이면 all-day
        all_day = True if len(selected_checkbox) > 0 else False

        # "event" 모달을 가져옴, 모달의 캐시 아이디는 user_id로 함
        modal_object = modal_manager.get_modal_object_by_name(
            ACTION_GROUP, cache_id=user_id
        )

        modal = modal_object.update_modal(original_view=view, all_day=all_day)

        response = slackAPI.modal_update(
            view=modal, view_id=view_id, response_action="update"
        )

        return {"ok": True}

    def modal_open(self, request_body):
        trigger_id = request_body["trigger_id"]
        user_id = request_body["user"]["id"]

        modal = modal_manager.get_modal_by_name(
            modal_name=ACTION_GROUP, cache_id=user_id
        )
        response = slackAPI.modal_open(view=modal, trigger_id=trigger_id)

        return {"ok": True}

    def make_google_calendar_api_event_insert_request(self, data):
        request = dict()

        # google_calendar api 표준 : Dict {summary, start, end, all-day}
        start_time = data.get(f"{ACTION_GROUP}-modal_event_start_time")
        end_time = data.get(f"{ACTION_GROUP}-modal_event_end_time")
        date = data.get(f"{ACTION_GROUP}-modal_event_date")

        summary = data.get(f"{ACTION_GROUP}-modal_event_summary")
        description = data.get(f"{ACTION_GROUP}-modal_event_description")
        all_day = (
            True if len(data.get(f"{ACTION_GROUP}-modal_event_allday")) > 0 else False
        )

        # 2023-01-09
        # 연차일 경우는 date, 이외는 dateTime
        (start, end) = (
            (
                datetime.strptime(date, "%Y-%m-%d"),
                datetime.strptime(date, "%Y-%m-%d"),
            )
            if all_day
            else (
                datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M"),
                datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M"),
            )
        )

        # 최용태 - 연차
        request["summary"] = summary
        request["start"] = start
        request["end"] = end
        request["description"] = description
        request["all-day"] = all_day

        return request


event_insert_service = EventInsert()
