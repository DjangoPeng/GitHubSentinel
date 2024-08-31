import sys
import os
import unittest
from io import StringIO

# 将 src 目录添加到模块搜索路径，方便导入项目中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import Config  # 导入配置类
from notifier import Notifier  # 导入要测试的 Notifier 类
from logger import LOG  # 导入日志记录器

class TestNotifier(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法运行前执行，初始化 Notifier 实例和测试数据。
        """
        self.config = Config()  # 初始化配置对象
        self.notifier = Notifier(self.config.email)  # 使用配置中的邮箱信息初始化 Notifier 实例

        # 设置测试用的仓库名称
        self.test_repo = "DjangoPeng/openai-quickstart"

        # 准备用于测试的报告内容
        self.test_report = """
        # DjangoPeng/openai-quickstart 项目进展

        ## 时间周期：2024-08-24

        ## 新增功能
        - Assistants API 代码与文档

        ## 主要改进
        - 适配 LangChain 新版本

        ## 修复问题
        - 关闭了一些未解决的问题。
        """

    def test_notify_without_email_settings(self):
        """
        测试当邮件设置未正确配置时，Notifier 是否不会发送邮件并记录相应的警告日志。
        """
        # 创建一个用于捕获日志的 StringIO 对象
        log_capture = StringIO()
        # 添加日志捕获器，级别设为 WARNING，并获取其 ID
        capture_id = LOG.add(log_capture, level="WARNING")

        # 初始化一个邮件配置为空的 Notifier 实例
        faulty_notifier = Notifier(None)
        # 调用 notify 方法尝试发送通知
        faulty_notifier.notify(self.test_repo, self.test_report)

        # 获取捕获的日志内容
        log_content = log_capture.getvalue()
        # 移除刚才添加的日志捕获器
        LOG.remove(capture_id)

        # 断言日志内容中包含预期的警告信息
        self.assertIn("邮件设置未配置正确", log_content)

    def test_send_email_success(self):
        """
        测试在邮件配置正确的情况下，Notifier 是否能够成功发送邮件。
        """
        try:
            # 调用 notify 方法发送通知
            self.notifier.notify(self.test_repo, self.test_report)
            # 如果发送成功，记录一条信息日志
            LOG.info("邮件发送成功")
        except Exception as e:
            # 如果发送过程中出现异常，测试失败并输出异常信息
            self.fail(f"发送邮件时发生异常: {e}")

if __name__ == '__main__':
    unittest.main()
