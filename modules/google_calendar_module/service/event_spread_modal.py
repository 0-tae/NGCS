from google_calendar_module.google_calendar_block_builder import block_builder
from datetime import datetime
from google_calendar_module.google_calendar_view_template import (
    template_manager,
    ViewTemplateObjectManager,
    ViewTemplateObject,
)


class CalendarSpreadModal:
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(self):
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
                            options="default",
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
                callback_id="spread_calendar-modal_submit_spread",
                creator_id=creator_id,
            ),
            template=template,
        )

    def update_spread_event_modal(self, original_view, date, event_list: list):
        updated_template = template_manager.load_template_by_creator_id_with_name(
            creator_id=original_view["private_metadata"], template_name="spread"
        )

        updated_template.set_template_line(
            line="line_2_actions",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_datepicker(
                        action_id="spread_calendar-modal_spread_date_select",
                        init_date=date,
                    ),
                    block_builder.create_static_select(
                        options=(
                            tuple(event_list) if len(event_list) > 0 else ("오늘 일정 없음",)
                        ),
                        placeholder_text="일정 선택",
                        action_id="spread_calendar-modal_spread_event_select",
                    ),
                )
            ),
        )

        return template_manager.apply_template(
            view=self.get_base_view(
                callback_id="spread_calendar-modal_submit_spread",
                creator_id=original_view["private_metadata"],
            ),
            template=updated_template,
        )

    def update_spread_member_type_modal(self, original_view, selected_type):
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
                callback_id="spread_calendar-modal_submit_spread",
                creator_id=original_view["private_metadata"],
            ),
            template=updated_template,
        )

    def set_view_component_properties(self, view, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_base_view(self, callback_id, creator_id):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = callback_id
        view["private_metadata"] = creator_id  # private_metadata를 통해 유저 아이디 확인
        self.set_view_component_properties(view=view, key="title", value="일정 전파하기")
        self.set_view_component_properties(view=view, key="submit", value="전파")
        self.set_view_component_properties(view=view, key="close", value="취소")

        return view
