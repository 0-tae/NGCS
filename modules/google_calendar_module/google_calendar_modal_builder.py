from google_calendar_module.google_calendar_block_builder import block_builder
from google_calendar_module.google_calendar_view_template import (
    template_manager,
    ViewTemplateObjectManager,
    ViewTemplateObject,
)


class CalendarVacationModal:
    __modals__ = {"vacation": "not created", "event": "not created"}
    __view_template_dict__ = dict()

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
                "field1_actions",
                "field2_header",
                "field2_actions",
            ),
        )

    def get_modal(self, modal_name):
        modal_creater = {
            "vacation": self.create_vacation_insert_modal,
            "event": "미구현~~",
        }

        self.__modals__[modal_name] = modal_creater[modal_name]()
        modal = self.__modals__[modal_name]

        return modal

    def __update_modal__(self, original_view, addr_blocks):
        modal = original_view
        self.modal_compose(view=original_view, blocks=addr_blocks)

        return modal

    def create_vacation_insert_modal(self):
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
                        "멤버 선택", "update_calendar-modal_member_select"
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
            view=self.get_base_view(), template=template
        )

    def update_vacation_insert_modal(self, orginal_view, vacation_type):
        date_block = block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    "update_modal-modal_vacation_start_date"
                ),
                block_builder.create_datepicker("update_modal-modal_vacation_end_date"),
            ),
        )

        time_block = block_builder.create_actions(
            actions=(
                block_builder.create_timepicker(
                    "update_modal-modal_vacation_start_time", "09:00"
                ),
                block_builder.create_timepicker(
                    "update_modal-modal_vacation_end_time", "18:00"
                ),
            )
        )

        vacation_dict = {
            "연차": [date_block, None],
            "시간 연차": [date_block, time_block],
            "반차": [date_block, time_block],
        }
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.get_template_by_name("vacation")

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=orginal_view)
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
            self.get_base_view(), template=updated_template
        )

    def set_view_component_properties(self, view, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_base_view(self):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = "modal_submit"
        view["private_metadata"] = "None"
        self.set_view_component_properties(view=view, key="title", value="휴가 및 일정 선택")
        self.set_view_component_properties(view=view, key="submit", value="제출")
        self.set_view_component_properties(view=view, key="close", value="취소")

        return view


modal_builder = CalendarVacationModal()
