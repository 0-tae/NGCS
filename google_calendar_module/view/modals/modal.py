from view.util.view_template_manager import template_manager
from view.util.block_builder import block_builder

ACTION_GROUP = "default"


# Standard of ModalObject
# Abstract class for ModalObject classes
class ModalObject:
    def __init__(
        self,
        __modal_name__=ACTION_GROUP,
        __modal__=None,
        __modal_title__="Default Modal Title",
        __callback_id__=f"{ACTION_GROUP}-modal_submit_default",
    ):
        self.__modal_name__ = __modal_name__
        self.__modal__ = __modal__
        self.__modal_title__ = __modal_title__
        self.__callback_id__ = __callback_id__

        template_manager.add_view_template(
            template_name=ACTION_GROUP,
            template_options=(
                "line_1_default",
                "line_2_default",
            ),
        )

    # 아직 실제로 사용되지 않음
    def create_modal(self):
        template = template_manager.get_view_template_by_name(ACTION_GROUP)
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("This is Default Modal"),
                block_builder.create_single_block_section(
                    "You didn't implemented [create_modal] function in your ModalObject class, Implement and create your Custom-Modal"
                ),
            )
        )

        return template_manager.apply_template(
            view=self.get_base_view(callback_id=self.action_id("modal_submit_default")),
            template=template,
        )

    def get_base_view(self):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = self.get_callback_id()
        view["private_metadata"] = self.get_id()
        self.set_view_component_properties(
            view=view, key="title", value=self.get_modal_title()
        )
        self.set_view_component_properties(view=view, key="submit", value="제출")
        self.set_view_component_properties(view=view, key="close", value="취소")

        return view

    def set_modal(self, new_modal):
        self.__modal__ = new_modal

    def get_modal(self):
        if not self.__modal__:
            return self.get_base_view()
        else:
            return self.__modal__

    def set_modal_name(self, new_modal_name):
        self.__modal_name__ = new_modal_name

    def get_modal_name(self):
        return self.__modal_name__

    def set_callback_id(self, new_callback_id):
        self.__callback_id__ = new_callback_id

    def get_callback_id(self):
        return self.__callback_id__

    def set_modal_title(self, new_modal_title):
        self.__modal_title__ = new_modal_title

    def get_modal_title(self):
        return self.__modal_title__

    def set_view_component_properties(self, view: dict, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_id(self):
        return str(id(self))[-5:]

    def action_id(action_type):
        return f"{ACTION_GROUP}-{action_type}"


original_object = ModalObject()
