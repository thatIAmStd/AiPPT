"""
    布局策略：
    基于权重计算，来进行布局模板匹配
"""
import random
from typing import List, Tuple


# 布局策略类，此处只做简单实现：从布局组中随机选择一个布局模板
class LayoutStrategy:

    def __init__(self, layout_group: List[Tuple[int, str]]):
        self.layout_group = layout_group

    def get_layout(self, slide_content) -> Tuple[int, str]:
        """
        根据幻灯片内容，选择合适的布局。此处使用最简单的随机选择
        :param slide_content:
        :return:
        """
        return random.choice(self.layout_group)
