import sys
import os
import unittest
import json
from unittest.mock import patch, mock_open, call

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from subscription_manager import SubscriptionManager  # 导入要测试的 SubscriptionManager 类

class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        # 在每个测试之前设置测试所需的数据
        self.subscriptions_file = 'test_subscriptions.json'  # 测试用的订阅文件名
        self.initial_data = ["DjangoPeng/openai-quickstart", "some/repo"]  # 测试用的初始订阅数据

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["DjangoPeng/openai-quickstart", "some/repo"]))
    def test_save_subscriptions(self, mock_file):
        """
        测试 save_subscriptions 方法是否正确保存订阅数据到文件。
        """
        # 创建 SubscriptionManager 实例，并设置初始数据
        manager = SubscriptionManager(self.subscriptions_file)
        manager.subscriptions = self.initial_data
        manager.save_subscriptions()
        
        # 验证 open 函数是否被调用，分别用于读取和写入文件
        mock_file.assert_any_call(self.subscriptions_file, 'r')  # 检查读取操作
        mock_file.assert_any_call(self.subscriptions_file, 'w')  # 检查写入操作

        # 提取写入的字符串内容，并验证写入内容是否正确
        written_data = ''.join([call_arg.args[0] for call_arg in mock_file().write.call_args_list])
        self.assertEqual(json.loads(written_data), self.initial_data)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["DjangoPeng/openai-quickstart", "some/repo"]))
    def test_load_subscriptions(self, mock_file):
        """
        测试 load_subscriptions 方法是否正确从文件加载订阅数据。
        """
        # 创建 SubscriptionManager 实例，并加载订阅数据
        manager = SubscriptionManager(self.subscriptions_file)
        
        # 验证加载的订阅数据是否与预期一致
        self.assertEqual(manager.subscriptions, self.initial_data)
        
        # 验证 open 函数是否正确调用以读取文件
        mock_file.assert_called_once_with(self.subscriptions_file, 'r')

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["DjangoPeng/openai-quickstart"]))
    def test_list_subscriptions(self, mock_file):
        """
        测试 list_subscriptions 方法是否正确返回当前订阅列表。
        """
        # 创建 SubscriptionManager 实例，并列出当前的订阅
        manager = SubscriptionManager(self.subscriptions_file)
        subscriptions = manager.list_subscriptions()
        
        # 验证返回的订阅列表是否正确
        self.assertEqual(subscriptions, ["DjangoPeng/openai-quickstart"])
        
        # 验证 open 函数是否正确调用以读取文件
        mock_file.assert_called_once_with(self.subscriptions_file, 'r')

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["DjangoPeng/openai-quickstart"]))
    def test_add_subscription(self, mock_file):
        """
        测试 add_subscription 方法是否正确添加新的订阅，并保存到文件。
        """
        # 创建 SubscriptionManager 实例，并添加新的订阅
        manager = SubscriptionManager(self.subscriptions_file)
        manager.add_subscription("new/repo")
        
        # 验证新的订阅是否正确添加到订阅列表中
        self.assertIn("new/repo", manager.subscriptions)
        
        # 验证 open 函数是否正确调用以写入文件
        mock_file.assert_called_with(self.subscriptions_file, 'w')
        
        # 提取写入的字符串内容，并验证写入的内容是否正确
        written_data = ''.join([call_arg.args[0] for call_arg in mock_file().write.call_args_list])
        self.assertEqual(json.loads(written_data), ["DjangoPeng/openai-quickstart", "new/repo"])

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps(["DjangoPeng/openai-quickstart", "some/repo"]))
    def test_remove_subscription(self, mock_file):
        """
        测试 remove_subscription 方法是否正确移除订阅，并保存到文件。
        """
        # 创建 SubscriptionManager 实例，并移除指定的订阅
        manager = SubscriptionManager(self.subscriptions_file)
        manager.remove_subscription("some/repo")
        
        # 验证订阅列表中是否已移除指定的订阅
        self.assertNotIn("some/repo", manager.subscriptions)
        
        # 验证 open 函数是否正确调用以写入文件
        mock_file.assert_called_with(self.subscriptions_file, 'w')
        
        # 提取写入的字符串内容，并验证写入的内容是否正确
        written_data = ''.join([call_arg.args[0] for call_arg in mock_file().write.call_args_list])
        self.assertEqual(json.loads(written_data), ["DjangoPeng/openai-quickstart"])

if __name__ == '__main__':
    unittest.main()
