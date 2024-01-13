from google_calendar_module.views.modal import ModalObject
from google_calendar_module.views.event_insert_modal import CalendarEventModalObject
from google_calendar_module.views.vacation_insert_modal import CalendarVacationModalObject
from google_calendar_module.views.event_spread_modal import CalendarSpreadModalObject


# ModalObject의 DI를 위해 ModalManger를 작성
class ModalManager:
    def __init__(self,__modal_dict__ = dict()):
        # modal_dict : 모달 이름에 해당하는 ModalObject 인스턴스를 등록 및 조회
        self.__modal_dict__ = __modal_dict__
        
        # built_in modals, ModalManager에 이미 등록된 모달
        self.add_modal_object(CalendarEventModalObject())
        self.add_modal_object(CalendarVacationModalObject())
        self.add_modal_object(CalendarSpreadModalObject())
        
    def get_modal_dict(self) -> dict:
        return self.__modal_dict__
    
    # creator_id는 템플릿 
    def create_modal_with_name(self, modal_name, crea):
        modal_object = self.get_modal_dict().get(modal_name)
        
        if not modal_object:
            raise ValueError(f"해당하는 모달이 존재하지 않음 : {modal_name}")
        
        return modal_object.create_modal()
    
    def add_modal_object(self, modal : ModalObject):
        # ex) {"event" : CalendarEventModal()}
        self.get_modal_dict().update({modal.get_modal_name() : modal})
    
modal_manager = ModalManager()