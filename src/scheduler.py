# src/scheduler.py

import time  # 导入time库，用于控制操作间隔

class Scheduler:
    def __init__(self, github_client, notifier, report_generator, subscription_manager, interval=86400):
        # 初始化调度器，设置必要的属性
        self.github_client = github_client  # GitHub客户端实例，用于与GitHub交互
        self.notifier = notifier  # 通知器实例，用于发送通知
        self.report_generator = report_generator  # 报告生成器实例，用于生成报告
        self.subscription_manager = subscription_manager  # 订阅管理器实例，用于管理订阅
        self.interval = interval  # 调度间隔，默认为一天（86400秒）

    def start(self):
        # 启动调度器
        self.run()

    def run(self):
        # 运行调度器
        while True:
            subscriptions = self.subscription_manager.list_subscriptions()  # 获取当前所有订阅
            for repo in subscriptions:
                # 遍历每个订阅的仓库，执行以下操作
                updates = self.github_client.export_daily_progress(repo)  # 从GitHub客户端获取每日进展数据
                markdown_file_path = self.report_generator.export_daily_progress(repo, updates)  # 将进展数据导出为Markdown文件
                self.report_generator.generate_daily_report(markdown_file_path)  # 从Markdown文件生成日报
            time.sleep(self.interval)  # 完成一轮操作后，休眠设定的间隔时间
