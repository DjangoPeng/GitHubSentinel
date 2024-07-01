import time
import threading

class Scheduler:
    def __init__(self, github_client, notifier, report_generator, subscription_manager, interval):
        self.github_client = github_client
        self.notifier = notifier
        self.report_generator = report_generator
        self.subscription_manager = subscription_manager
        self.interval = interval
    
    def start(self):
        while True:
            self.run()
            time.sleep(self.interval)
    
    def run(self):
        subscriptions = self.subscription_manager.get_subscriptions()
        updates = self.github_client.fetch_updates(subscriptions)
        report = self.report_generator.generate(updates)
        self.notifier.notify(report)
