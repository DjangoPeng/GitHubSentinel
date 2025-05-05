import os
import json
import requests  # 用于调用DeepSeek API
from logger import LOG  # 导入日志模块


class LLM:
    def __init__(self):
        # 初始化DeepSeek API配置
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-da4403c03da1440db45dc626a781747b")  # 优先从环境变量获取API密钥
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        # 从TXT文件加载提示信息
        with open("./../prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("logs/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")

        try:
            # 调用DeepSeek API生成报告
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": messages
            }
            response = requests.post(self.api_url, headers=headers, json=payload)
            response_data = response.json()
            LOG.debug("GPT response: {}", response_data)

            # 检查API响应是否包含错误
            if response.status_code != 200 or 'error' in response_data:
                error_msg = response_data.get('error', {}).get('message', 'Unknown API error')
                LOG.error("API Error: {}", error_msg)
                if 'Insufficient Balance' in error_msg:
                    raise Exception("DeepSeek API余额不足，请充值后再试。")
                else:
                    raise Exception(f"API Error: {error_msg}")

            # 返回模型生成的内容
            return response_data['choices'][0]['message']['content']
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
