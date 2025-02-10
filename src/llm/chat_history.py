"""
    聊天机器人历史模块

"""
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

# 聊天会话历史的字典
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
        获取指定会话的聊天历史，如果不存在，则创建一个
    :param session_id: 会话id
    """

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
