import json
import requests
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self, config):
        """
        初始化 LLM 类，根据配置选择使用的模型（OpenAI 或 Ollama）。
        
        :param config: 配置对象，包含所有的模型配置参数。
        """
        self.config = config
        self.model = config.llm_model_type.lower()  # 获取模型类型并转换为小写
        if self.model == "openai":
            from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
            self.client = OpenAI()  # 创建OpenAI客户端实例
        elif self.model == "ollama":
            self.api_url = config.ollama_api_url  # 设置Ollama API的URL
        else:
            raise ValueError(f"Unsupported model type: {self.model}")  # 如果模型类型不支持，抛出错误
        
        # 从TXT文件加载系统提示信息
        with open("prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()

    def generate_daily_report(self, markdown_content, dry_run=False):
        """
        生成每日报告，根据配置选择不同的模型来处理请求。
        
        :param markdown_content: 用户提供的Markdown内容。
        :param dry_run: 如果为True，提示信息将保存到文件而不实际调用模型。
        :return: 生成的报告内容或"DRY RUN"字符串。
        """
        # 准备消息列表，包含系统提示和用户内容
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)  # 将消息保存为JSON格式
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")
            return "DRY RUN"

        # 根据选择的模型调用相应的生成报告方法
        if self.model == "openai":
            return self._generate_report_openai(messages)
        elif self.model == "ollama":
            return self._generate_report_ollama(messages)
        else:
            raise ValueError(f"Unsupported model type: {self.model}")

    def _generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 OpenAI GPT 模型开始生成报告。")
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 使用配置中的OpenAI模型名称
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_report_ollama(self, messages):
        """
        使用 Ollama LLaMA 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 Ollama 托管模型服务开始生成报告。")
        try:
            payload = {
                "model": self.config.ollama_model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "stream": False
            }
            response = requests.post(self.api_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()
            
            # 调试输出查看完整的响应结构
            LOG.debug("Ollama response: {}", response_data)
            
            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Invalid response structure from Ollama API")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise


if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    config = Config()
    llm = LLM(config)

    markdown_content="""
# Progress for langchain-ai/langchain (2024-08-20 to 2024-08-21)


## Issues Closed in the Last 1 Days
- partners/chroma: release 0.1.3 #25599
- docs: few-shot conceptual guide #25596
- docs: update examples in api ref #25589
"""

    report = llm.generate_daily_report(markdown_content, dry_run=False)
    print(report)
