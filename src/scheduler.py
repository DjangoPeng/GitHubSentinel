# src/scheduler.py

import time

class Scheduler:
    def __init__(self, github_client, notifier, report_generator, subscription_manager, interval=86400):
        self.github_client = github_client
        self.notifier = notifier
        self.report_generator = report_generator
        self.subscription_manager = subscription_manager
        self.interval = interval

    def start(self):
        self.run()

    def run(self):
        while True:
            subscriptions = self.subscription_manager.list_subscriptions()
            for repo in subscriptions:
                updates = self.github_client.export_daily_progress(repo)
                markdown_file_path = self.report_generator.export_daily_progress(repo, updates)
                self.report_generator.generate_daily_report(markdown_file_path)
            time.sleep(self.interval)
