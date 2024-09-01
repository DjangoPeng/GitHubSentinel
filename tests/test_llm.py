import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 将 src 目录添加到模块搜索路径，方便导入项目中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import Config  # 导入配置类
from llm import LLM  # 导入要测试的 LLM 类

class TestLLM(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法运行前执行，初始化 LLM 实例和测试数据。
        """
        self.config = Config()  # 初始化配置对象
        self.llm = LLM(self.config)  # 使用配置对象初始化 LLM 实例

        # 设置示例的系统提示信息
        self.system_prompt = "Your specific system prompt for GitHub report generation"

        # 准备用于测试的 GitHub 内容字符串
        self.github_content = """
        # Progress for langchain-ai/langchain (2024-08-20 to 2024-08-21)

        ## Issues Closed in the Last 1 Days
        - partners/chroma: release 0.1.3 #25599
        - docs: few-shot conceptual guide #25596
        - docs: update examples in api ref #25589
        """

    @patch('llm.LOG.error')
    def test_invalid_model_type(self, mock_log_error):
        """
        测试传入无效模型类型时的错误处理路径。
        """
        self.config.llm_model_type = "invalid_model"
        with self.assertRaises(ValueError):
            llm = LLM(self.config)
        mock_log_error.assert_called_with("不支持的模型类型: invalid_model")

    @patch('llm.requests.post')
    @patch('llm.LOG.error')
    def test_ollama_invalid_response_structure(self, mock_log_error, mock_post):
        """
        测试 Ollama API 返回的响应结构无效时的错误处理路径。
        """
        # 模拟 Ollama API 的无效响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid_key": "no_content_here"}
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            self.llm.generate_report(self.system_prompt, self.github_content)
        mock_log_error.assert_called_with("生成报告时发生错误：Ollama API 返回的响应结构无效")


    @patch('llm.LOG.error')
    @patch('llm.OpenAI')
    def test_openai_exception_handling(self, mock_openai, mock_log_error):
        """
        测试调用 OpenAI 模型时发生异常的错误处理路径。
        """
        # 设置为使用 OpenAI 模型
        self.config.llm_model_type = "openai"
        self.llm = LLM(self.config)
        
        # 模拟 OpenAI 客户端抛出异常
        mock_openai().chat.completions.create.side_effect = Exception("OpenAI API error")
        
        with self.assertRaises(Exception):
            self.llm.generate_report(self.system_prompt, self.github_content)
        
        # 检查是否记录了预期的错误日志
        mock_log_error.assert_called_with("生成报告时发生错误：OpenAI API error")


if __name__ == '__main__':
    unittest.main()
