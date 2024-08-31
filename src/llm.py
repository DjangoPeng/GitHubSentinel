import json
import os
import requests
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型

from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self, config):
        """
        初始化 LLM 类，根据配置选择使用的模型（OpenAI 或 Ollama），并预加载所有可能的提示信息。
        
        :param config: 配置对象，包含所有的模型配置参数。
        """
        self.config = config
        self.model = config.llm_model_type.lower()  # 获取模型类型并转换为小写
        self.prompts = {}  # 存储所有预加载的提示信息
        if self.model == "openai":
            self.client = OpenAI()  # 创建OpenAI客户端实例
        elif self.model == "ollama":
            self.api_url = config.ollama_api_url  # 设置Ollama API的URL
        else:
            LOG.error(f"不支持的模型类型: {self.model}")
            raise ValueError(f"不支持的模型类型: {self.model}")  # 如果模型类型不支持，抛出错误
        
        # 预加载所有可能的系统提示文件
        self._preload_prompts()

    def _preload_prompts(self):
        """
        预加载所有可能的提示文件，并存储在字典中。
        """
        for report_type in self.config.report_types:  # 使用从配置中加载的报告类型
            prompt_file = f"prompts/{report_type}_{self.model}_prompt.txt"
            if not os.path.exists(prompt_file):
                LOG.error(f"提示文件不存在: {prompt_file}")
                raise FileNotFoundError(f"提示文件未找到: {prompt_file}")
            with open(prompt_file, "r", encoding='utf-8') as file:
                self.prompts[report_type] = file.read()

    def generate_report(self, report_type, markdown_content, dry_run=False):
        """
        生成报告，根据配置选择不同的模型来处理请求。
        
        :param report_type: 报告类型（例如 "github" 或 "hacker_news"）。
        :param markdown_content: 用户提供的Markdown内容。
        :param dry_run: 如果为True，提示信息将保存到文件而不实际调用模型。
        :return: 生成的报告内容或"DRY RUN"字符串。
        """
        if report_type not in self.prompts:
            LOG.error(f"无效的报告类型: {report_type}")
            raise ValueError(f"不支持的报告类型: {report_type}")

        system_prompt = self.prompts[report_type]

        # 准备消息列表，包含系统提示和用户内容
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info(f"干运行模式已启用，保存 {report_type} 报告的提示信息到文件中。")
            with open(f"daily_progress/{report_type}_prompt.txt", "w+") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)  # 将消息保存为JSON格式
            LOG.debug(f"提示信息已保存到 daily_progress/{report_type}_prompt.txt")
            return "DRY RUN"

        # 根据选择的模型调用相应的生成报告方法
        if self.model == "openai":
            return self._generate_report_openai(messages, report_type)
        elif self.model == "ollama":
            return self._generate_report_ollama(messages, report_type)
        else:
            raise ValueError(f"不支持的模型类型: {self.model}")

    def _generate_report_openai(self, messages, report_type):
        """
        使用 OpenAI GPT 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :param report_type: 报告类型（例如 "github" 或 "hacker_news"）。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 OpenAI {self.config.openai_model_name} 模型生成 {report_type} 报告。")
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 使用配置中的OpenAI模型名称
                messages=messages
            )
            LOG.debug("GPT 响应: {}", response)
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_report_ollama(self, messages, report_type):
        """
        使用 Ollama LLaMA 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :param report_type: 报告类型（例如 "github" 或 "hacker_news"）。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 Ollama {self.config.ollama_model_name} 模型生成 {report_type} 报告。")
        try:
            payload = {
                "model": self.config.ollama_model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "stream": False
            }
            response = requests.post(self.api_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()
            
            # 调试输出查看完整的响应结构
            LOG.debug("Ollama 响应: {}", response_data)
            
            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Ollama API 返回的响应结构无效")
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

    # 生成 GitHub 报告
    github_report = llm.generate_report("github", markdown_content)
    print(github_report)
