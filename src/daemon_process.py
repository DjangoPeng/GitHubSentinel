import daemon
import threading
import time


from config import Config
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from scheduler import Scheduler
from logger import LOG

def run_scheduler(scheduler):
    scheduler.start()

def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    
    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval
    )
    
    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    LOG.info("Scheduler thread started.")
    
    # Use python-daemon to properly daemonize the process
    with daemon.DaemonContext():
        try:
            while True:
                time.sleep(config.update_interval)
        except KeyboardInterrupt:
            LOG.info("Daemon process stopped.")

if __name__ == '__main__':
    main()

# nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
