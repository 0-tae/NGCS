import copy


class ViewTemplateObject:
    def __init__(self, template_name, template: dict()):
        self.template_name = template_name
        self.template = template  # dict

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
    # 뷰 업데이트로 인해 블럭의 갯수가 줄어들 경우, Line key의 선형 조회로 인해 블럭이 기존과 다른 라인에 매칭되는 현상
    # 예) Block: B1 B2 B3 B4 B5 , Line: L1 L2 L3 L4 L5 일때,
    # 매칭 결과 : B1(L1) B2(L2) B3(L3) B4(L4) B5(L5)
    # 만약 업데이트로 인해 B3가 사라질 경우
    # 초기화된 템플릿으로 인해
    # B1(B1) B2(L2) B4(L3) B5(L4) none(L5)가 되는 상황

    def convert_view_to_template(self, view):
        blocks = view["blocks"]
        template_lines = list(self.get_template().keys())
        unmatched_line = list()

        block_idx = 0

        for line_idx, line in enumerate(template_lines):
            # 처음 블럭 삽입 떄 None인 Line은 건너 뛰고 다음 Line 탐색
            # 단, 블럭의 갯수와 라인의 갯수가 일치하면, None 자리에 삽입
            if (line_idx != block_idx) and line == None:
                unmatched_line.append(line)
            else:
                if block_idx == len(blocks):
                    break
                self.set_template_line(line=line, block=blocks[block_idx])
                block_idx += 1

        for line in unmatched_line:
            if block_idx == len(blocks):
                break
            self.set_template_line(line=line, block=blocks[block_idx])
            block_idx += 1

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

    def set_template_all(self, blocks):
        lines = list(self.get_template().keys())

        if len(lines) != len(blocks):
            raise ValueError(
                f"주어진 블럭의 갯수와 템플릿의 라인 수가 일치하지 않음 -> lines = {len(lines)}, given_blocks = {len(blocks)}"
            )

        for index, block in enumerate(blocks):
            self.set_template_line(lines[index], block)

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
    __template_cache__ = dict()

    # 유저 아이디를 통해 현재 템플릿을 템플릿 캐시에 저장
    def update_template_cache(self, creator_id, template: ViewTemplateObject):
        self.__template_cache__.update(
            {
                creator_id: {
                    "template": template,
                    "template_name": template.get_template_name(),
                },
            }
        )

    # 유저 아이디를 통해 저장된 템플릿을 가져옴
    def get_template_cache(self, creator_id) -> ViewTemplateObject:
        return self.__template_cache__.get(creator_id)

    # 유저 아이디를 통해 템플릿 캐시를 삭제(submit 시)
    def destroy_template_cache(self, creator_id) -> ViewTemplateObject:
        self.__template_cache__.pop(creator_id)

    # 템플릿을 템플릿 딕셔너리에 등록
    def set_template_dict(self, template: ViewTemplateObject):
        self.__template_dict__[template.get_template_name()] = template

    def load_template_by_creator_id_with_name(
        self, creator_id, template_name
    ) -> ViewTemplateObject:
        cached_template = self.get_template_cache(creator_id=creator_id)

        # 캐시된 템플릿이 없거나 템플릿 네임과 불일치한 캐시를 가지고 있다면, 새로 생성
        if (
            cached_template == None
            or cached_template.get("template_name") != template_name
        ):
            return self.get_template_by_name(template_name=template_name)

        return cached_template.get("template")

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

    # 템플릿을 적용, 템플릿을 블럭으로 변환 한다는 의미
    def apply_template(self, view, template: ViewTemplateObject):
        self.update_template_cache(
            creator_id=view["private_metadata"], template=template
        )

        updated_view = view
        updated_view["blocks"] = template.convert_template_to_blocks()

        return updated_view


template_manager = ViewTemplateObjectManager()
