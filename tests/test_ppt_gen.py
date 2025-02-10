import os
import sys
import unittest

from pptx import Presentation

from ppt.input_parser import parse_input_text
from ppt.layout_manager import LayoutManager
from ppt.ppt_generator import generate_presentation
from ppt.template_manager import get_layout_mapping

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# print(f"现在可以访问的路径包括: {sys.path}")


class TestPpt(unittest.TestCase):

    def test_ppt_gen(self):
        input_text = """# [PPT文件名称]

## 收入情况
- 总收入增长15%
- 市场份额扩大至30%

## 业绩图表
- OpenAI 利润不断增加
![业绩图表](images/test.png)

## 新产品发布
- 产品A: 特色功能介绍
- 产品B: 市场定位
![未来增长](images/test.png)"""

        prs = Presentation("D:/codeSpace/ai/AiPPT/templates/SimpleTemplate.pptx")
        layout_mapping = get_layout_mapping(prs)
        layout_manager = LayoutManager(layout_mapping)
        ppt_data = parse_input_text(input_text, layout_manager)
        generate_presentation(ppt_data, "D:/codeSpace/ai/AiPPT/templates/SimpleTemplate.pptx",
                              "D:/codeSpace/ai/AiPPT/templates/SimpleTemplate_demo.pptx")
