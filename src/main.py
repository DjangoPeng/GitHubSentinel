# src/main.py

import argparse
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

    parser = argparse.ArgumentParser(description='GitHub Sentinel Command Line Interface')
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    parser_add = subparsers.add_parser('add', help='Add a subscription')
    parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
    parser_add.set_defaults(func=lambda args: command_handler.add_subscription(args))

    parser_remove = subparsers.add_parser('remove', help='Remove a subscription')
    parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
    parser_remove.set_defaults(func=lambda args: command_handler.remove_subscription(args))

    parser_list = subparsers.add_parser('list', help='List all subscriptions')
    parser_list.set_defaults(func=lambda args: command_handler.list_subscriptions())

    parser_fetch = subparsers.add_parser('fetch', help='Fetch updates immediately')
    parser_fetch.set_defaults(func=lambda args: command_handler.fetch_updates())

    parser_export = subparsers.add_parser('export', help='Export daily progress')
    parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
    parser_export.set_defaults(func=lambda args: command_handler.export_daily_progress(args))

    parser_generate = subparsers.add_parser('generate', help='Generate daily report from markdown file')
    parser_generate.add_argument('file', type=str, help='The markdown file to generate report from')
    parser_generate.set_defaults(func=lambda args: command_handler.generate_daily_report(args))

    parser_help = subparsers.add_parser('help', help='Show help message')
    parser_help.set_defaults(func=lambda args: command_handler.print_help())

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
