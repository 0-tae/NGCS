import copy
from google_calendar_module.views.view_tempate import ViewTemplate

class ViewTemplateManager:
    __template_dict__ = dict()
    __template_cache__ = dict()

    # 유저 아이디를 통해 현재 템플릿을 템플릿 캐시에 저장
    def update_template_cache(self, creator_id, template: ViewTemplate):
        self.__template_cache__.update(
            {
                creator_id: {
                    "template": template,
                    "template_name": template.get_template_name(),
                },
            }
        )

    # 유저 아이디를 통해 저장된 템플릿을 가져옴
    def get_template_cache(self, creator_id) -> ViewTemplate:
        return self.__template_cache__.get(creator_id)

    # 유저 아이디를 통해 템플릿 캐시를 삭제(submit 시)
    def destroy_template_cache(self, creator_id) -> ViewTemplate:
        if self.get_template_cache(creator_id=creator_id) != None:
            self.__template_cache__.pop(creator_id)

    # 템플릿을 템플릿 딕셔너리에 등록
    def set_template_dict(self, template: ViewTemplate):
        self.__template_dict__[template.get_template_name()] = template

    def load_template_by_creator_id_with_name(
        self, creator_id, template_name
    ) -> ViewTemplate:
        cached_template = self.get_template_cache(creator_id=creator_id)

        # 캐시된 템플릿이 없거나 템플릿 네임과 불일치한 캐시를 가지고 있다면, 새로 생성
        if (
            cached_template == None
            or cached_template.get("template_name") != template_name
        ):
            return self.get_template_by_name(template_name=template_name)

        return cached_template.get("template")

    # 템플릿 객체를 복사해옴
    def get_template_by_name(self, template_name) -> ViewTemplate:
        loaded_template = self.__template_dict__.get(template_name)

        if not loaded_template:
            raise ValueError(f"템플릿이 존재하지 않습니다. [{template_name}]")

        return copy.deepcopy(loaded_template)

    def create_view_template(self, template_name, template_options):
        template = ViewTemplate(template_name, dict())

        # template dict에 해당 option 추가
        for option_name in template_options:
            template.add_template_line(line=option_name, block=None)

        self.set_template_dict(template)

        return template

    # 템플릿을 적용, 템플릿을 블럭으로 변환 한다는 의미
    def apply_template(self, view, template: ViewTemplate):
        self.update_template_cache(
            creator_id=view["private_metadata"], template=template
        )

        updated_view = view
        updated_view["blocks"] = template.convert_template_to_blocks()

        return updated_view


template_manager = ViewTemplateManager()
