"""
    构建单张幻灯片模块
    SlideBuilder 类用于构建单张幻灯片并通过 LayoutManager 自动分配布局
"""
from ppt.layout_manager import LayoutManager
from ppt.ppt_data import Slide, SlideContent


class SlideBuilder:

    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.title = ""  # 幻灯片标题
        self.bullet_points = []  # 幻灯片要点列表，支持多级结构
        self.image_path = None  # 幻灯片图片列表

    def set_title(self, title: str):
        self.title = title

    def add_bullet_point(self, bullet_text: str, level: int = 0):
        self.bullet_points.append({"text": bullet_text, "level": level})

    def set_image(self, image_path: str):
        self.image_path = image_path

    def build(self) -> Slide:
        slide_content = SlideContent(
            self.title,
            self.bullet_points,
            self.image_path
        )
        layout_id, layout_name = self.layout_manager.assign_layout(slide_content)
        return Slide(layout_id, layout_name, slide_content)
