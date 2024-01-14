import slackbot_module.slackbot_api as slackAPI
import slackbot_module.slackbot_info as slackInfo
from google_calendar_api import calendarAPI
from views.block_builder import block_builder
from views.modal_manager import modal_manager
import json
from datetime import datetime

WEEKDAY = ["월", "화", "수", "목", "금", "토", "일"]


class EventSpreadService:
    # 메시지 블록 구성
    def spread_message_block(self, sender_name, summary_text, time_text):
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
                            action_id="update_calendar-insert_event",
                        ),
                    )
                ),
            )
        )

    def spread(self, data: dict, sender_name, reciever_id):
        summary = data.get("summary")
        time = data.get("time")

        message_block = self.spread_message_block(
            sender_name=sender_name,
            summary_text=summary,
            time_text=time,
        )

        slackAPI.post_message(
            channel_id=reciever_id,
            text=f"{sender_name}님이 일정을 전파합니다.",
            blocks=message_block,
        )

    # 모달 제출 후, 채널 및 멤버에 전파
    def modal_spread_submit(self, request_body, action_name, callback_id):
        view = UTFToKoreanJSON(request_body["view"])
        user_id = request_body["user"]["id"]
        user_name = get_user_name(user_id=user_id)

        # view에서 선택된 값들을 딕셔너리에 추가함
        data = dict()
        for block in view["state"]["values"].values():
            for action_id, action_dict in block.items():
                data[action_id] = get_value_from_action(action_dict)

        summary_with_time = data.get("spread_calendar-modal_spread_event_select")

        if not summary_with_time:
            return "please select your event", 405

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
            data.get("spread_calendar-modal_spread_date_select"), "%Y-%m-%d"
        )

        today_message = "*(오늘)* " if datetime.now().date() == date_time.date() else ""

        print("TIME?:", date_time.weekday())

        time_message = (
            today_message
            + f"{date_time.year}년 {date_time.month}월 {date_time.day}일 ({WEEKDAY[date_time.weekday()]}) {time}"
        )

        # 전파 대상 리스트(채널 혹은 멤버)
        receivers = (
            data.get("spread_calendar-modal_spread_users_select")
            if data.get("spread_calendar-modal_spread_channels_select") == None
            else [
                data.get("spread_calendar-modal_spread_channels_select"),
            ]
        )

        # data: 메시지 구성에 필요한 데이터
        # sender_name: 전파하는 유저의 이름
        # receiver_id: 전파 대상의 id(채널 혹은 멤버)
        print(receivers)
        for receiver_id in receivers:
            self.spread(
                data={"summary": summary_message, "time": time_message},
                sender_name=user_name,
                reciever_id=receiver_id,
            )

        return {"response_action": "clear"}, 200

    # 처음 모달창의 일정 업데이트
    def modal_init_spread(self, view, user_id):
        now = datetime.now()
        event_list = list(
            map(
                lambda e: f"{e['summary']} ({self.period_specify(e['start'], e['end'], e['all-day'])})",
                calendarAPI.get_event_list(user_id=user_id, day_option=now),
            )
        )

        modal_object = modal_manager.get_modal_object_by_name(modal_name="spread",cache_id=user_id)
        
        modal = modal_object.update_spread_event_modal(
            original_view=view, date=now.strftime("%Y-%m-%d"), event_list=event_list
        )

        return slackAPI.modal_update(
            view=modal, view_id=view["id"], response_action="update"
        )

    # 타입이 선택되면 멤버 혹은 채널에 대한 inputbox가 나옴
    def spread_type_selected(self, request_body, action_name):
        view = UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        selected_option = view["state"]["values"][block_id][action_id][
            "selected_option"
        ]

        target_type = selected_option["value"]

        modal_object = modal_manager.get_modal_object_by_name(modal_name="spread", cache_id=user_id)
        modal = modal_object.update_spread_member_type_modal(
            original_view=view, selected_type=target_type
        )
        
        slackAPI.modal_update(
            view=modal, view_id=view_id, response_action="update"
        )

        return "ok", 200

    # 일정이 선택되면 해당 일정의 이벤트 리스트를 가져옴
    def spread_date_selected(self, request_body, action_name):
        print(json_prettier(request_body))

        view = UTFToKoreanJSON(request_body["view"])
        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        # 선택된 날짜와 날짜에 해당하는 이벤트 리스트를 가져옴
        selected_date = view["state"]["values"][block_id][action_id]["selected_date"]

        event_list = list(
            map(
                lambda e: f"{e['summary']} ({self.period_specify(e['start'], e['end'], e['all-day'])})",
                calendarAPI.get_event_list(
                    user_id=user_id,
                    day_option=datetime.strptime(selected_date, "%Y-%m-%d"),
                ),
            )
        )

        updated_view = modal_builder.update_spread_event_modal(
            original_view=view, date=selected_date, event_list=event_list
        )

        slackAPI.modal_update(
            view=updated_view, view_id=view_id, response_action="update"
        )
        return "ok", 200

    def spread_event_selected(self, request_body, action_name):
        view = UTFToKoreanJSON(request_body["view"])

        view_id = view["id"]
        user_id = request_body["user"]["id"]

        occured_action = request_body["actions"][0]
        action_id = occured_action["action_id"]
        block_id = occured_action["block_id"]

        # 선택된 날짜와 날짜에 해당하는 이벤트 리스트를 가져옴
        selected_option = view["state"]["values"][block_id][action_id][
            "selected_option"
        ]

        updated_view = modal_builder.update_modal_for_set_callback_id(
            original_view=view,
            modal_name="spread",
            title="일정 전파하기",
            new_callback_id=f"{view['callback_id']}-{selected_option}",
        )

        print(
            slackAPI.modal_update(
                view=updated_view, view_id=view_id, response_action="update"
            )
        )

        return 200, "ok"

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

    def add_to_calendar(
        self,
    ):
        slackAPI.post_message()  # 나에게 일정을 추가했다고 알림
        return


def get_value_from_action(action_dict):
    action_type_dict = {
        "timepicker": ["selected_time"],
        "datepicker": ["selected_date"],
        "static_select": ["selected_option", "text", "text"],
        "users_select": ["selected_user"],
        "plain_text_input": ["value"],
        "checkboxes": ["selected_options"],
        "radio_buttons": ["selected_option", "text", "text"],
        "multi_users_select": ["selected_users"],
        "channels_select": ["selected_channel"],
    }

    keys = action_type_dict[action_dict["type"]]

    # selected_option, text, text
    value = get_dictionary_value_for_depth(
        keys=keys, dictionary=action_dict, current_depth=0
    )

    return value


def get_dictionary_value_for_depth(keys, dictionary, current_depth):
    if dictionary.get(keys[current_depth]) == None:
        return None

    current_dictionary = dictionary[keys[current_depth]]

    if current_depth == len(keys) - 1:
        return current_dictionary

    return get_dictionary_value_for_depth(keys, current_dictionary, current_depth + 1)


def UTFToKorean(text):
    return text.encode("UTF-8").decode("UTF-8").replace("+", " ")


def UTFToKoreanJSON(data):
    converted_data = json.dumps(data).replace("+", " ")
    return json.loads(converted_data)


def json_prettier(data):
    return json.dumps(data, indent=4, separators=(",", ":"), sort_keys=True)


def get_user_name(user_id):
    return slackInfo.get_user_info(user_id, "real_name")


spread_service = EventSpreadService()
