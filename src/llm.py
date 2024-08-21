# src/llm.py

import os
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self):
        # 【修改1】创建一个OpenAI客户端实例，使用环境变量中的API密钥和自定义的API端点
        self.client = OpenAI(api_key=os.getenv('WildtoOpenAI'),
                            base_url="https://api.gptsapi.net/v1"
                            )
        
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 【修改2】构建system prompt，要求模型以报告生成器的身份进行交互
        system_prompt = "你是一个专注于信息处理与报告生成的高级助手。你的任务是从复杂的数据中提炼出关键信息，并生成结构清晰、内容简洁的报告。确保在处理信息时逻辑严谨、层次分明，最终报告应突出重要更新并合并类似内容。"
        
        # 构建一个用于生成报告的提示文本，要求生成的报告包含新增功能、主要改进和问题修复
        user_prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(user_prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 指定使用的模型版本
                messages=[
                    {"role": "system", "content": system_prompt},  # 提交系统角色的消息
                    {"role": "user", "content": user_prompt}  # 提交用户角色的消息
                ]
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
