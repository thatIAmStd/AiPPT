"""
    解析markdown 格式的内容，转换为ppt的数据结构
"""
import re
from typing import Optional, Tuple

from ppt.layout_manager import LayoutManager
from ppt.ppt_data import PowerPoint
from ppt.slide.slide_builder import SlideBuilder


def parse_input_text(input_text: str, layout_manager: LayoutManager) -> tuple[PowerPoint, str]:
    """
    解析输入的文本并转换为 PowerPoint 数据结构。自动为每张幻灯片分配适当的布局。
    """
    lines = input_text.split('\n')  # 按行拆分文本
    presentation_title = ""  # PowerPoint 的主标题
    slides = []  # 存储所有幻灯片
    slide_builder: Optional[SlideBuilder] = None  # 当前幻灯片的构建器

    # 正则表达式，用于匹配幻灯片标题、要点和图片
    slide_title_pattern = re.compile(r'^##\s+(.*)')
    bullet_pattern = re.compile(r'^(\s*)-\s+(.*)')
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        if line.strip() == "":
            continue  # 跳过空行

        # 主标题 (用作 PowerPoint 的标题和文件名)
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()

            first_slide_builder = SlideBuilder(layout_manager)
            first_slide_builder.set_title(presentation_title)
            slides.append(first_slide_builder.build())

        # 幻灯片标题
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title = match.group(1).strip()

                # 如果有当前幻灯片，生成并添加到幻灯片列表中
                if slide_builder:
                    slides.append(slide_builder.build())

                # 创建新的 SlideBuilder
                slide_builder = SlideBuilder(layout_manager)
                slide_builder.set_title(title)

        # 项目符号（要点）
        elif bullet_pattern.match(line) and slide_builder:
            match = bullet_pattern.match(line)
            if match:
                indent_spaces, bullet = match.groups()  # 获取缩进空格和项目符号内容
                indent_level = len(indent_spaces) // 2  # 计算缩进层级，每 2 个空格为一级
                bullet_text = bullet.strip()  # 获取项目符号的文本内容

                # 根据层级添加要点
                slide_builder.add_bullet_point(bullet_text, level=indent_level)

        # 图片插入
        elif line.startswith('![') and slide_builder:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                slide_builder.set_image(image_path)

    # 为最后一张幻灯片分配布局并添加到列表中
    if slide_builder:
        slides.append(slide_builder.build())

    # 返回 PowerPoint 数据结构以及演示文稿标题
    return PowerPoint(title=presentation_title, slides=slides),presentation_title
