# Standard Library Imports
import json
import os
import re
import traceback

# Third-Party Imports
import streamlit as st

# Project-Specific Imports
try:
    from src.report_generator import ReportGenerator
    from src.config import Settings
    from src.llm import LLM # Added import
    from src.github_client import GitHubClient # Added import
except ImportError as e:
    # This is a critical error, so display it prominently and stop the app.
    st.error(f"核心模块导入失败: {e}。应用无法启动。\n请检查项目结构和依赖项。")
    st.stop()

# --- Constants ---
CONFIG_PATH = "config.json"
SUBSCRIPTIONS_PATH = "subscriptions.json"
APP_VERSION = "0.1.1" # Example version

# --- App Configuration ---
st.set_page_config(
    page_title="GitHub Sentinel Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

def show_message(message_type: str, text: str):
    """Displays a message using Streamlit's alert components with icons."""
    if message_type == "success":
        st.success(f"✅ {text}")
    elif message_type == "error":
        st.error(f"❌ {text}")
    elif message_type == "warning":
        st.warning(f"⚠️ {text}")
    elif message_type == "info":
        st.info(f"ℹ️ {text}")
    else:
        st.write(text) # Default to st.write if type is unknown

def load_json_file(file_path: str) -> dict | None:
    """Loads a JSON file with error handling."""
    try:
        if not os.path.exists(file_path):
            if file_path == CONFIG_PATH:
                show_message("error", f"关键配置文件 {file_path} 未找到。应用无法运行。")
                st.stop()
            show_message("warning", f"文件 {file_path} 未找到。将使用默认/空数据结构。")
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError: # Should be caught by os.path.exists
        if file_path == CONFIG_PATH: # Should not happen due to check above
            show_message("error", f"关键配置文件 {file_path} 未找到。应用无法运行。")
            st.stop()
        show_message("error", f"文件 {file_path} 未找到。")
        return None
    except json.JSONDecodeError:
        show_message("error", f"解析文件 {file_path} 失败。请检查JSON格式。")
        return None
    except Exception as e: # Catch any other unexpected errors during file loading
        show_message("error", f"加载文件 {file_path} 时发生未知错误: {e}")
        if file_path == CONFIG_PATH:
            st.stop()
        return None


def save_json_file(file_path: str, data: dict) -> bool:
    """Saves data to a JSON file with error handling."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        show_message("error", f"无法写入到文件 {file_path}。详情: {e}")
        return False
    except Exception as e:
        show_message("error", f"保存文件 {file_path} 时发生未知错误: {e}")
        return False


def normalize_repo_input(repo_input: str) -> str | None:
    """
    Normalizes GitHub repository input (URL or 'owner/repo') to 'owner/repo' format.
    Returns None if input is invalid.
    """
    repo_input = repo_input.strip()
    # Regex for owner/repo from various GitHub URL formats or direct input
    # Handles: https://github.com/owner/repo, http://github.com/owner/repo, github.com/owner/repo, owner/repo, owner/repo.git
    match = re.match(r"^(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)(?:\.git)?\/?$", repo_input)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    # Simpler owner/repo match if not a URL
    match_simple = re.match(r"^([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)$", repo_input)
    if match_simple:
        return f"{match_simple.group(1)}/{match_simple.group(2)}"
    return None

def build_github_url(owner_repo_str: str) -> str:
    """Constructs a full GitHub URL from an 'owner/repo' string."""
    return f"https://github.com/{owner_repo_str}"


# --- Subscription Management ---

def get_subscriptions() -> dict:
    """Retrieves and prepares subscription data."""
    data = load_json_file(SUBSCRIPTIONS_PATH)
    if data is None:
        return {"github_subscriptions": [], "hacker_news_subscriptions": []} # Return default structure

    # Ensure top-level keys exist
    data.setdefault("github_subscriptions", [])
    data.setdefault("hacker_news_subscriptions", [])

    # Migrate old string-based GitHub subscriptions to new dict format
    migrated_subs = []
    needs_save = False
    for sub in data.get("github_subscriptions", []): # Use .get for safety
        if isinstance(sub, str): # Old format: "owner/repo"
            migrated_subs.append({"repo_url": sub, "last_processed_timestamp": None, "custom_branch": None})
            needs_save = True
        elif isinstance(sub, dict) and "repo_url" in sub: # New format
            sub.setdefault("last_processed_timestamp", None) # Ensure all keys exist
            sub.setdefault("custom_branch", None)
            migrated_subs.append(sub)
        # Else: unknown format, skip or log

    if needs_save:
        data["github_subscriptions"] = migrated_subs
        if save_json_file(SUBSCRIPTIONS_PATH, data): # Use the new save_json_file
            show_message("info", "旧版订阅格式已自动更新为新版。")
        else:
            show_message("error", "自动迁移旧版订阅格式失败。更改未保存。")
            # Potentially return original data or handle error more gracefully
    else:
        data["github_subscriptions"] = migrated_subs # Ensure list is what we processed

    return data


def display_subscription_management():
    """UI for managing GitHub repository subscriptions."""
    st.header("🔧 GitHub 仓库订阅管理")

    # Initialize session state for removal logic if not present
    if "repo_to_remove" not in st.session_state:
        st.session_state.repo_to_remove = None

    subscriptions_data = get_subscriptions()
    github_subs_list = subscriptions_data.get("github_subscriptions", [])

    st.subheader("➕ 添加新订阅")
    new_repo_input = st.text_input(
        "输入 GitHub 仓库 (例如 'owner/repo' 或完整 URL):",
        key="new_repo_text_input_sub_mgmt", # More specific key
        help="输入仓库的 owner/repo 格式或完整的 GitHub URL。"
    )

    if st.button("添加订阅", key="add_sub_button", help="点击以添加此仓库到订阅列表。"):
        if new_repo_input:
            normalized_repo_url = normalize_repo_input(new_repo_input)
            if not normalized_repo_url:
                 show_message("error", "输入格式不正确。请使用 'owner/repo' 或完整的 GitHub URL。")
            elif any(sub.get("repo_url") == normalized_repo_url for sub in github_subs_list):
                show_message("warning", f"仓库 {normalized_repo_url} 已经订阅过了。")
            else:
                new_sub_entry = {"repo_url": normalized_repo_url, "last_processed_timestamp": None, "custom_branch": None}
                github_subs_list.append(new_sub_entry)
                # subscriptions_data["github_subscriptions"] should point to github_subs_list
                if save_json_file(SUBSCRIPTIONS_PATH, subscriptions_data):
                    show_message("success", f"成功添加订阅: {normalized_repo_url}")
                    st.rerun()
                else:
                    github_subs_list.pop() # Revert addition if save failed
        else:
            show_message("warning", "请输入仓库信息。")

    st.markdown("---")
    st.subheader("📜 当前已订阅的仓库")
    if not github_subs_list:
        show_message("info", "目前没有订阅任何 GitHub 仓库。")
    else:
        for idx, repo_entry in enumerate(github_subs_list):
            repo_url_normalized = repo_entry.get("repo_url")
            if not repo_url_normalized: continue

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"- [{repo_url_normalized}]({build_github_url(repo_url_normalized)})")
            with col2:
                # Unique key for each button, using normalized URL and index
                button_key = f"remove_sub_{repo_url_normalized.replace('/', '_')}_{idx}"
                if st.button("➖ 移除", key=button_key, help=f"移除 {repo_url_normalized} 订阅"):
                    st.session_state.repo_to_remove = repo_url_normalized

        # Process removal outside the loop, based on session state
        if st.session_state.repo_to_remove:
            repo_to_remove_url = st.session_state.repo_to_remove
            current_subs = get_subscriptions() # Re-fetch to ensure we have the latest before modifying
            updated_github_subs = [sub for sub in current_subs.get("github_subscriptions", []) if sub.get("repo_url") != repo_to_remove_url]

            if len(updated_github_subs) < len(current_subs.get("github_subscriptions", [])):
                current_subs["github_subscriptions"] = updated_github_subs
                if save_json_file(SUBSCRIPTIONS_PATH, current_subs):
                    show_message("success", f"成功移除仓库: {repo_to_remove_url}")
                else:
                    show_message("error", f"移除仓库 {repo_to_remove_url} 失败。更改未保存。")
            st.session_state.repo_to_remove = None # Reset after processing
            st.rerun()


# --- Report Generation UI ---
def display_report_generation_ui():
    """UI for generating various types of reports."""
    st.header("📊 生成报告")

    # Initialize session state for report content if not present
    if "generated_report_content" not in st.session_state:
        st.session_state.generated_report_content = None

    config_data = load_json_file(CONFIG_PATH)
    if not config_data: return

    available_report_types = config_data.get("report_types", [])
    if not available_report_types:
        show_message("warning", "配置文件中未定义任何报告类型 (`report_types`)。")
        return

    report_type = st.selectbox(
        "选择报告类型:", available_report_types, key="report_type_select",
        help="选择您希望生成的报告种类。"
    )

    # --- Report specific options ---
    generate_report_button = False
    target_repo_input = None # For single GitHub repo
    github_report_scope = "all" # Default for GitHub

    if report_type == "github":
        github_report_scope_options = ["所有已订阅仓库", "指定单个仓库"]
        github_report_scope_selection = st.radio(
            "选择GitHub报告范围:", github_report_scope_options, key="gh_scope_radio",
            help="选择是为所有已订阅的仓库生成报告，还是为单个特定仓库生成。"
        )

        if github_report_scope_selection == "指定单个仓库":
            github_report_scope = "single"
            current_subscriptions = get_subscriptions()
            subscribed_repo_urls = [
                sub.get("repo_url") for sub in current_subscriptions.get("github_subscriptions", [])
                if isinstance(sub, dict) and sub.get("repo_url")
            ]
            repo_options = [""] + sorted(list(set(subscribed_repo_urls))) # Ensure unique and sorted

            col_manual, col_select = st.columns(2)
            with col_manual:
                target_repo_manual_input = st.text_input(
                    "手动输入 owner/repo:", key="gh_single_repo_manual_text", # Specific key
                    help="如果仓库未订阅或想手动指定。"
                )
            with col_select:
                target_repo_select = st.selectbox(
                    "或从已订阅仓库中选择:", repo_options, index=0,
                    key="gh_single_repo_select_box", # Specific key
                    help="从已订阅仓库列表中选择。"
                )

            if target_repo_manual_input:
                normalized_manual_input = normalize_repo_input(target_repo_manual_input)
                if normalized_manual_input:
                    target_repo_input = normalized_manual_input
                else:
                    show_message("error", "手动输入的仓库格式不正确。请使用 'owner/repo'。")
            elif target_repo_select:
                target_repo_input = target_repo_select

            if target_repo_input:
                generate_report_button = st.button(f"为 {target_repo_input} 生成GitHub报告", key="generate_single_gh_report_btn")
            else:
                show_message("info", "请为 '指定单个仓库' 提供一个仓库（手动输入或从列表选择）。")
        else: # "所有已订阅仓库"
            github_report_scope = "all"
            generate_report_button = st.button("为所有已订阅仓库生成GitHub报告", key="generate_all_gh_report_btn")

    elif report_type == "hacker_news_hours_topic":
        generate_report_button = st.button("生成Hacker News小时热门话题报告", key="generate_hn_hours_topic_btn")
    elif report_type == "hacker_news_daily_report":
        generate_report_button = st.button("生成Hacker News每日摘要报告", key="generate_hn_daily_report_btn")
    else:
        show_message("warning", f"暂不支持 '{report_type}' 类型的报告生成UI。")

    # --- Report Generation Logic ---
    if generate_report_button:
        try:
            settings = Settings(config_file=CONFIG_PATH)

            # Instantiate LLM
            # Assumes LLM constructor takes settings or handles its own config.
            # If LLM is not needed for all report types, this could be conditional.
            llm_instance = LLM(settings=settings)

            # Instantiate GitHubClient - required for GitHub related reports
            # Token should be fetched securely, e.g., via settings that loads from config_data or env
            # Using config_data as it's already loaded in this function's scope.
            github_token = config_data.get("github", {}).get("token")

            # For non-GitHub reports, github_client might not be strictly needed by ReportGenerator
            # depending on its internal logic. However, the current ReportGenerator __init__ expects it.
            if not github_token and report_type == "github": # Only critical if a github report is being generated
                show_message("error", "GitHub token 未在配置中找到，无法生成GitHub相关报告。")
                st.session_state.generated_report_content = "错误: GitHub token 未配置。"
                # Return to prevent further processing for GitHub reports without a token
                # For other report types, this might not be a fatal error for ReportGenerator initialization.
                # However, if ReportGenerator constructor *always* needs a functional github_client,
                # then this check should be more stringent or github_client should handle a None token gracefully.
                # For now, let's allow init but GitHub functions within RG will fail.
                # A better approach might be to conditionally pass github_client=None if not a github report,
                # but that depends on ReportGenerator's __init__ allowing it.
                # Sticking to current RG signature:
            github_client_instance = GitHubClient(token=github_token if github_token else "dummy_token_if_not_github_report") # Pass a dummy if not essential for other types

            # Correctly instantiate ReportGenerator
            report_generator = ReportGenerator(llm=llm_instance, settings=settings, github_client=github_client_instance)

        except Exception as e: # Catch errors during Settings, LLM, GitHubClient, or ReportGenerator initialization
            show_message("error", f"初始化报告所需组件失败: {e}")
            st.code(traceback.format_exc())
            st.session_state.generated_report_content = f"初始化报告生成器失败: {e}"
            return # Stop if core components fail

        report_content = None
        with st.spinner("⏳ 正在生成报告中，请稍候..."):
            try:
                if report_type == "github":
                    if github_report_scope == "all":
                        report_content = report_generator.generate_github_subscription_report()
                    elif github_report_scope == "single" and target_repo_input:
                        owner, repo_name = target_repo_input.split('/')
                        report_content = report_generator.generate_github_project_report(
                            repo_url=build_github_url(target_repo_input), owner=owner, repo_name=repo_name
                        ) # Assuming other params like days, branch are handled by ReportGenerator or Settings
                elif report_type == "hacker_news_hours_topic":
                    report_content = report_generator.generate_hacker_news_hours_topic_report()
                elif report_type == "hacker_news_daily_report":
                    report_content = report_generator.generate_hacker_news_daily_report()

                if report_content: # Successfully generated content
                    st.session_state.generated_report_content = report_content
                    show_message("success", "报告生成成功！")
                else: # No content generated, but no error (e.g., no new PRs for a repo)
                    msg = "未能生成报告内容，或报告为空（例如，没有符合条件的数据）。"
                    st.session_state.generated_report_content = msg # Store this info
                    show_message("info", msg)
            except Exception as e:
                error_msg = f"生成报告时发生错误: {str(e)}"
                # Store full traceback for display in markdown
                st.session_state.generated_report_content = f"{error_msg}\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                show_message("error", error_msg)
                # Optionally, display traceback directly in an expander or code block if preferred
                # st.code(traceback.format_exc())

    st.markdown("---")
    if st.session_state.generated_report_content:
        st.subheader("📄 生成的报告:")
        st.markdown(st.session_state.generated_report_content, unsafe_allow_html=True)
        if st.button("清除报告显示", key="clear_report_display_btn", help="点击以清除当前显示的报告内容。"):
            st.session_state.generated_report_content = None
            st.rerun()


# --- Config Overview UI ---
def _display_config_detail_item(label: str, value, is_sensitive: bool = False):
    """Internal helper to display a single config item."""
    display_value = "••••••••" if is_sensitive and value else str(value)
    st.markdown(f"**{label}:** `{display_value}`")

def display_config_overview():
    """UI for displaying application configuration overview."""
    st.header("⚙️ 应用配置概览")
    config_data = load_json_file(CONFIG_PATH)
    if not config_data:
        show_message("error", "无法加载配置数据，配置概览不可用。")
        return

    with st.expander("GitHub 配置", expanded=True):
        github_cfg = config_data.get("github", {})
        if github_cfg:
            _display_config_detail_item("Token", github_cfg.get("token"), is_sensitive=True)
            _display_config_detail_item("订阅文件路径", github_cfg.get("subscriptions_file", SUBSCRIPTIONS_PATH))
            _display_config_detail_item("进度报告频率 (天)", github_cfg.get("progress_frequency_days", "N/A"))
            _display_config_detail_item("进度报告生成时间", github_cfg.get("progress_execution_time", "N/A"))
        else:
            show_message("info", "未配置 GitHub 相关信息。")

    with st.expander("邮件配置"):
        email_cfg = config_data.get("email", {})
        if email_cfg:
            _display_config_detail_item("SMTP 服务器", email_cfg.get("smtp_server", "N/A"))
            _display_config_detail_item("SMTP 端口", email_cfg.get("smtp_port", "N/A"))
            _display_config_detail_item("发件人", email_cfg.get("from", "N/A"))
            _display_config_detail_item("密码", email_cfg.get("password"), is_sensitive=True)
            to_emails = email_cfg.get('to', [])
            _display_config_detail_item("收件人", ", ".join(to_emails) if isinstance(to_emails, list) else str(to_emails))
        else:
            show_message("info", "未配置邮件相关信息。")

    with st.expander("LLM 配置"):
        llm_cfg = config_data.get("llm", {})
        if llm_cfg:
            _display_config_detail_item("模型类型", llm_cfg.get("model_type", "N/A"))
            _display_config_detail_item("OpenAI 模型名称", llm_cfg.get("openai_model_name", "N/A"))
            _display_config_detail_item("Ollama 模型名称", llm_cfg.get("ollama_model_name", "N/A"))
            _display_config_detail_item("Ollama API URL", llm_cfg.get("ollama_api_url", "N/A"))
        else:
            show_message("info", "未配置 LLM 相关信息。")

    with st.expander("报告类型"):
        report_types = config_data.get("report_types", [])
        if report_types:
            st.markdown("- " + "\n- ".join(report_types))
        else:
            show_message("info", "未配置报告类型。")

    with st.expander("Slack 配置"):
        slack_cfg = config_data.get("slack", {})
        if slack_cfg:
            _display_config_detail_item("Webhook URL", slack_cfg.get("webhook_url"), is_sensitive=True)
        else:
            show_message("info", "未配置 Slack 相关信息。")

    st.markdown("---")
    st.caption(f"提示: 配置文件 `{CONFIG_PATH}` 控制这些设置。敏感信息（如Token/密码）在此处部分隐藏。")
    # Theming info - kept from previous step
    st.markdown("""
    <details>
    <summary>点击查看自定义样式说明</summary>
    <p>您可以通过在项目根目录下创建 <code>.streamlit/config.toml</code> 文件来自定义应用主题和样式。</p>
    <p>例如，要设置暗色主题并更改主颜色，您的 <code>.streamlit/config.toml</code> 可能如下所示:</p>
    <pre><code>
[theme]
base="dark"
primaryColor="#1E88E5"
    </code></pre>
    <p>更多信息请查阅 <a href="https://docs.streamlit.io/library/advanced-features/theming" target="_blank">Streamlit 主题文档</a>。</p>
    </details>
    """, unsafe_allow_html=True)


def display_subscriptions_overview():
    """UI for displaying a summary of current subscriptions."""
    st.subheader("📚 当前订阅概览")
    subscriptions_data = get_subscriptions()
    if subscriptions_data:
        github_subs_count = len(subscriptions_data.get("github_subscriptions", []))
        st.metric(label="GitHub 仓库订阅数量", value=github_subs_count)
        # Future: Add counts for other subscription types (e.g., Hacker News)
    else:
        show_message("warning", "无法加载订阅信息以显示概览。")

# --- Main Application ---
def main():
    """Main function to run the Streamlit application."""
    st.title("智能信息助手 - GitHub Sentinel Dashboard")
    st.caption(f"欢迎使用 GitHub Sentinel！ ({APP_VERSION}) 选择左侧导航栏的功能开始探索。")

    # Sidebar Navigation
    st.sidebar.title("🧭 导航与控制")
    nav_options = ["配置概览", "订阅管理", "报告生成"]
    nav_icons = {"配置概览": "⚙️", "订阅管理": "🔧", "报告生成": "📊"}
    nav_display_options = [f"{nav_icons[opt]} {opt}" for opt in nav_options]
    nav_mapping = {display_opt: opt for display_opt, opt in zip(nav_display_options, nav_options)}

    displayed_selection = st.sidebar.radio(
        "选择功能:", nav_display_options, key="nav_main_radio_selector", label_visibility="collapsed"
    )
    nav_selection = nav_mapping[displayed_selection]

    st.sidebar.markdown("---")
    st.sidebar.info(f"**GitHub Sentinel**\n\n版本: {APP_VERSION}")

    # Main Content Area
    if nav_selection == "配置概览":
        display_config_overview()
        st.markdown("---") # Visual separator
        display_subscriptions_overview()
    elif nav_selection == "订阅管理":
        display_subscription_management()
    elif nav_selection == "报告生成":
        display_report_generation_ui()
    else:
        show_message("error", "无效的导航选项。") # Should not happen with radio buttons

if __name__ == "__main__":
    main()
