from google_calendar_module.google_calendar_block_builder import block_builder
from datetime import datetime
from google_calendar_module.google_calendar_view_template import (
    template_manager,
    ViewTemplateObjectManager,
    ViewTemplateObject,
)


class CalendarVacationModal:
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(self):
        template_manager.create_view_template(
            "vacation",
            template_options=(
                "line_1_header",
                "line_2_actions",
                "line_3_header",
                "line_4_actions",
                "line_5_actions",
            ),
        )
        template_manager.create_view_template(
            "event",
            template_options=(
                "line_1_header",
                "line_2_actions",
                "line_3_header",
                "line_4_actions",
                "line_5_header_hidable",
                "line_6_actions_hidable",
                "line_7_header",
                "line_8_actions",
            ),
        )
        template_manager.create_view_template(
            "spread",
            template_options=(
                "line_1_header",  # 어떤 이벤트를 전파하는지?
                "line_2_actions",  # date_picker, static_select(event)
                "line_3_header",  # 누구에게 전파하는지?
                "line_4_actions",  # radio buttons(멤버, 채널)
                "line_5_actions_changable",  # static_select(event) or member_select
            ),
        )

    def after_submit(self, creator_id):
        template_manager.destroy_template_cache(creator_id)

    # 이름에 해당하는 모달창을 얻어옴
    def get_modal(self, modal_name, creator_id="default"):
        modal_creater = {
            "vacation": self.create_vacation_insert_modal,
            "event": self.create_event_insert_modal,
            "spread": self.create_spread_modal,
        }

        return modal_creater[modal_name](creator_id)

    def create_spread_modal(self, creator_id):
        template = template_manager.get_template_by_name("spread")
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("어떤 일정을 전파 할까요?"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_datepicker(
                            action_id="spread_calendar-modal_spread_date_select",
                            init_date=datetime.now().strftime("%Y-%m-%d"),
                        ),
                        block_builder.create_static_select(
                            options=(
                                "------------여러가지 이벤트들(default: 오늘 이벤트 목록)-----------"
                            ),
                            placeholder_text="일정 선택",
                            action_id="spread_calendar-modal_spread_event_select",
                        ),
                    )
                ),
                block_builder.create_block_header("누구에게 전파 할까요?"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_radio_buttons(
                            options=("멤버", "채널"),
                            action_id="spread_calendar-modal_spread_type_select",
                        ),
                    )
                ),
                block_builder.create_input_multi_users_select(
                    label="멤버에게 전파",  # line_5_actions_changable default
                    placeholder_text="멤버 선택",
                    action_id="spread_calendar-modal_spread_users_select",
                ),
            )
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                title="일정 전파하기", event_type="spread", creator_id=creator_id
            ),
            template=template,
        )

    def update_spread_modal(self, original_view, selected_type):
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.load_template_by_creator_id_with_name(
            creator_id=original_view["private_metadata"], template_name="spread"
        )

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=original_view)

        # type이 멤버일 경우 해당 블록을 적용
        member_input = block_builder.create_input_multi_users_select(
            label="멤버에게 전파",  # line_5_actions_changable default
            placeholder_text="멤버 선택",
            action_id="spread_calendar-modal_spread_users_select",
        )

        # type이 채널일 경우 해당 블록을 적용
        channel_input = block_builder.create_input_channel_select(
            label="채널에 전파",  # line_5_actions_changable default
            placeholder_text="채널 선택",
            action_id="spread_calendar-modal_spread_channels_select",
        )

        # 템플릿 라인 업데이트
        updated_template.set_template_line(
            line="line_5_actions_changable",
            block=member_input if selected_type == "멤버" else channel_input,
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                title="이벤트 및 일정 선택",
                event_type="spread",
                creator_id=original_view["private_metadata"],
            ),
            template=updated_template,
        )

    # 일정 등록 모달창을 생성함
    def create_event_insert_modal(self, creator_id):
        template = template_manager.get_template_by_name("event")
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("등록할 일정"),
                block_builder.create_input_text(
                    action_id="update_calendar-modal_event_summary"
                ),
                block_builder.create_block_header("날짜 선택"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_datepicker(
                            action_id="update_calendar-modal_event_date"
                        ),
                        block_builder.create_checkboxes(
                            action_id="update_calendar-modal_event_allday",
                            options=("하루종일",),
                        ),
                    )
                ),
                block_builder.create_block_header("시간 선택"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_timepicker(
                            action_id="update_calendar-modal_event_start_time",
                            init_time="09:00",
                        ),
                        block_builder.create_timepicker(
                            action_id="update_calendar-modal_event_end_time",
                            init_time="18:00",
                        ),
                    )
                ),
                block_builder.create_block_header("상세 내용"),
                block_builder.create_input_text(
                    action_id="update_calendar-modal_event_description", multiline=True
                ),
            ),
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                title="이벤트 및 일정 선택", event_type="event", creator_id=creator_id
            ),
            template=template,
        )

    def update_event_insert_modal(self, original_view, all_day):
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.load_template_by_creator_id_with_name(
            creator_id=original_view["private_metadata"], template_name="event"
        )

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=original_view)

        updated_template.set_template_line(
            line="line_5_header_hidable",
            block=None if all_day else block_builder.create_block_header("시간 선택"),
        )
        updated_template.set_template_line(
            line="line_6_actions_hidable",
            block=None
            if all_day
            else block_builder.create_actions(
                actions=(
                    block_builder.create_timepicker(
                        action_id="update_calendar-modal_event_start_time",
                        init_time="09:00",
                    ),
                    block_builder.create_timepicker(
                        action_id="update_calendar-modal_event_end_time",
                        init_time="18:00",
                    ),
                )
            ),
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                title="이벤트 및 일정 선택",
                event_type="event",
                creator_id=original_view["private_metadata"],
            ),
            template=updated_template,
        )

    # 휴가 등록 모달창을 생성함
    def create_vacation_insert_modal(self, creator_id):
        # view template을 설정
        template = template_manager.get_template_by_name("vacation")

        template.set_template_line(
            line="line_1_header",
            block=block_builder.create_block_header("누가 어떤 휴가를 사용하나요?"),
        )
        template.set_template_line(
            line="line_2_actions",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_user_select(
                        "멤버 선택(미선택 시, 본인)",
                        "update_calendar-modal_vacation_member_select",
                    ),
                    block_builder.create_static_select(
                        placeholder_text="휴가 선택",
                        action_id="update_calendar-modal_vacation_type_select",
                        options=("연차", "시간 연차", "반차"),
                    ),
                )
            ),
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                title="휴가 및 일정 선택", event_type="vacation", creator_id=creator_id
            ),
            template=template,
        )

    def update_vacation_insert_modal(self, original_view, vacation_type):
        date_block = block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_start_date"
                ),
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_end_date"
                ),
            ),
        )
        single_date_block = block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_start_date"
                ),
            ),
        )

        time_block = block_builder.create_actions(
            actions=(
                block_builder.create_timepicker(
                    "update_calendar-modal_vacation_start_time", "09:00"
                ),
                block_builder.create_timepicker(
                    "update_calendar-modal_vacation_end_time", "18:00"
                ),
            )
        )

        vacation_dict = {
            "연차": [date_block, None],
            "시간 연차": [single_date_block, time_block],
            "반차": [single_date_block, time_block],
        }

        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.load_template_by_creator_id_with_name(
            creator_id=original_view["private_metadata"], template_name="vacation"
        )

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=original_view)
        updated_template.set_template_line(
            line="line_3_header",
            block=block_builder.create_block_header("휴가 일정을 선택 해주세요 :smile:"),
        )
        updated_template.set_template_line(
            line="line_4_actions", block=vacation_dict.get(vacation_type)[0]
        )
        updated_template.set_template_line(
            line="line_5_actions", block=vacation_dict.get(vacation_type)[1]
        )

        return template_manager.apply_template(
            self.get_base_view(
                title="휴가 및 일정 선택",
                creator_id=original_view["private_metadata"],
                event_type="vacation",
            ),
            template=updated_template,
        )

    def set_view_component_properties(self, view, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_base_view(self, title, event_type, creator_id):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = f"update_calendar-modal_{event_type}_submit"
        view["private_metadata"] = creator_id  # private_metadata를 통해 유저 아이디 확인
        self.set_view_component_properties(view=view, key="title", value=title)
        self.set_view_component_properties(view=view, key="submit", value="제출")
        self.set_view_component_properties(view=view, key="close", value="취소")

        return view


modal_builder = CalendarVacationModal()
