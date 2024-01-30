from view.util.block_builder import block_builder
from view.util.view_template_manager import template_manager
from view.modals.modal import ModalObject

ACTION_GROUP = "event_insert"


class CalendarEventModalObject(ModalObject):
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(
        self,
        __modal_name__=ACTION_GROUP,
        __modal__=None,
        __modal_title__="이벤트 및 일정 선택",
        __callback_id__=f"{ACTION_GROUP}-modal_submit_event",
    ):
        super().__init__(__modal_name__, __modal__, __modal_title__, __callback_id__)

        template_manager.add_view_template(
            template_name=ACTION_GROUP,
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

    # 일정 등록 모달창을 생성함
    def create_modal(self):
        template = template_manager.get_view_template_by_name(ACTION_GROUP)

        # template 설정
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("등록할 일정"),
                block_builder.create_input_text(
                    action_id=self.action_id("modal_event_summary")
                ),
                block_builder.create_block_header("날짜 선택"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_datepicker(
                            action_id=self.action_id("modal_event_date")
                        ),
                        block_builder.create_checkboxes(
                            action_id=self.action_id("modal_event_allday"),
                            options=("하루종일",),
                        ),
                    )
                ),
                block_builder.create_block_header("시간 선택"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_timepicker(
                            action_id=self.action_id("modal_event_start_time"),
                            init_time="09:00",
                        ),
                        block_builder.create_timepicker(
                            action_id=self.action_id("modal_event_end_time"),
                            init_time="18:00",
                        ),
                    )
                ),
                block_builder.create_block_header("상세 내용"),
                block_builder.create_input_text(
                    action_id=self.action_id("modal_event_description"), multiline=True
                ),
            ),
        )

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal = template_manager.apply_template(
            view=self.get_modal(),
            template=template,
            cache_id=self.get_modal()["private_metadata"],
        )

        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)

        return modal

    def update_modal(self, original_view, all_day):
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.get_view_template_by_name(
            template_name=ACTION_GROUP, cache_id=original_view["private_metadata"]
        )

        # response view를 템플릿에 적용
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
                        action_id=self.action_id("modal_event_start_time"),
                        init_time="09:00",
                    ),
                    block_builder.create_timepicker(
                        action_id=self.action_id("modal_event_end_time"),
                        init_time="18:00",
                    ),
                )
            ),
        )

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal = template_manager.apply_template(
            view=self.get_modal(),
            template=updated_template,
            cache_id=self.get_modal()["private_metadata"],
        )

        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)

        return modal

    # 이 밑은 Custom Blocks
    def create_time_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_timepicker(
                    self.action_id("modal_vacation_start_time"), "09:00"
                ),
                block_builder.create_timepicker(
                    self.action_id("modal_vacation_end_time"), "18:00"
                ),
            )
        )

    def create_date_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    self.action_id("modal_vacation_start_date")
                ),
                block_builder.create_datepicker(
                    self.action_id("modal_vacation_end_date")
                ),
            ),
        )

    def create_single_date_block(self):
        return block_builder.create_actions(
            actions=(
                block_builder.create_datepicker(
                    self.action_id("modal_vacation_start_date")
                ),
            ),
        )

    def action_id(self, action_type):
        return f"{ACTION_GROUP}-{action_type}"

original = CalendarEventModalObject()