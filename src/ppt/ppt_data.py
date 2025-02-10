"""
    此模块定义ppt的数据结构。后续的ppt生产都是解析此数据结构进行生成
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional

# 定义幻灯片的内容，包括标题、要点列表（支持多级），图片路径
@dataclass
class SlideContent:
    title: str
    # 要点列表，包含每个要点的文本和层级
    bullet_points: List[dict] = field(default_factory=list)
    image_path: Optional[str] = None


# 定义每张幻灯片，包括布局 ID、布局名称以及幻灯片内容。
@dataclass
class Slide:
    layout_id: int
    layout_name: str
    content: SlideContent


# 整个 PowerPoint 演示文稿，包括标题和幻灯片列表。
@dataclass
class PowerPoint:
    title: str
    slides: List[Slide] = field(default_factory=list)

    # 获取PowerPoint的json结构，包含SlideContent
    def to_json(self) -> dict:
        return {
            'title': self.title,
            'slides': [
                {
                    'layout_id': slide.layout_id,
                    'layout_name': slide.layout_name,
                    'content': {
                        'title': slide.content.title,
                        'bullet_points': slide.content.bullet_points,
                        'image_path': slide.content.image_path
                    }
                }
                for slide in self.slides
            ]
        }

    # 重写str方法，直接打印字典字符串
    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=4)
