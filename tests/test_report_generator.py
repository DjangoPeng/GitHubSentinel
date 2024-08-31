import sys
import os
import unittest
from unittest.mock import MagicMock

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from report_generator import ReportGenerator  # 导入要测试的 ReportGenerator 类

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法之前运行，初始化测试环境。
        """
        # 创建一个模拟的 LLM（大语言模型）对象
        self.mock_llm = MagicMock()
        # 初始化 ReportGenerator 实例，并传入模拟的 LLM 对象
        self.report_generator = ReportGenerator(self.mock_llm)
        # 设置测试用的 Markdown 文件路径
        self.test_markdown_file_path = 'test_daily_progress.md'

        # 模拟 Markdown 文件的内容，代表一个项目的每日进展
        self.markdown_content = """
        # Daily Progress for DjangoPeng/openai-quickstart (2024-08-24)

        ## Issues Closed Today
        - Fix bug #123
        """

        # 创建测试用的 Markdown 文件并写入内容
        with open(self.test_markdown_file_path, 'w') as file:
            file.write(self.markdown_content)

    def tearDown(self):
        """
        在每个测试方法之后运行，清理测试环境。
        """
        # 删除测试用的 Markdown 文件
        if os.path.exists(self.test_markdown_file_path):
            os.remove(self.test_markdown_file_path)
        # 删除生成的报告文件
        report_file_path = os.path.splitext(self.test_markdown_file_path)[0] + "_report.md"
        if os.path.exists(report_file_path):
            os.remove(report_file_path)

    def test_generate_daily_report(self):
        """
        测试 generate_daily_report 方法是否正确生成报告并保存到文件。
        """
        # 模拟 LLM 返回的报告内容
        mock_report = "This is a generated report."
        self.mock_llm.generate_report.return_value = mock_report  # 修改此行代码

        # 调用 generate_daily_report 方法
        report, report_file_path = self.report_generator.generate_daily_report(self.test_markdown_file_path)

        # 验证返回值是否正确
        self.assertEqual(report, mock_report)
        self.assertTrue(report_file_path.endswith("_report.md"))

        # 验证生成的报告文件内容是否正确
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, mock_report)

        # 验证 LLM 的 generate_report 方法是否被正确调用，且传入了正确的参数
        self.mock_llm.generate_report.assert_called_once_with("github", self.markdown_content)

if __name__ == '__main__':
    unittest.main()
