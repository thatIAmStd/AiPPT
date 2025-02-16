import os
import sys

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.image_advisor import ImageAdvisor
from ppt.config import Config
from ppt.input_parser import parse_input_text
from ppt.layout_manager import LayoutManager
from ppt.ppt_generator import generate_presentation
from ppt.template_manager import load_template, get_layout_mapping
from logger import LOG
from llm.chatbot import ChatBot

config = Config()
chatbot = ChatBot(config.chatbot_prompt)

ppt_template = config.ppt_template
layout_mapping = get_layout_mapping(load_template(ppt_template))

layout_manager = LayoutManager(layout_mapping)

image_advisor = ImageAdvisor()


def generate_contents(message, history):
    # 用户输入信息列表
    inputs = []
    LOG.debug(f"history:{history}")

    text_input = message.get("text")
    if text_input:
        inputs.append(text_input)

    # todo 上传文件处理，doc解析，语音转文字

    user_input = "需求如下：\n" + "\n".join(inputs)

    slides_content = chatbot.chat_with_history(user_input)
    LOG.info(slides_content)

    return slides_content


def handle_image_generate(history):
    try:
        slides_content = history[-1]["content"]
        LOG.info(f"一键配图：{slides_content}")

        content_with_images, image_pair = image_advisor.generate_images(slides_content)
        new_message = {"role": "assistant", "content": content_with_images}

        history.append(new_message)
        return history
    except Exception as e:
        LOG.error(f"生产图片错误：{e}")
        raise gr.Error(f"生产图片错误，请刷新重试。错误日志如下：{e}")


def generate_ppt(history):
    try:
        # 聊天记录的最新内容
        slides_content = history[-1]["content"]
        LOG.info(f"生成PPT：{slides_content}")

        # 解析 markdown 格式的内容，转换为ppt的数据结构
        ppt_data, ppt_title = parse_input_text(slides_content, layout_manager)
        output_path = f"outputs/{ppt_title}.pptx"

        # 生成ppt
        generate_presentation(ppt_data, ppt_template, output_path)
        return output_path
    except Exception as e:
        LOG.error(f"生成PPT失败：{e}")
        raise gr.Error(f"生成PPT失败，请刷新重试。错误日志如下：{e}")


# 创建 Gradio 界面
with gr.Blocks(
        title="AiPPT",
        css="""
    body { animation: fadeIn 2s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    """
) as demo:
    # 添加标题
    gr.Markdown("## AiPPT")

    # 定义语音（mic）转文本的接口
    # gr.Interface(
    #     fn=transcribe,  # 执行转录的函数
    #     inputs=[
    #         gr.Audio(sources="microphone", type="filepath"),  # 使用麦克风录制的音频输入
    #     ],
    #     outputs="text",  # 输出为文本
    #     flagging_mode="never",  # 禁用标记功能
    # )

    # 创建聊天机器人界面，提示用户输入
    contents_chatbot = gr.Chatbot(
        placeholder="<h1>AI 一键生成 PPT</h1><br> <h4>聊天界面输入你的主题内容 ，比如：'固态电池的发展与未来'。回车发送消息，如果需要配图，则点击一键配图，再点击一键生成PPT</h4><br> ",
        height=600,
        type="messages",
    )

    # 定义 ChatBot 和生成内容的接口
    gr.ChatInterface(
        fn=generate_contents,  # 处理用户输入的函数
        chatbot=contents_chatbot,  # 绑定的聊天机器人
        type="messages",
        multimodal=True  # 支持多模态输入（文本和文件）
    )

    image_generate_btn = gr.Button("一键配图")
    image_generate_btn.click(
        fn=handle_image_generate,
        inputs=contents_chatbot,
        outputs=contents_chatbot
    )

    generate_btn = gr.Button("一键生成PPT")
    generate_btn.click(
        fn=generate_ppt,
        inputs=contents_chatbot,
        outputs=gr.File()
    )

# 主程序入口
if __name__ == "__main__":
    # 启动Gradio应用，允许队列功能，并通过 HTTPS 访问
    demo.queue().launch(
        share=False,
        server_name="0.0.0.0",
        # auth=("x", "x") # ⚠️注意：记住修改密码
    )
