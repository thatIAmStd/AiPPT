"""
    布局管理模块：
    基于权重计算，来进行布局模板匹配
"""
from idlelib.iomenu import encoding
from typing import List, Tuple

from logger import LOG
from ppt.layout_strategy import LayoutStrategy
from ppt.ppt_data import SlideContent

# 定义 content_type 对应的权重
CONTENT_TYPE_WEIGHTS = {
    'Title': 1,
    'Content': 2,
    'Picture': 4
}


# 计算content_type的权重
def calculate_layout_weights(layout_name: str) -> int:
    # layout_name格式：Title, Content, Picture 0
    splits = layout_name.split(", ")

    # 去除后面的数字，此处只计算权重
    content_types = (x.split(" ")[0] for x in splits)
    weight_sums = sum(CONTENT_TYPE_WEIGHTS.get(c_type, 0) for c_type in content_types)
    return weight_sums


def calculate_content_encoding(slide_content):
    """
    根据幻灯片内容类型，计算权重，然后进行编码

    :param slide_content:
    :return:
    """
    encode = 0
    if slide_content.title:
        encode += CONTENT_TYPE_WEIGHTS.get('Title', 0)
    if slide_content.bullet_points:
        encode += CONTENT_TYPE_WEIGHTS.get('Content', 0)
    if slide_content.image_path:
        encode += CONTENT_TYPE_WEIGHTS.get('Picture', 0)

    return encode


# 布局管理器，根据输入内容，自动选择合适的布局策略
class LayoutManager:
    """
        布局管理器根据 SlideContent 的内容（如标题、要点和图片）自动选择合适的布局策略，并随机选择一个布局。
        """

    def __init__(self, layout_mapping: dict):
        self.layout_mapping = layout_mapping  # 布局映射配置

        # 初始化布局策略，提前为所有布局创建策略并存储在字典中
        self.strategies = {
            1: self._create_strategy(1),  # 仅 Title
            3: self._create_strategy(3),  # Title + Content
            5: self._create_strategy(5),  # Title + Picture
            7: self._create_strategy(7)  # Title + Content + Picture
        }

        # 打印调试信息
        LOG.debug(f"LayoutManager 初始化完成:\n {self}")

    def assign_layout(self, slide_content: SlideContent):
        # 根据幻灯片内容类型，来进行权重编码，再通过权重值分配对应的布局
        encode_weight = calculate_content_encoding(slide_content)
        strategy = self.strategies.get(encode_weight)
        return strategy.get_layout(slide_content)

    def _create_strategy(self, layout_type: int) -> LayoutStrategy:
        """
        根据布局类型创建通用的布局策略，并生成布局组，记录布局组的 debug 信息。
        """
        layout_group = [
            (layout_id, layout_name) for layout_name, layout_id in self.layout_mapping.items()
            if calculate_layout_weights(layout_name) == layout_type
        ]

        # Debug 级别日志输出，查看各个布局组的详细情况
        LOG.debug(f"创建 {layout_type} 编码对应的布局组，共 {len(layout_group)} 个布局: {layout_group}")

        return LayoutStrategy(layout_group)
