"""
    聊天机器人抽象类
"""
from abc import ABC

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from llm.chat_history import get_session_history
from src.logger import LOG


class ChatBot(ABC):

    def __init__(self, prompt_file: str, session_id: str = None):
        """
        :param prompt_file:
        :param session_id:
        """
        self.prompt_file = prompt_file
        self.session_id = session_id if session_id else 'default_session_id'
        self.system_prompt = self.load_prompt()
        self.load_chatbot()

    def load_prompt(self):
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")

    def load_chatbot(self):
        """
        构建提示词模板
        """
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),  # 系统提示词
            MessagesPlaceholder(variable_name="messages"),  # 消息占位符
        ])
        LOG.debug(f"加载 system_prompt:{system_prompt.messages}")

        # 构建聊天机器人
        self.chatbot = system_prompt | ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=4096
        )

        # 构建消息历史
        self.chatbot_with_history = RunnableWithMessageHistory(self.chatbot, get_session_history)

    def chat_with_history(self, user_input, session_id=None):

        response = self.chatbot_with_history.invoke(
            [HumanMessage(content=user_input)],
            {"configurable": {"session_id": session_id}},  # 传入配置，包括会话ID
        )
        LOG.debug(f"chat_bot response:{response}")
        return response.content
