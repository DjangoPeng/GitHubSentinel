# src/main.py

import threading
import shlex
from config import Config
from scheduler import Scheduler
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from command_handler import CommandHandler
from parser import create_parser


def run_scheduler(scheduler):
    scheduler.start()


def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM(config.openai_api_key)
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    command_handler = CommandHandler(github_client, subscription_manager, report_generator)

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

    parser = create_parser(command_handler)

    while True:
        try:
            user_input = input("GitHub Sentinel> ")
            if user_input in ['exit', 'quit']:
                break
            args = parser.parse_args(shlex.split(user_input))
            if args.command is None:
                print("Invalid command. Type 'help' to see the list of available commands.")
                continue
            args.func(args)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    print("""
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
""")
    main()
