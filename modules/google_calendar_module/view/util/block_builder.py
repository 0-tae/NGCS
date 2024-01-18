from datetime import datetime


# Slack Block-kit 문법에 맞는 Block Component 추가용 클래스
class BlockBuilder:
    def create_block_header(self, text):
        block = {
            "type": "header",
            "text": {"type": "plain_text", "text": text, "emoji": True},
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
    def make_event_block_list(self, event_list, action_type, day_option):
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

        block_list = list()
        action = action_type_dict[action_type]

        block_header = action.get("block_header")
        block_list.append(self.create_block_header(text=block_header))

        for event in event_list:
            section_text = action.get("section_text")(event=event)
            block = self.create_single_block_section(text=f"- {section_text}")
            block_list.append(block)

        return block_list

    def create_datepicker(
        self, action_id, init_date=datetime.now().strftime("%Y-%m-%d")
    ):
        return {"type": "datepicker", "initial_date": init_date, "action_id": action_id}

    def create_timepicker(self, action_id, init_time):
        return {"type": "timepicker", "initial_time": init_time, "action_id": action_id}

    def create_actions(self, actions):
        elements = []

        for action in actions:
            elements.append(action)

        return {"type": "actions", "elements": elements}

    def create_button(self, text, action_id, value=None):
        return {
            "type": "button",
            "text": {"type": "plain_text", "text": text, "emoji": True},
            "value": action_id if not value else value,
            "action_id": action_id,
        }

    def create_url_button(self, text, url, action_id):
        return {
            "type": "button",
            "text": {"type": "plain_text", "text": text, "emoji": True},
            "url": url,
            "action_id": action_id,
        }

    def create_option(self, text, value=None):
        return {
            "text": {"type": "plain_text", "text": text, "emoji": True},
            "value": text if not value else value,
        }

    def create_static_select(self, placeholder_text, action_id, options):
        option_list = []
        for option in options:
            if type(option) == str or not option.get("text") or not option.get("value"):
                raise ValueError("option이 형식을 충족하지 않음(create_static_select)")

            option_list.append(option)

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

    def create_channel_select(self, placehloder_text, action_id):
        return (
            {
                "type": "channels_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": placehloder_text,
                    "emoji": True,
                },
                "action_id": action_id,
            },
        )

    def create_input_text(self, action_id, multiline=False):
        return {
            "type": "input",
            "optional": True,
            "element": {
                "type": "plain_text_input",
                "action_id": action_id,
                "multiline": multiline,
            },
            "label": {"type": "plain_text", "text": "일정", "emoji": True},
        }

    def create_input_datepicker(self, label, action_id):
        return {
            "type": "input",
            "element": {
                "type": "datepicker",
                "action_id": action_id,
            },
            "label": {"type": "plain_text", "text": label, "emoji": True},
        }

    def create_input_timepicker(self, label, action_id):
        return {
            "type": "input",
            "element": {
                "type": "timepicker",
                "action_id": action_id,
            },
            "label": {"type": "plain_text", "text": label, "emoji": True},
        }

    def create_input_channel_select(self, label, placeholder_text, action_id):
        return {
            "type": "input",
            "element": {
                "type": "channels_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": placeholder_text,
                    "emoji": True,
                },
                "action_id": action_id,
            },
            "label": {"type": "plain_text", "text": label, "emoji": True},
        }

    def create_input_multi_users_select(self, label, placeholder_text, action_id):
        return {
            "type": "input",
            "element": {
                "type": "multi_users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": placeholder_text,
                    "emoji": True,
                },
                "action_id": action_id,
            },
            "label": {"type": "plain_text", "text": label, "emoji": True},
        }

    def create_input_user_select(self, label, placeholder_text, action_id):
        return {
            "type": "input",
            "element": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": placeholder_text,
                    "emoji": True,
                },
                "action_id": action_id,
            },
            "label": {"type": "plain_text", "text": label, "emoji": True},
        }

    def create_checkboxes(self, action_id, options):
        option_list = []

        for option_text in options:
            option_list.append(self.create_option(text=option_text))

        return {
            "type": "checkboxes",
            "options": option_list,
            "action_id": action_id,
        }

    def create_radio_buttons(self, action_id, options):
        option_list = []

        for option_text in options:
            option_list.append(self.create_option(text=option_text))

        return {
            "type": "radio_buttons",
            "options": option_list,
            "action_id": action_id,
        }

    def create_single_block_context(self, text):
        return {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": text},
            ],
        }

    def compose(self, blocks):
        block_list = list()
        for block in blocks:
            if type(block) == list:
                block_list.extend(block)
            else:
                block_list.append(block)

        return block_list


block_builder = BlockBuilder()
