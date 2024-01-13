from modules.google_calendar_module.views.view_template_manager import template_manager
from modules.google_calendar_module.views.modal_manager import modal_manager
from modules.google_calendar_module.views.block_builder import block_builder

# 이름이 ModalObject인 이유는.. 실제 사용될 Modal은 Json String 이라서
# Abstract class for ModalObject classes
class ModalObject():
    def __init__(self, __modal_name__ = "default"):
        self.__modal_name__ = __modal_name__
        
        template_manager.create_view_template(
            "default",
            template_options=(
                "line_1_header",
                "line_2_section",
            ),
        )
        
    def create_modal(self, creator_id):
        # 구현하지 않았다면 default modal을 생성하기 위한 용도이므로, "default"를 명시
        template = template_manager.get_template_by_name("default")
        template.set_template_all(
            blocks=(
                block_builder.create_block_header("This is Default Modal"),
                block_builder.create_single_block_section("You didn't implemented [create_modal] function in your ModalObject class, Implement and create your Custom-Modal"),
                )
            )
                
        return template_manager.apply_template(
            view=self.get_base_view(
                callback_id="update_calendar-modal_submit_default",
                creator_id=creator_id,
            ),
            template=template,
        )
    
        
    def get_base_view(self, callback_id, creator_id = None):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = callback_id
        view["private_metadata"] = creator_id
        self.set_view_component_properties(view=view, key="title", value="Default Modal")
        self.set_view_component_properties(view=view, key="submit", value="OK")
        self.set_view_component_properties(view=view, key="close", value="OK")
        
        return view
        
    def set_modal_name(self, new_modal_name):
        self.__modal_name__ = new_modal_name

    def get_modal_name(self):
        return self.__modal_name__

    def set_view_component_properties(self, view: dict, key, value):
        view[key] = {"type": "plain_text", "text": value}
    
    def after_submit(self, creator_id):
        template_manager.destroy_template_cache(creator_id)