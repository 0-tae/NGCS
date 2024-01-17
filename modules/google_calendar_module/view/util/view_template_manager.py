import copy
from view.util.view_tempate import ViewTemplate

CACHE_EXPIRE = 30


class ViewTemplateManager:
    def __init__(self, __template_dict__=dict(), __cache_dict__=dict()):
        self.__template_dict__ = __template_dict__
        self.__cache_dict__ = __cache_dict__

    # ViewTemplate 객체를 복사해옴
    def get_view_template_by_name(self, template_name, cache_id=None) -> ViewTemplate:
        # 이름에 해당하는 ViewTemplate를 가져옴
        template = self.__get_template_dict__().get(template_name)

        if not template:
            raise ValueError(f"템플릿이 존재하지 않습니다. [{template_name}]")

        # 캐시 아이디가 유효하다면, ViewTemplate 객체 캐싱
        if self.__has_cache__(cache_id):
            return self.__get_cache__(cache_id).get("template")

        # 캐시된 값이 없다면, ViewTemplate 객체를 새로 생성
        template = copy.deepcopy(template)

        # 캐시된 값이 없지만, cache_id를 입력 받았을 때 캐싱
        if cache_id != None:
            self.__update_cache__(template=template, cache_id=cache_id)

        return template

    def add_view_template(self, template_name, template_options):
        template = ViewTemplate(template_name, dict())

        # template dict에 해당 option 추가
        for option_name in template_options:
            template.add_template_line(line=option_name, block=None)

        self.__update_template_dict__(template)

        return template

    # 템플릿을 적용, 템플릿을 블럭으로 변환 한다는 의미
    def apply_template(self, view, cache_id=None, template: ViewTemplate = None):
        if cache_id != None:
            self.__update_cache__(cache_id, template)

        updated_view = view
        updated_view["blocks"] = template.convert_template_to_blocks()

        return updated_view

    def __get_cache_dict__(self) -> dict:
        return self.__cache_dict__

    def __get_cache__(self, cache_id) -> ViewTemplate:
        if not cache_id:
            return None
        else:
            return self.__get_cache_dict__().get(cache_id)

    def __has_cache__(self, cache_id):
        return cache_id != None and self.__get_cache_dict__().get(cache_id) != None

    def __update_cache__(self, cache_id, template: ViewTemplate):
        self.__get_cache_dict__().update(
            {
                cache_id: {
                    "template": template,
                    "template_name": template.get_template_name(),
                },
            }
        )

    def __destroy_cache_all__(self):
        self.__get_cache_dict__().clear

    def __destroy_cache__(self, cache_id) -> ViewTemplate:
        if self.__has_cache__(cache_id):
            return self.__get_cache_dict__().pop(cache_id)

    # 템플릿을 템플릿 딕셔너리에 등록
    def __update_template_dict__(self, template: ViewTemplate):
        self.__get_template_dict__().update({template.get_template_name(): template})

    def __get_template_dict__(self) -> dict:
        return self.__template_dict__


template_manager = ViewTemplateManager()
