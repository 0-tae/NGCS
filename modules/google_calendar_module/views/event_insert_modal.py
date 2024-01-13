from google_calendar_module.google_calendar_block_builder import block_builder
from modules.google_calendar_module.views.modal_manager import modal_manager
from google_calendar_module.views.modal import Modal
from datetime import datetime
from modules.google_calendar_module.views.view_template_manager import template_manager

class CalendarEventModalObject(Modal):
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(self, __modal_name__ = "event"):
        self.__modal_name__ = __modal_name__
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
        
        modal_manager.add_modal(modal_name=__modal_name__, create_strategy=self.create_modal_strategy)

    # 일정 등록 모달창을 생성함
    # creator_id를 view의 private_metadata로 설정해서 템플릿 캐싱 작업에 쓰임
    def create_modal(self, creator_id):
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
                callback_id="update_calendar-modal_submit_event",
                creator_id=creator_id,
            ),
            template=template,
        )

    def update_modal(self, original_view, all_day):
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
                callback_id="update_calendar-modal_submit_event",
                creator_id=original_view["private_metadata"],
            ),
            template=updated_template,
        )

    def get_base_view(self, callback_id, creator_id):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = callback_id
        view["private_metadata"] = creator_id  # private_metadata를 통해 유저 아이디 확인
        self.set_view_component_properties(view=view, key="title", value="이벤트 및 일정 선택")
        self.set_view_component_properties(view=view, key="submit", value="제출")
        self.set_view_component_properties(view=view, key="close", value="취소")

        return view


    # 이 밑은 Custom Blocks
    def create_time_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_timepicker(
                    "update_calendar-modal_vacation_start_time", "09:00"
                ),
                block_builder.create_timepicker(
                    "update_calendar-modal_vacation_end_time", "18:00"
                ),
            )
        )

    def create_date_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_start_date"
                ),
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_end_date"
                ),
            ),
        )

    def create_single_date_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    "update_calendar-modal_vacation_start_date"
                ),
            ),
        )
