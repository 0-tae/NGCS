class ViewTemplate:
    def __init__(self, __template_name__, __template__: dict):
        self.__template_name__ = __template_name__
        self.__template__ = __template__  # dict

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

    # Issue
    # view.blocks 안의 첫 번째 요소부터, 템플릿에 순서대로 삽입
    # 뷰 업데이트로 인해 블럭의 갯수가 줄어들 경우, Line key의 선형 조회로 인해 블럭이 기존과 다른 라인에 매칭되는 현상
    # 예) Block: B1 B2 B3 B4 B5 , Line: L1 L2 L3 L4 L5 일때,
    # 매칭 결과 : B1(L1) B2(L2) B3(L3) B4(L4) B5(L5)
    # 만약 업데이트로 인해 B3가 사라질 경우, 초기화된 템플릿으로 인해
    # B1(B1) B2(L2) B4(L3) B5(L4) none(L5)가 되는 상황
    def convert_view_to_template(self, view):
        blocks = view["blocks"]
        template_lines = list(self.get_template().keys())
        unmatched_line = list()

        block_idx = 0

        for line_idx, line in enumerate(template_lines):
            # 처음 블럭 삽입 때, None인 Line은 건너 뛰고 다음 Line 탐색
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
        self.__template__.update({line: block})

    # 라인에 대해 블럭을 설정함
    def set_template_line(self, line, block):
        if line not in list(self.get_template().keys()):
            raise ValueError(
                f"현재 템플릿에 존재하지 않는 line에 대한 업데이트를 시도함 -> {line} is not in {list(self.get_template().keys())}"
            )

        self.__template__.update({line: block})

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
        return self.__template__.get(line_name)

    # 현재 ViewTemplate 객체의 template를 설정함
    def set_template(self, new_template):
        self.__template__ = new_template

    # 현재 ViewTemplate 객체의 tempalte(dict)를 가져옴
    def get_template(self) -> dict:
        return self.__template__

    # 템플릿의 이름을 가져옴
    def get_template_name(self):
        return self.__template_name__
