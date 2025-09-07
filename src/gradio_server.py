"""Gradio 前端展示层

仅调整界面布局；不改动任何业务逻辑 / 函数签名。
由早期的 `gr.Interface` 自动触发模式改为 `gr.Blocks` + 手动“生成报告”按钮，提高可控性。

当前布局结构（上下分区）：
┌──────────────────────────────────────────────────────────────┐
│ 顶部标题 & 说明                                               │
├──────────────────────────────────────────────────────────────┤
│ 输入区域（单行）                                             │
│  ├─ 下拉：订阅列表                                            │
│  ├─ 滑块：报告周期 (天)                                      │
│  └─ 按钮：🚀 生成报告                                         │
├──────────────────────────────────────────────────────────────┤
│ 输出区域（左右两列）                                         │
│  ├─ 左列：Markdown 报告预览                                  │
│  └─ 右列：报告文件下载 (File)                                │
├──────────────────────────────────────────────────────────────┤
│ 底部版权信息                                                 │
└──────────────────────────────────────────────────────────────┘

交互方式：用户选择参数后点击按钮触发生成，不再随输入即时刷新。
"""

import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# -------------------- 依赖实例化（保持不变） -------------------- #
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def export_progress_by_date_range(repo, days):
    """导出并生成指定时间范围内项目进展报告（业务逻辑保持不变）。"""
    try:
        raw_file_path = github_client.export_progress_by_date_range(repo, days)
        report, report_file_path = report_generator.generate_report_by_date_range(
            raw_file_path, days
        )
        return report, report_file_path
    except Exception as e:
        LOG.error("生成报告失败: {}", e)
        friendly = (
            f"❌ 生成失败：{type(e).__name__}\n\n"
            "可能原因：\n"
            "- LLM 接口超时或限流\n"
            "- OPENAI_API_KEY 未配置或失效\n"
            "- 网络访问受限\n"
            "请稍后重试或检查配置。"
        )
        # 返回占位文本，以及 None（Gradio File 允许为空）
        return friendly, None


# -------------------- 界面布局（仅 UI 调整） -------------------- #
with gr.Blocks(title="GitHubSentinel", theme=gr.themes.Soft()) as demo:
    # 顶部标题说明
    gr.Markdown(
        """
        # 🔍 GitHubSentinel
        **自动化获取并汇总 GitHub 项目在指定时间范围内的进展。**
        选择一个仓库与报告周期，系统会自动导出数据并生成结构化报告。
        """
    )

    # 上方：输入区域（整行）
    with gr.Group():
        with gr.Row():
            repo_input = gr.Dropdown(
                subscription_manager.list_subscriptions(),
                label="订阅列表",
                info="选择需要生成进展报告的 GitHub 仓库",
                scale=3,
            )
            days_input = gr.Slider(
                value=2,
                minimum=1,
                maximum=7,
                step=1,
                label="报告周期 (天)",
                info="统计过去 N 天内的提交 / issue / PR 等动态",
                scale=2,
            )
            generate_btn = gr.Button("🚀 生成报告", variant="primary", scale=1)
        gr.Markdown(
            """
            *提示*: 选择参数后点击“生成报告”按钮。若生成结果为空，可能是该周期无活动。
            """
        )

    # 下方：输出区域（报告 + 文件并列显示）
    gr.Markdown("### 📄 报告输出")
    with gr.Row(equal_height=False):
        with gr.Column(scale=7):
            report_md = gr.Markdown(
                value="_请选择仓库并设置周期以生成报告_", elem_id="report_markdown"
            )
        with gr.Column(scale=5):
            gr.Markdown("**下载生成的报告文件**")
            report_file = gr.File(label="报告文件", file_count="single")

    # 点击按钮触发生成
    generate_btn.click(
        fn=export_progress_by_date_range,
        inputs=[repo_input, days_input],
        outputs=[report_md, report_file],
    )

    # 底部版权
    gr.Markdown(
        """
        ---
        © 2025 GitHubSentinel  |  本界面仅做数据呈现，不存储任何私有代码内容。
        """
    )


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # 可选：带认证方式（保留注释，不改动逻辑）
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
