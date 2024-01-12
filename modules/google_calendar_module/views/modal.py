class Modal:
    def __init__(self, __modal_name__):
        self.__modal_name__ = __modal_name__

    def set_modal_name(self, new_modal_name):
        self.__modal_name__ = new_modal_name

    def get_modal_name(self):
        return self.__modal_name__

    def set_view_component_properties(self, view: dict, key, value):
        view[key] = {"type": "plain_text", "text": value}
