from view.util.block_builder import block_builder
from view.util.view_template_manager import template_manager
from view.modals.modal import ModalObject
from datetime import datetime

ACTION_GROUP = "event_spread"


class CalendarSpreadModalObject(ModalObject):
    def __init__(
        self,
        __modal_name__=ACTION_GROUP,
        __modal__=None,
        __modal_title__="일정 전파하기",
        __callback_id__=f"{ACTION_GROUP}-modal_submit_spread",
    ):
        super().__init__(__modal_name__, __modal__, __modal_title__, __callback_id__)
        template_manager.add_view_template(
            ACTION_GROUP,
            template_options=(
                "line_1_header",  # 어떤 이벤트를 전파하는지?
                "line_2_actions",  # date_picker, static_select(event)
                "line_3_header",  # 누구에게 전파하는지?
                "line_4_actions",  # radio buttons(멤버, 채널)
                "line_5_actions_changable",  # static_select(event) or member_select
            ),
        )
        self.register_to_modal_manager(self)

    def create_modal(self):
        template = template_manager.get_view_template_by_name(ACTION_GROUP)
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("어떤 일정을 전파 할까요?"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_datepicker(
                            action_id=self.action_id("modal_spread_date_select"),
                            init_date=datetime.now().strftime("%Y-%m-%d"),
                        ),
                        block_builder.create_static_select(
                            options=(block_builder.create_option("default"),),
                            placeholder_text="일정 선택",
                            action_id=self.action_id("modal_spread_event_select"),
                        ),
                    )
                ),
                block_builder.create_block_header("누구에게 전파 할까요?"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_radio_buttons(
                            options=("멤버", "채널"),
                            action_id=self.action_id("modal_spread_type_select"),
                        ),
                    )
                ),
                block_builder.create_input_multi_users_select(
                    label="멤버에게 전파",  # line_5_actions_changable default
                    placeholder_text="멤버 선택",
                    action_id=self.action_id("modal_spread_users_select"),
                ),
            )
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

    def update_spread_event_modal(self, original_view, date, event_options: tuple):
        updated_template = template_manager.get_view_template_by_name(
            template_name=ACTION_GROUP, cache_id=original_view["private_metadata"]
        )

        updated_template.set_template_line(
            line="line_2_actions",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_datepicker(
                        action_id=self.action_id("modal_spread_date_select"),
                        init_date=date,
                    ),
                    block_builder.create_static_select(
                        options=(
                            event_options
                            if len(event_options) > 0
                            else (
                                block_builder.create_option(
                                    text="일정 없음", value="non-event"
                                ),
                            )
                        ),
                        placeholder_text="일정 선택",
                        action_id=self.action_id("modal_spread_event_select"),
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

    def update_spread_member_type_modal(self, original_view, selected_type):
        # 업데이트할 템플릿을 가져옴
        updated_template = template_manager.get_view_template_by_name(
            template_name=ACTION_GROUP, cache_id=original_view["private_metadata"]
        )

        # 가져온 view를 템플릿에 적용
        updated_template.convert_view_to_template(view=original_view)

        # type이 멤버일 경우 해당 블록을 적용
        member_input = block_builder.create_input_multi_users_select(
            label="멤버에게 전파",  # line_5_actions_changable default
            placeholder_text="멤버 선택",
            action_id=self.action_id("modal_spread_users_select"),
        )

        # type이 채널일 경우 해당 블록을 적용
        channel_input = block_builder.create_input_channel_select(
            label="채널에 전파",  # line_5_actions_changable default
            placeholder_text="채널 선택",
            action_id=self.action_id("modal_spread_channels_select"),
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
            cache_id=self.get_modal()["private_metadata"],
        )

        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)

        return modal

    def action_id(self, action_type):
        return f"{ACTION_GROUP}-{action_type}"


original = CalendarSpreadModalObject()
