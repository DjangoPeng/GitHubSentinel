import daemon  # 导入daemon库，用于创建守护进程
import threading  # 导入threading库，用于多线程处理
import time  # 导入time库，用于控制时间间隔

from config import Config  # 导入配置管理类
from github_client import GitHubClient  # 导入GitHub客户端类，处理GitHub API请求
from notifier import Notifier  # 导入通知器类，用于发送通知
from report_generator import ReportGenerator  # 导入报告生成器类
from llm import LLM  # 导入语言模型类，可能用于生成报告内容
from subscription_manager import SubscriptionManager  # 导入订阅管理器类，管理GitHub仓库订阅
from scheduler import Scheduler  # 导入调度器类，用于定时执行任务
from logger import LOG  # 导入日志记录器

def run_scheduler(scheduler):
    # 启动调度器的函数，用于在线程中运行
    scheduler.start()

def main():
    config = Config()  # 创建配置实例
    github_client = GitHubClient(config.github_token)  # 创建GitHub客户端实例
    notifier = Notifier(config.notification_settings)  # 创建通知器实例
    llm = LLM()  # 创建语言模型实例
    report_generator = ReportGenerator(llm)  # 创建报告生成器实例
    subscription_manager = SubscriptionManager(config.subscriptions_file)  # 创建订阅管理器实例
    
    # 创建调度器实例，配置其参数
    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval  # 设置更新间隔
    )
    
    # 创建并启动调度器运行的线程
    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True  # 设置线程为守护线程
    scheduler_thread.start()  # 启动线程
    
    LOG.info("Scheduler thread started.")  # 记录调度器线程已启动
    
    # 使用python-daemon库，以守护进程方式运行程序
    with daemon.DaemonContext():
        try:
            while True:
                time.sleep(config.update_interval)  # 按配置的更新间隔休眠
        except KeyboardInterrupt:
            LOG.info("Daemon process stopped.")  # 在接收到中断信号时记录日志

if __name__ == '__main__':
    main()

# 启动方式：nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
