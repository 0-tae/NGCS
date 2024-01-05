from google_calendar_module.google_calendar_block_builder import block_builder


class CalendarModal:
    __current_modal__ = None

    __modals__ = {"insert_vaction": "not created", "insert_event": "not created"}

    def get_modal(self, modal_name):
        modal_creater = {
            "insert_vaction": self.create_event_insert_modal,
            "insert_event": "미구현~~",
        }

        modal = self.__modals__.get(modal_name)

        # 싱글톤으로 동작
        if modal is "not created":
            self.__modals__[modal_name] = modal_creater[modal_name]()
            modal = self.__modals__[modal_name]

        return modal

    def create_event_insert_modal(self):
        modal = self.get_default_view()
        self.modal_compose(
            view=modal,
            blocks=(
                block_builder.create_block_header("누가 어떤 휴가를 사용하나요?"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_user_select(
                            "멤버 선택", "modal_member_select"
                        ),
                        block_builder.create_static_select(
                            placeholder_text="휴가 선택",
                            action_id="modal_vacation_type_select",
                            options=("연차", "시간 연차", "반차"),
                        ),
                    )
                ),
                block_builder.create_block_header("휴가 일정을 선택 해주세요 :smlie:"),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_datepicker("modal_vacation_start_date"),
                        block_builder.create_datepicker("modal_vacation_end_date"),
                    ),
                ),
                block_builder.create_actions(
                    actions=(
                        block_builder.create_timepicker("modal_vacation_start_time"),
                        block_builder.create_timepicker("modal_vacation_end_time"),
                    )
                ),
            ),
        )

        return modal

    def modal_compose(self, view, blocks):
        block_list = []

        for block in blocks:
            block_list.append(block)

        view["blocks"] = block_list

    def set_view_properties(self, view, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_default_view(self):
        view = {}
        self.set_view_properties(view=view, key="type", value="modal")
        self.set_view_properties(view=view, key="title", value="휴가 및 일정 선택")
        self.set_view_properties(view=view, key="submit", value="제출")
        self.set_view_properties(view=view, key="close", value="취소")
        self.set_view_properties(view=view, key="callback_id", value="modal_submit")
        self.set_view_properties(view=view, key="private_metadata", value="None")

        return view

    def add_block():
        return

    def add_component():
        return


modal_builder = CalendarModal()
