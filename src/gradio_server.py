import gradio as gr

from config import Config
from github_client import GitHubClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG

config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def export_progress_by_date_range(repo, days):
    raw_file_path = github_client.export_progress_by_date_range(repo, days)
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)

    return report, report_file_path

demo = gr.Interface(
    fn=export_progress_by_date_range,
    title="GitHubSentinel",
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),

    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],
)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))