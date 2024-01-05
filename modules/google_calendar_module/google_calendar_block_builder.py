from datetime import datetime

# TODO: 블럭 빌드 작업을 따로 분리해야 함
#       코드를 줄일 수 있을 것 같은데..


class CalendarBlockBuilder:
    def create_block_header(self, text):
        block = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": text,
            },
        }

        return block

    def create_block_section_with_field(self, fields):
        field_list = []

        for text in fields:
            field_list.append({"type": "mrkdwn", "text": text})

        return {"type": "section", "fields": field_list}

    def create_single_block_section(self, text):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text,
            },
        }

    def create_block_section_vacation(self, event):
        # ex. event["summary"] = "최용태-오전 반차"
        name = event["summary"].split("-")[0]
        vacation_type = event["summary"].split("-")[-1]

        event_summary = "연차"

        # 연차일 경우 시간 설명 생략
        # 그 이외는 시간 설명
        if not event["all-day"]:
            time_range = (
                datetime.fromisoformat(event["start"]).strftime("%H:%M")
                + "~"
                + datetime.fromisoformat(event["end"]).strftime("%H:%M")
            )

            event_summary = f"{vacation_type} ({time_range})"

        # ex) 최용태 님 오늘 09:00~12:00 오전 반차
        # ex) 최용태 님 오늘 연차
        return f"*{name}* 님 {event_summary}"

    def create_block_section_common_event(self, event):
        event_summary = event["summary"]

        # 하루 종일 일 경우, 시간 설명 생략
        # 그 이외는 시간 설명
        if not event["all-day"]:
            time_range = (
                datetime.fromisoformat(event["start"]).strftime("%H:%M")
                + "~"
                + datetime.fromisoformat(event["end"]).strftime("%H:%M")
            )

            event_summary += f" ({time_range})"

        return f"{event_summary}"

    def create_block_divider(self):
        block = {"type": "divider"}
        return block

    # TODO: day_option(오늘, 특정 일자) 구현
    def make_block_list(self, event_list, action_type, day_option):
        action_type_dict = {
            "today_vacation": {
                "section_text": self.create_block_section_vacation,
                "block_header": "오늘 휴가자 목록:smile:",
            },
            "today_event": {
                "section_text": self.create_block_section_common_event,
                "block_header": "오늘 일정 목록:saluting_face:",
            },
        }

        block_list = []
        action = action_type_dict[action_type]

        block_header = action.get("block_header")
        block_list.append(self.create_block_header(text=block_header))

        for event in event_list:
            section_text = action.get("section_text")(event=event)
            block = self.create_single_block_section(text=section_text)
            block_list.append(block)

        return block_list

    def create_datepicker(self, action_id):
        return {"type": "datepicker", "action_id": action_id}

    def create_timepicker(self, action_id):
        return {"type": "timepicker", "action_id": action_id}

    def create_actions(self, actions):
        elements = []

        for action in actions:
            elements.append(action)

        return {"type": "actions", "elements": elements}

    def create_button(self, text, action_id):
        return {
            "type": "button",
            "text": {"type": "plain_text", "text": text, "emoji": True},
            "value": action_id,
            "action_id": action_id,
        }

    def create_option(self, text):
        return {
            "text": {"type": "plain_text", "text": text, "emoji": True},
            "value": text,
        }

    def create_static_select(self, placeholder_text, action_id, options):
        option_list = []

        for option_text in options:
            option_list.append(self.create_option(text=option_text))

        return {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": placeholder_text,
                "emoji": True,
            },
            "options": option_list,
            "action_id": action_id,
        }

    def create_user_select(self, placeholder_text, action_id):
        return {
            "type": "users_select",
            "placeholder": {
                "type": "plain_text",
                "text": placeholder_text,
                "emoji": True,
            },
            "action_id": action_id,
        }


block_builder = CalendarBlockBuilder()
