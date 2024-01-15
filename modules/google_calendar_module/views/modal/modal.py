from views.util.view_template_manager import template_manager
from views.util.block_builder import block_builder

# 이름이 ModalObject인 이유는.. 실제 사용될 Modal은 Json String 이기 때문
# Abstract class for ModalObject classes
class ModalObject():
    def __init__(self, 
                 __modal_name__ = "default", 
                 __modal__ = None,
                 __modal_title__ = "Default Modal Title",
                 __callback_id__ = "default-modal_submit_default"):
        
        self.__modal_name__ = __modal_name__
        self.__modal__ = __modal__
        self.__modal_title__ = __modal_title__
        self.__callback_id__ = __callback_id__
        
        template_manager.add_view_template(
            template_name="default",
            template_options=(
                "line_1_default",
                "line_2_default",
            ),
        )
        
    def create_modal(self, creator_id):
        # 구현하지 않았다면 default modal을 생성하기 위한 용도이므로, "default"를 명시
        template = template_manager.get_view_template_by_name("default")
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
    
        
    def get_base_view(self):
        view = {}
        view["blocks"] = []
        view["type"] = "modal"
        view["callback_id"] = self.get_callback_id()
        view["private_metadata"] = self.get_id()
        self.set_view_component_properties(view=view, key="title", value=self.get_modal_title())
        self.set_view_component_properties(view=view, key="submit", value="제출")
        self.set_view_component_properties(view=view, key="close", value="취소")
        
        return view
    
    def set_modal(self, new_modal):
        self.__modal__= new_modal
        
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