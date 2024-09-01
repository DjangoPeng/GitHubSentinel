import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# 将 src 目录添加到模块搜索路径，方便导入项目中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import Config  # 导入配置类
from notifier import Notifier  # 导入要测试的 Notifier 类
from logger import LOG  # 导入日志记录器

class TestNotifier(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法之前运行，初始化 Notifier 实例和测试数据，并设置日志捕获。
        """
        self.config = Config()
        self.notifier = Notifier(self.config.email)
        self.test_repo = "DjangoPeng/openai-quickstart"
        self.test_github_report = """
        # DjangoPeng/openai-quickstart 项目进展

        ## 时间周期：2024-08-24

        ## 新增功能
        - Assistants API 代码与文档

        ## 主要改进
        - 适配 LangChain 新版本

        ## 修复问题
        - 关闭了一些未解决的问题。
        """
        self.test_hn_report = """
        # Hacker News 前沿技术趋势 (2024-09-01)

        ## Top 1：硬盘驱动器的讨论引发热门讨论
        """

        # 设置日志捕获
        self.log_capture = StringIO()
        self.capture_id = LOG.add(self.log_capture, level="INFO")

    def tearDown(self):
        """
        在每个测试方法之后运行，移除日志捕获。
        """
        LOG.remove(self.capture_id)
        self.log_capture.close()

    @patch('smtplib.SMTP_SSL')
    def test_notify_github_report_success(self, mock_smtp):
        """
        测试在邮件配置正确的情况下，GitHub 报告邮件是否成功发送，并检查日志输出。
        """
        # 执行邮件发送
        self.notifier.notify_github_report(self.test_repo, self.test_github_report)

        # 获取并检查日志内容
        log_content = self.log_capture.getvalue()
        self.assertIn("邮件发送成功！", log_content)

    @patch('smtplib.SMTP_SSL')
    def test_notify_hn_report_success(self, mock_smtp):
        """
        测试在邮件配置正确的情况下，Hacker News 报告邮件是否成功发送，并检查日志输出。
        """
        # 执行邮件发送
        self.notifier.notify_hn_report("2024-09-01", self.test_hn_report)

        # 获取并检查日志内容
        log_content = self.log_capture.getvalue()
        self.assertIn("邮件发送成功！", log_content)

    def test_notify_without_email_settings(self):
        """
        测试当邮件设置未正确配置时，Notifier 是否不会发送邮件并记录相应的警告日志。
        """
        faulty_notifier = Notifier(None)
        faulty_notifier.notify_github_report(self.test_repo, self.test_github_report)

        log_content = self.log_capture.getvalue()
        self.assertIn("邮件设置未配置正确", log_content)


if __name__ == '__main__':
    unittest.main()
