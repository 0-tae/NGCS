from views.block_builder import block_builder
from views.view_template_manager import template_manager
from views.modal import ModalObject
from datetime import datetime

class CalendarSpreadModalObject(ModalObject):
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(self,
                 __modal_name__ = "spread", 
                 __modal__ = None,
                 __modal_title__ = "일정 전파하기",
                 __callback_id__ = "spread_calendar-modal_submit_spread"):
      
        super().__init__(__modal_name__, __modal__, __modal_title__, __callback_id__)
        template_manager.add_view_template(
            "spread",
            template_options=(
                "line_1_header",  # 어떤 이벤트를 전파하는지?
                "line_2_actions",  # date_picker, static_select(event)
                "line_3_header",  # 누구에게 전파하는지?
                "line_4_actions",  # radio buttons(멤버, 채널)
                "line_5_actions_changable",  # static_select(event) or member_select
            ),
        )

    def create_modal(self):
        template = template_manager.get_view_template_by_name("spread")
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

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal =  template_manager.apply_template(
            view=self.get_modal(),
            template=template,
            cache_id=self.get_modal()["private_metadata"]
        )
        
        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)
        
        return modal

    def update_spread_event_modal(self, original_view, date, event_list: list):
        updated_template = template_manager.get_view_template_by_name(
            template_name="spread",
            cache_id=original_view["private_metadata"]
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

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal =  template_manager.apply_template(
            view=self.get_modal(),
            template=updated_template,
            cache_id=self.get_modal()["private_metadata"]
        )
        
        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)
        
        return modal

    def update_spread_member_type_modal(self, original_view, selected_type):
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.get_view_template_by_name(
            template_name="spread",
            cache_id=original_view["private_metadata"]
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

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal = template_manager.apply_template(
            view=self.get_modal(),
            template=updated_template,
            cache_id=self.get_modal()["private_metadata"]
        )
        
        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)
        
        return modal
