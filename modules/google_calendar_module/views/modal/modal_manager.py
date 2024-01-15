from views.modal.modal import ModalObject
from views.modal.event_insert_modal import CalendarEventModalObject
from views.modal.vacation_insert_modal import CalendarVacationModalObject
from views.modal.event_spread_modal import CalendarSpreadModalObject
import copy


CACHE_EXPIRE = 30

# ModalObject의 DI를 위해 ModalManger를 작성
class ModalManager:
    def __init__(self,__modal_dict__ = dict(), __cache_dict__ = dict()):
        # modal_dict : 모달 이름에 해당하는 ModalObject 인스턴스를 등록 및 조회
        self.__modal_dict__ = __modal_dict__
        self.__cache_dict__ = __cache_dict__
        
        # built_in modals, ModalManager에 이미 등록된 모달
        self.add_modal_object(CalendarEventModalObject())
        self.add_modal_object(CalendarVacationModalObject())
        self.add_modal_object(CalendarSpreadModalObject())
        
    # 캐시는 고민을 많이 해본 것 같습니다
    # modal_manager를 쓰는 사용자 입장에서 cache_id는 어떤 것으로 할 것이며
    # template_manager와 modal_manager의 사용하는 목적과 클래스가 다르니, 각각 어떤 형식으로 cache_id를 사용할 것인지...
    def get_modal_object_by_name(self, modal_name, cache_id = None):
        modal_object = self.__get_modal_dict__().get(modal_name)
        
        if not modal_object:
            raise ValueError(f"해당하는 모달이 존재하지 않음 : {modal_name}")
        print(self.__cache_dict__)
        # 캐싱되어 있는 ModalObject가 있다면 객체를 가져옴
        if self.__has_cache__(cache_id):
            modal_object = self.__get_cache__(cache_id)
            
            # 캐시된 ModalObject와 modal_name이 같을 때 modal을 가져옴
            if modal_object.get_modal_name() == modal_name:
                return modal_object
         
        # 캐싱 되어있지 않다면 ModalObject Class의 초기 객체를 복사해서 가져옴
        modal_object = copy.deepcopy(modal_object) 
        
        # 캐시 아이디가 주어졌다면, ModalObject에 대한 캐시 업데이트
        if cache_id != None:
                self.__update_cache__(cache_id, modal_object)
        
        return modal_object
        
    def get_modal_by_name(self, modal_name, cache_id = None):
        modal_object = self.__get_modal_dict__().get(modal_name)
        
        if not modal_object:
            raise ValueError(f"해당하는 모달이 존재하지 않음 : {modal_name}")
        
        # 캐싱되어 있는 ModalObject가 있다면 객체를 가져옴
        if self.__has_cache__(cache_id):
            cached_modal_object = self.__get_cache__(cache_id)
            
            # 캐시된 ModalObject와 modal_name이 같을 때 modal을 가져옴
            if cached_modal_object.get_modal_name() == modal_name:
                return cached_modal_object.get_modal()
         
        # 캐싱 되어있지 않다면 ModalObject Class의 초기 객체를 복사해서 가져옴
        modal_object = copy.deepcopy(modal_object) 
        
        # 캐시 아이디가 주어졌다면, ModalObject에 대한 캐시 업데이트
        if cache_id != None:
                self.__update_cache__(cache_id, modal_object)
        
        return modal_object.create_modal()
        
    # ModalObject의 초기 객체를 등록
    def add_modal_object(self, modal : ModalObject):
        # ex) {"event" : CalendarEventModal()}
        self.__get_modal_dict__().update({modal.get_modal_name() : modal})
        
    def __get_modal_dict__(self) -> dict:
        return self.__modal_dict__
    
    def __get_cache_dict__(self) -> dict:
        return self.__cache_dict__
    
    def __get_cache__(self, cache_id):
        if not cache_id:
            return None

        return self.__get_cache_dict__().get(cache_id)
    
    def __has_cache__(self, cache_id):
        return cache_id != None and self.__get_cache_dict__().get(cache_id) != None
    
    def __destroy_cache_all__(self):
        self.__get_cache_dict__().clear()
    
    def __destroy_cache__(self, cache_id):
        if self.__has_cache__(cache_id):
            return self.__get_cache_dict__().pop(cache_id)
    
    def __update_cache__(self, cache_id,modal_object):
        self.__get_cache_dict__().update({cache_id: modal_object})
    
modal_manager = ModalManager()