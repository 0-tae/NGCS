import copy


class ViewTemplateObject:
    def __init__(self, template_name, template: dict()):
        self.template_name = template_name
        self.template = template

    # 받아온 템플릿을 현재 ViewTemplate 규격에 맞추어 블럭으로 변환함
    def convert_template_to_blocks(self):
        template_lines = list(self.get_template().keys())
        blocks = list()

        # 현재 템플릿의 line_name을 통해, 주어진 템플릿 line의 block을 가져옴
        for line in template_lines:
            block = self.get_template_block_in_line(line)
            if not block == None:
                blocks.append(block)

        return blocks

    # view.blocks 안의 첫 번째 요소부터, 템플릿에 순서대로 삽입
    def convert_view_to_template(self, view):
        blocks = view["blocks"]
        template_lines = list(self.get_template().keys())

        for index, block in enumerate(blocks):
            self.set_template_line(line=template_lines[index], block=block)

        return self.get_template()

    # 템플릿에 라인을 추가함
    def add_template_line(self, line, block):
        self.template.update({line: block})

    # 라인에 대해 블럭을 설정함
    def set_template_line(self, line, block):
        if line not in list(self.get_template().keys()):
            raise ValueError(
                f"현재 템플릿에 존재하지 않는 line에 대한 업데이트를 시도함 -> {line} is not in {list(self.get_template().keys())}"
            )

        self.template.update({line: block})

    # 해당 라인에 존재하는 블럭을 가져옴
    def get_template_block_in_line(self, line_name):
        return self.template.get(line_name)

    # 현재 ViewTemplate 객체의 template를 설정함
    def set_template(self, new_template):
        self.template = new_template

    # 현재 ViewTemplate 객체의 tempalte(dict)를 가져옴
    def get_template(self) -> dict():
        return self.template

    # 템플릿의 이름을 가져옴
    def get_template_name(self):
        return self.template_name


class ViewTemplateObjectManager:
    __template_dict__ = dict()

    def set_template_dict(self, template: ViewTemplateObject):
        self.__template_dict__[template.get_template_name()] = template

    # 템플릿 객체를 복사해옴
    def get_template_by_name(self, template_name) -> ViewTemplateObject:
        return copy.deepcopy(self.__template_dict__.get(template_name))

    def create_view_template(self, template_name, template_options):
        template = ViewTemplateObject(template_name, dict())

        # template dict에 해당 option 추가
        for option_name in template_options:
            template.add_template_line(line=option_name, block=None)

        self.set_template_dict(template)

        return template

    def apply_template(self, view, template: ViewTemplateObject):
        updated_view = view
        updated_view["blocks"] = template.convert_template_to_blocks()

        return updated_view


template_manager = ViewTemplateObjectManager()
