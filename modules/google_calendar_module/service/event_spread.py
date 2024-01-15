import slackbot_module.slackbot_api as slackAPI
import slackbot_module.slackbot_utils as util
from google_calendar_api import calendarAPI
from views.util.block_builder import block_builder
from views.modal.modal_manager import modal_manager
from datetime import datetime
import json

WEEKDAY = ["월", "화", "수", "목", "금", "토", "일"]
SERVICE_DOMAIN = "spread"
ACTION_GROUP = "event_spread"


class EventSpreadService:
    def __init__(self, __event_holder__=dict()):
        self.__event_holder__ = __event_holder__

    def modal_open(self, request_body):
        trigger_id = request_body["trigger_id"]
        user_id = request_body["user"]["id"]
        modal_type = ACTION_GROUP

        modal = modal_manager.get_modal_by_name(modal_name=modal_type, cache_id=user_id)
        response = slackAPI.modal_open(view=modal, trigger_id=trigger_id)

        self.modal_init_spread(view=response["view"], user_id=user_id)

        return "ok", 200

    def spread(self, data: dict, sender_name, reciever_id):
        summary = data.get("summary")
        time = data.get("time")
        event_id = data.get("event_id")

        message_block = self.spread_message_block(
            sender_name=sender_name,
            summary_text=summary,
            time_text=time,
            event_id=event_id,
        )

        slackAPI.post_message(
            channel_id=reciever_id,
            text=f"{sender_name}님이 일정을 전파합니다.",
            blocks=message_block,
        )

    # 모달 제출 후, 채널 및 멤버에 전파
    def modal_spread_submit(self, request_body):
        view = util.UTFToKoreanJSON(request_body["view"])
        user_id = request_body["user"]["id"]
        user_name = util.get_user_name(user_id=user_id)

        # view에서 선택된 값들을 딕셔너리에 추가함
        data = dict()
        for block in view["state"]["values"].values():
            for action_id, action_dict in block.items():
                data[action_id] = util.get_value_from_action(action_dict)

        # static_select에서 text부분을 추출
        summary_with_time = data[f"{ACTION_GROUP}-modal_spread_event_select"][
            "text"
        ].get("text")

        # static_select에서 value부분을 추출하여 event_id 얻어옴
        event_id = data[f"{ACTION_GROUP}-modal_spread_event_select"].get("value")

        if not summary_with_time:
            return "event_not_selected", 405

        # 일정 (19:00 ~ 18:00)
        # 일정
        summary_message = summary_with_time.split("(")[0].strip()

        # (19:00 ~ 18:00) -> 19:00 ~ 18:00
        time = (
            ""
            if len(summary_with_time.split("(")) == 1
            else summary_with_time.split("(")[1].strip().rstrip(")")
        )
        date_time = datetime.strptime(
            data.get(f"{ACTION_GROUP}-modal_spread_date_select"), "%Y-%m-%d"
        )

        today_message = "*(오늘)* " if datetime.now().date() == date_time.date() else ""

        time_message = (
            today_message
            + f"{date_time.year}년 {date_time.month}월 {date_time.day}일 ({WEEKDAY[date_time.weekday()]}) {time}"
        )

        # 전파 대상 리스트(채널 혹은 멤버)
        receivers = (
            data.get(f"{ACTION_GROUP}-modal_spread_users_select")
            if data.get(f"{ACTION_GROUP}-modal_spread_channels_select") == None
            else [
                data.get(f"{ACTION_GROUP}-modal_spread_channels_select"),
            ]
        )

        # data: 메시지 구성에 필요한 데이터
        # sender_name: 전파하는 유저의 이름
        # receiver_id: 전파 대상의 id(채널 혹은 멤버)
        print(receivers)
        for receiver_id in receivers:
            self.spread(
                data={
                    "summary": summary_message,
                    "time": time_message,
                    "event_id": event_id,
                },
                sender_name=user_name,
                reciever_id=receiver_id,
            )

        return {"response_action": "clear"}, 200

    # 처음 모달창의 일정 업데이트
    def modal_init_spread(self, view, user_id):
        now = datetime.now()

        event_options = tuple(
            map(
                lambda e: block_builder.create_option(
                    text=f"{e['summary']} ({self.period_specify(e['start'], e['end'], e['all-day'])})",
                    value=e["id"],
                ),
                calendarAPI.get_event_list(
                    user_id=user_id,
                    day_option="today",
                ),
            )
        )

        modal_object = modal_manager.get_modal_object_by_name(
            modal_name=ACTION_GROUP, cache_id=user_id
        )

        modal = modal_object.update_spread_event_modal(
            original_view=view,
            date=now.strftime("%Y-%m-%d"),
            event_options=event_options,
        )

        response = slackAPI.modal_update(
            view=modal, view_id=view["id"], response_action="update"
        )

        return response

    # 타입이 선택되면 멤버 혹은 채널에 대한 inputbox가 나옴
    def spread_type_selected(self, request_body):
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        selected_option = view["state"]["values"][block_id][action_id][
            "selected_option"
        ]

        target_type = selected_option["value"]

        modal_object = modal_manager.get_modal_object_by_name(
            modal_name=ACTION_GROUP, cache_id=user_id
        )
        modal = modal_object.update_spread_member_type_modal(
            original_view=view, selected_type=target_type
        )

        response = slackAPI.modal_update(
            view=modal, view_id=view_id, response_action="update"
        )

        return response

    def spread_event_selected(self, request_body):
        view = util.UTFToKoreanJSON(request_body["view"])
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        # 선택된 이벤트의 아이디를 가져옴
        selected_event_id = view["state"]["values"][block_id][action_id][
            "selected_option"
        ]["value"]
        event = calendarAPI.find_event_by_id(
            user_id=user_id, event_id=selected_event_id
        )

        # 이벤트 아이디와 이벤트를 딕셔너리에 홀드
        self.event_hold(event_id=selected_event_id, event=event)

        return "ok", 200

    # 일정이 선택되면 해당 일정의 이벤트 리스트를 가져옴
    def spread_date_selected(self, request_body):
        view = util.UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        # 선택된 날짜와 날짜에 해당하는 이벤트 리스트를 가져옴
        selected_date = view["state"]["values"][block_id][action_id]["selected_date"]

        event_options = tuple(
            map(
                lambda e: block_builder.create_option(
                    text=f"{e['summary']} ({self.period_specify(e['start'], e['end'], e['all-day'])})",
                    value=e["id"],
                ),
                calendarAPI.get_event_list(
                    user_id=user_id,
                    day_option=datetime.strptime(selected_date, "%Y-%m-%d"),
                ),
            )
        )

        modal_object = modal_manager.get_modal_by_name(
            modal_name=ACTION_GROUP, cache_id=user_id
        )

        updated_view = modal_object.update_spread_event_modal(
            original_view=view, date=selected_date, event_options=event_options
        )

        response = slackAPI.modal_update(
            view=updated_view, view_id=view_id, response_action="update"
        )

        return response

    # 미완성
    # 이벤트가 선택되면 발생하는 일
    def insert_event(self, request_body):
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        event_id = occured_action["value"]
        event = self.get_holding_event_by_id(event_id=event_id)

        # 만약 가져온 이벤트가 없다면, 예외처리
        if not event:
            return None

        # event_request = Dict {summary, start(datetime), end(datetime), all-day}
        calendarAPI.insert_event(
            event_request={
                "summary": event.get("summary"),
                "description": event.get("description"),
                "start": datetime.fromisoformat(event.get("start")),
                "end": datetime.fromisoformat(event.get("end")),
                "all-day": event.get("all-day"),
            }
        )

        return "ok", 200

    # 메시지 블록 구성
    def spread_message_block(self, sender_name, summary_text, time_text, event_id):
        return block_builder.compose(
            blocks=(
                block_builder.create_block_header(
                    text=f"{sender_name}님이 일정을 전파합니다 :loudspeaker:"
                ),
                block_builder.create_block_divider(),
                block_builder.create_block_header(text="일정 내용"),
                block_builder.create_single_block_section(text=f"- {summary_text}"),
                block_builder.create_block_header(text="시간"),
                block_builder.create_single_block_section(text=f"- {time_text}"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_button(
                            text="내 캘린더에 추가하기",
                            action_id=f"{ACTION_GROUP}-insert_event",
                            value=event_id,
                        ),
                    )
                ),
            )
        )

    def period_specify(self, start, end, all_day):
        if not all_day:
            start_time = datetime.fromisoformat(start).strftime("%H:%M")
            end_time = datetime.fromisoformat(end).strftime("%H:%M")
            return f"{start_time} ~ {end_time}"

        start_date = start.split("-")
        end_date = end.split("-")

        start_datetime = datetime(
            year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2])
        )

        end_datetime = datetime(
            year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2])
        )

        gap = start_datetime - end_datetime
        return "하루 종일" if gap.days == 0 else f"{start} ~ {end}"

    # event_holder 관련 함수들
    def get_event_holder(self) -> dict:
        return self.__event_holder__

    def has_event(self, event_id):
        return event_id != None and self.get_event_holder().get(event_id) != None

    def get_holding_event_by_id(self, event_id):
        return self.get_event_holder().get(event_id)

    def event_hold(self, event_id, event):
        self.get_event_holder().update({event_id: event})

    def event_release(self, event_id):
        if self.has_event(event_id):
            return self.get_event_holder().pop(event_id)


spread_service = EventSpreadService()
