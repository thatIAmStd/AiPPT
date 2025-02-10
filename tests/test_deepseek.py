import unittest

from langchain_openai.chat_models.base import BaseChatOpenAI


class TestDeepseek(unittest.TestCase):

    def test_ppt_gen(self):
        llm = BaseChatOpenAI(
            model='deepseek-chat',
            base_url="https://api.deepseek.com/v1",
            api_key=""
        )
        response = llm.invoke("Hi!")
        print(response.content)


