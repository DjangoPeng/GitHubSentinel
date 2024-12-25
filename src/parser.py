# src/parser.py

import argparse
from command_handler import CommandHandler

def create_parser(command_handler):
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

    return parser
