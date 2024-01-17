import _slack.slack_utils as util
from _slack.slack_api import slackAPI
from view.util.modal_manager import modal_manager
from _google.google_calendar_api import calendarAPI
from datetime import datetime

ACTION_GROUP = "vacation_insert"


class VacationInsert:
    def modal_vacation_submit(self, request_body):
        # +기호 이슈로 인한 디코딩 코드 추가
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        data = dict()

        for block in view["state"]["values"].values():
            for action_id, action_dict in block.items():
                data[action_id] = util.get_value_from_action(action_dict)

        data["requested_user_id"] = user_id

        request = self.make_google_calendar_api_vacation_insert_request(data=data)

        if request == None:
            return {
                "response_action": "update",
                "view": modal_manager.get_modal_object_by_name(
                    modal_name=ACTION_GROUP
                ).get_modal(),
            }, 200

        # 캘린더에 업데이트
        calendarAPI.insert_event(event_request=request, user_id=user_id)
        # event_spread.spread()

        return {"response_action": "clear"}

    def vacation_type_selected(self, request_body):
        # +기호 이슈로 인한 디코딩 코드 추가
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        selected_option = view["state"]["values"][block_id][action_id][
            "selected_option"
        ]

        vacation_type = selected_option["value"]

        modal_object = modal_manager.get_modal_object_by_name(
            modal_name=ACTION_GROUP, cache_id=user_id
        )
        updated_view = modal_object.update_modal(
            original_view=view, vacation_type=vacation_type
        )

        response = slackAPI.modal_update(
            view=updated_view, view_id=view_id, response_action="update"
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

    def make_google_calendar_api_vacation_insert_request(self, data):
        request = dict()

        # google_calendar api 표준 : Dict {summary, start, end, all-day}
        start_time = data.get(f"{ACTION_GROUP}-modal_vacation_start_time")
        end_time = data.get(f"{ACTION_GROUP}-modal_vacation_end_time")
        start_date = data.get(f"{ACTION_GROUP}-modal_vacation_start_date")
        end_date = data.get(f"{ACTION_GROUP}-modal_vacation_end_date")
        vacation_type_option = data.get(f"{ACTION_GROUP}-modal_vacation_type_select")
        selected_user = data.get(f"{ACTION_GROUP}-modal_vacation_member_select")
        requested_user = data.get("requested_user_id")

        vacation_type = vacation_type_option["text"]["text"]
        # 휴가를 선택하지 않았을 때 예외처리
        if vacation_type_option == None:
            return None

        # 유저가 선택되지 않았다면 신청자 본인
        user_name = util.get_user_name(
            selected_user if selected_user != None else requested_user
        )

        # 2023-01-09
        # 연차일 경우는 date, 이외는 dateTime
        (start, end) = (
            (
                datetime.strptime(start_date, "%Y-%m-%d"),
                datetime.strptime(end_date, "%Y-%m-%d"),
            )
            if vacation_type == "연차"
            else (
                datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M"),
                datetime.strptime(f"{start_date} {end_time}", "%Y-%m-%d %H:%M"),
            )
        )

        # 최용태 - 연차
        request["summary"] = (
            user_name
            + "-"
            + self.vacation_specify(
                vacation_type=vacation_type,
                start=start,
            )
        )

        request["start"] = start
        request["end"] = end
        request["description"] = None  # 사용하지 않음
        request["all-day"] = True if vacation_type == "연차" else False

        return request

    def vacation_specify(self, vacation_type, start: datetime):
        AM_START = 9
        PM_START = 12

        prefix = ""

        if vacation_type == "반차":
            prefix = "오전 " if start.hour < PM_START else "오후 "

        return prefix + vacation_type


vacation_insert_service = VacationInsert()
