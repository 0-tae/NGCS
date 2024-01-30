from view.util.block_builder import block_builder
from view.util.view_template_manager import template_manager
from view.modals.modal import ModalObject

ACTION_GROUP = "vacation_insert"


class CalendarVacationModalObject(ModalObject):
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(
        self,
        __modal_name__=ACTION_GROUP,
        __modal__=None,
        __modal_title__="휴가 등록하기",
        __callback_id__=f"{ACTION_GROUP}-modal_submit_vacation",
    ):
        super().__init__(__modal_name__, __modal__, __modal_title__, __callback_id__)
        template_manager.add_view_template(
            ACTION_GROUP,
            template_options=(
                "line_1_header",
                "line_2_actions",
                "line_3_header",
                "line_4_actions",
                "line_5_actions",
            ),
        )

    # 휴가 등록 모달창을 생성함
    def create_modal(self):
        # view template을 설정
        template = template_manager.get_view_template_by_name(ACTION_GROUP)

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
                        self.action_id("modal_vacation_member_select"),
                    ),
                    block_builder.create_static_select(
                        placeholder_text="휴가 선택",
                        action_id=self.action_id("modal_vacation_type_select"),
                        options=(
                            block_builder.create_option("연차"),
                            block_builder.create_option("시간 연차"),
                            block_builder.create_option("반차"),
                        ),
                    ),
                )
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

    def update_modal(self, original_view, vacation_type):
        date_block = self.create_date_block()
        single_date_block = self.create_single_date_block()
        time_block = self.create_time_block()

        vacation_dict = {
            "연차": [date_block, None],
            "시간 연차": [single_date_block, time_block],
            "반차": [single_date_block, time_block],
        }

        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.get_view_template_by_name(
            template_name=ACTION_GROUP, cache_id=original_view["private_metadata"]
        )

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=original_view)

        # view의 line을 수정
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

    # Custom Block
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


original = CalendarVacationModalObject()
