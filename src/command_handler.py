# src/command_handler.py

import shlex
from github_client import GitHubClient
from report_generator import ReportGenerator
from subscription_manager import SubscriptionManager

class CommandHandler:
    def __init__(self, github_client, subscription_manager, report_generator):
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator

    def add_subscription(self, args):
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription: {args.repo}")

    def remove_subscription(self, args):
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription: {args.repo}")

    def list_subscriptions(self):
        subscriptions = self.subscription_manager.get_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"- {sub}")

    def fetch_updates(self):
        subscriptions = self.subscription_manager.get_subscriptions()
        updates = self.github_client.fetch_updates(subscriptions)
        report = self.report_generator.generate(updates)
        print("Updates fetched:")
        print(report)

    def export_daily_progress(self, args):
        self.github_client.export_daily_progress(args.repo)

    def generate_daily_report(self, args):
        self.report_generator.generate_daily_report(args.file)

    def print_help(self):
        help_text = """
GitHub Sentinel Command Line Interface

Available commands:
  add <repo>       Add a subscription (e.g., owner/repo)
  remove <repo>    Remove a subscription (e.g., owner/repo)
  list             List all subscriptions
  fetch            Fetch updates immediately
  export           Export daily progress (e.g., export <repo>)
  generate         Generate daily report from markdown file (e.g., generate <file>)
  help             Show this help message
  exit             Exit the tool
  quit             Exit the tool
"""
        print(help_text)
