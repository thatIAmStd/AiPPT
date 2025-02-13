"""
    图片生成顾问agent
"""
import os
import re
from abc import ABC
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from logger import LOG


class ImageAdvisor(ABC):

    def __init__(self, prompt_file="./prompts/image_advisor.txt"):
        self.prompt_file = prompt_file
        self.system_prompt = self.load_prompt()
        self.create_advisor()

    def load_prompt(self):
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            raise e

    def create_advisor(self):
        """
            构建提示词模板
            """
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),  # 系统提示词
            ("human","**content** \n {input}")
        ])
        LOG.debug(f"加载 system_prompt:{system_prompt.messages}")

        # 构建聊天机器人
        self.image_advisor = system_prompt | ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=4096
        )

    def generate_images(self, ppt_markdown_content, image_directory="images", num_images=3):
        """
            生成图片，尝试三次

        生成图片并嵌入到指定的 PowerPoint 内容中。

        参数:
            ppt_markdown_content (str): PowerPoint markdown 原始格式
            image_directory (str): 本地保存图片的文件夹名称
            num_images (int): 每个幻灯片搜索的图像数量

        返回:
            content_with_images (str): 嵌入图片后的内容
            image_pair (dict): 每个幻灯片标题对应的图像路径
        """
        response = self.image_advisor.invoke({"input": ppt_markdown_content})
        LOG.debug(f"[Advisor 建议配图]\n{response.content}")

        #   提取关键字
        key_words = self.get_keywords(response.content)
        image_pair = {}  # 存储幻灯片标题和图片的键值对

        # 检索并保存图片
        for slide_title, query in key_words.items():

            images = self.get_bing_images(slide_title, query, num_images, timeout=1, retries=3)
            # 打印日志
            if images:
                for image in images:
                    LOG.debug(
                        f"Name: {image['slide_title']}, Query: {image['query']} 分辨率：{image['width']}x{image['height']}")
            else:
                LOG.warning(f"No images found for {slide_title}.")
                continue

            # 取分辨率最高的，保存
            img = images[0]
            save_directory = f"tmps/generate/{image_directory}"
            os.makedirs(save_directory, exist_ok=True)
            #       保存路径
            save_path = os.path.join(save_directory, f"{img['slide_title']}_1.jpeg")
            self.save_image(img["obj"], save_path)
            image_pair[img["slide_title"]] = save_path

        # 把保存的图片路径插入到markdown里面
        content_with_images = self.insert_images(ppt_markdown_content, image_pair)
        return content_with_images, image_pair

    def get_keywords(self, advice):
        """
        使用正则表达式提取关键词。

        参数:
            advice (str): 提示文本
        返回:
            keywords (dict): 提取的关键词字典
        """
        pairs = re.findall(r'\[(.+?)\]:\s*(.+)', advice)
        keywords = {title.strip(): query.strip() for title, query in pairs}
        LOG.debug(f"[检索关键词 正则提取结果]{keywords}")
        return keywords

    def get_bing_images(self, slide_title, query, num_images=5, timeout=1, retries=3):
        """
        从 Bing 检索图像，最多重试3次。

        参数:
            slide_title (str): 幻灯片标题
            query (str): 图像搜索关键词
            num_images (int): 搜索的图像数量
            timeout (int): 每次请求超时时间（秒），默认1秒
            retries (int): 最大重试次数，默认3次

        返回:
            sorted_images (list): 符合条件的图像数据列表
        """
        url = f"https://www.bing.com/images/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }

        # 尝试请求并设置重试逻辑
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                break  # 请求成功，跳出重试循环
            except requests.RequestException as e:
                LOG.warning(f"Attempt {attempt + 1}/{retries} failed for query '{query}': {e}")
                if attempt == retries - 1:
                    LOG.error(f"Max retries reached for query '{query}'.")
                    return []

        soup = BeautifulSoup(response.text, "html.parser")
        image_elements = soup.select("a.iusc")

        image_links = []
        for img in image_elements:
            m_data = img.get("m")
            if m_data:
                m_json = eval(m_data)
                if "murl" in m_json:
                    image_links.append(m_json["murl"])
            if len(image_links) >= num_images:
                break

        image_data = []
        for link in image_links:
            for attempt in range(retries):
                try:
                    img_data = requests.get(link, headers=headers, timeout=timeout)
                    img = Image.open(BytesIO(img_data.content))
                    image_info = {
                        "slide_title": slide_title,
                        "query": query,
                        "width": img.width,
                        "height": img.height,
                        "resolution": img.width * img.height,
                        "obj": img,
                    }
                    image_data.append(image_info)
                    break  # 成功下载图像，跳出重试循环
                except Exception as e:
                    LOG.warning(f"Attempt {attempt + 1}/{retries} failed for image '{link}': {e}")
                    if attempt == retries - 1:
                        LOG.error(f"Max retries reached for image '{link}'. Skipping.")

        sorted_images = sorted(image_data, key=lambda x: x["resolution"], reverse=True)
        return sorted_images

    def save_image(self, img, save_path, format="JPEG", quality=85, max_size=1080):
        """
        保存图像到本地并压缩。

        参数:
            img (Image): 图像对象
            save_path (str): 保存路径
            format (str): 保存格式，默认 JPEG
            quality (int): 图像质量，默认 85
            max_size (int): 最大边长，默认 1080
        """
        try:
            width, height = img.size
            if max(width, height) > max_size:
                scaling_factor = max_size / max(width, height)
                new_width = int(width * scaling_factor)
                new_height = int(height * scaling_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if img.mode == "RGBA":
                format = "PNG"
                save_options = {"optimize": True}
            else:
                save_options = {
                    "quality": quality,
                    "optimize": True,
                    "progressive": True
                }

            img.save(save_path, format=format, **save_options)
            LOG.debug(f"Image saved as {save_path} in {format} format with quality {quality}.")
        except Exception as e:
            LOG.error(f"Failed to save image: {e}")

    def insert_images(self, markdown_content, image_pair):
        """
        将图像嵌入到 Markdown 内容中。

        参数:
            markdown_content (str): Markdown 内容
            image_pair (dict): 幻灯片标题到图像路径的映射

        返回:
            new_content (str): 嵌入图像后的内容
        """
        lines = markdown_content.split('\n')
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            if line.startswith('## '):
                slide_title = line[3:].strip()
                if slide_title in image_pair:
                    image_path = image_pair[slide_title]
                    image_markdown = f'![{slide_title}]({image_path})'
                    new_lines.append(image_markdown)
            i += 1
        new_content = '\n'.join(new_lines)
        return new_content
