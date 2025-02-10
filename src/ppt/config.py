import os.path
from src.logger import LOG

import json


class Config:

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.load_config(config_file)

    def load_config(self, config_file: str):

        #   判断文件是否存在
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件 '{config_file}' 不存在。")

        try:
            with open(config_file, 'r') as file:
                configs = json.load(file)
                # 加载 运行模式，默认为 "text" 模式
                self.input_mode = configs.get('input_mode', "text")

                # 加载 PPT 默认模板路径，若未指定则使用默认模板
                self.ppt_template = configs.get('ppt_template', "templates/MasterTemplate.pptx")

                # 加载 ChatBot 提示信息
                self.chatbot_prompt = configs.get('chatbot_prompt', '')

                # 加载内容格式化提示和助手提示
                self.content_formatter_prompt = configs.get('content_formatter_prompt', '')
                self.content_assistant_prompt = configs.get('content_assistant_prompt', '')
                self.image_advisor_prompt = configs.get('image_advisor_prompt', '')
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件 '{config_file}' 无效。") from e
