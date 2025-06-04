import os
from logger import LOG  # 导入日志模块
from datetime import datetime, timezone, timedelta # Added for release date handling

class ReportGenerator:
    # 1. Modified __init__ signature and assignments
    def __init__(self, llm, settings, github_client): # Added settings and github_client
        self.llm = llm
        self.settings = settings # Store settings instance
        self.github_client = github_client # Store github_client instance

        # Fully enable __init__ with settings
        self.report_types = self.settings.get_report_types()
        self.prompts = {}  # 存储所有预加载的提示信息
        self._preload_prompts() # Call to preload prompts

    def _preload_prompts(self):
        """
        Preloads prompt files based on report types from settings.
        """
        LOG.debug("Preloading prompts...")
        if not self.report_types:
            LOG.warning("No report types configured in settings. No prompts will be loaded.")
            return

        for report_type in self.report_types:
            prompt_filename_key = report_type
            # Construct prompt key, e.g., including LLM model name if relevant
            # This logic assumes self.llm might have a 'model' attribute.
            # Adjust if model identifier comes from settings or elsewhere.
            llm_model_name = getattr(self.llm, 'model', None) or getattr(self.llm, 'model_name', None)
            if llm_model_name:
                 prompt_filename_key = f"{report_type}_{llm_model_name}"

            # Use settings to get the full, validated path to the prompt file
            prompt_file_path = self.settings.get_prompt_file_path(prompt_filename_key)

            if not prompt_file_path or not os.path.exists(prompt_file_path):
                LOG.warning(f"Prompt file not configured or does not exist for key: '{prompt_filename_key}' (Expected Path: {prompt_file_path}). Skipping this prompt.")
                # Assign a default generic prompt or None
                # For critical prompts, this might be an error. For now, a generic default.
                self.prompts[report_type] = "Please summarize the following content:"
            else:
                try:
                    with open(prompt_file_path, "r", encoding='utf-8') as file:
                        self.prompts[report_type] = file.read()
                    LOG.debug(f"Successfully loaded prompt for '{prompt_filename_key}' from {prompt_file_path}")
                except Exception as e:
                    LOG.error(f"Error loading prompt file {prompt_file_path} for '{prompt_filename_key}': {e}")
                    self.prompts[report_type] = "Error loading prompt. Please summarize the following content:" # Fallback
        LOG.info(f"Prompts loaded for types: {list(self.prompts.keys())}")

    def _format_releases_markdown(self, releases: list) -> str:
        """
        Formats a list of release dictionaries into a Markdown string.
        """
        if not releases:
            return "### 🚀 近期 Releases:\n\n最近没有发现 Releases。\n"

        markdown_parts = ["### 🚀 近期 Releases:\n"]
        for release in releases:
            name = release.get("name", "N/A")
            tag_name = release.get("tag_name", "N/A")
            html_url = release.get("html_url", "#")
            author_login = release.get("author_login", "N/A")
            published_at_str = release.get("published_at", "N/A")
            body = release.get("body", "无 Release Notes。")

            try:
                # Format date like YYYY-MM-DD
                formatted_date = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            except ValueError:
                formatted_date = published_at_str # Keep original if parsing fails

            release_md = (
                f"*   **[{name}]({html_url})** (Tag: `{tag_name}`)\n"
                f"    *发布者: {author_login} 于 {formatted_date}*\n"
            )
            if body and body.strip(): # Only add details if body is not empty
                release_md += (
                    f"    <details>\n"
                    f"    <summary>查看 Release Notes</summary>\n\n"
                    f"    {body.strip()}\n\n"
                    f"    </details>\n"
                )
            release_md += "---\n" # Separator for readability
            markdown_parts.append(release_md)
        
        return "\n".join(markdown_parts)

    def _generate_github_project_basic_info_markdown(self, owner: str, repo_name: str, days: int) -> str:
        """
        Fetches and formats basic project info (issues, PRs, commits, releases) into Markdown.
        This is the content that might be passed to an LLM or used directly.
        """
        repo_full_name = f"{owner}/{repo_name}"
        # Ensure 'since_date' is ISO format string for GitHub API
        since_date_dt = datetime.now(timezone.utc) - timedelta(days=days)
        since_date_iso = since_date_dt.isoformat()

        LOG.debug(f"Fetching updates for {repo_full_name} since {since_date_iso} ({days} days)")

        # It's crucial that github_client methods return lists of dicts with expected keys
        commits = self.github_client.fetch_commits(repo_full_name, since=since_date_iso)
        issues = self.github_client.fetch_issues(repo_full_name, since=since_date_iso)
        pull_requests = self.github_client.fetch_pull_requests(repo_full_name, since=since_date_iso)
        recent_releases = self.github_client.get_recent_releases(owner, repo_name, days_limit=days)

        content_parts = [f"## {repo_full_name} 项目更新 (过去 {days} 天)\n"]

        content_parts.append("### 📝 Commits:\n")
        if commits:
            for commit in commits[:10]: # Display top 10 commits
                commit_sha = commit.get('sha', '')[:7]
                commit_msg = commit.get('commit', {}).get('message', 'No commit message').splitlines()[0]
                author_login = commit.get('author', {}).get('login', 'N/A')
                commit_url = commit.get('html_url', '#')
                content_parts.append(f"- [`{commit_sha}`]({commit_url}) {commit_msg} (by {author_login})")
        else:
            content_parts.append("最近 {days} 天内没有 Commits。\n")

        content_parts.append("\n### 🛠 Issues (Closed):\n")
        if issues:
            for issue in issues[:10]: # Display top 10 issues
                issue_number = issue.get('number')
                issue_title = issue.get('title', 'N/A')
                issue_url = issue.get('html_url', '#')
                closed_by = issue.get('user', {}).get('login', 'N/A') # User who closed or was assigned? API might vary.
                                                                    # For 'closed' issues, 'user' is often the creator.
                                                                    # If using events, actor would be clearer.
                                                                    # For now, assume 'user' is relevant.
                content_parts.append(f"- [#{issue_number}]({issue_url}) {issue_title} (User: {closed_by})")
        else:
            content_parts.append(f"最近 {days} 天内没有关闭的 Issues。\n")

        content_parts.append("\n### ⇄ Pull Requests (Closed/Merged):\n")
        if pull_requests:
            for pr in pull_requests[:10]: # Display top 10 PRs
                pr_number = pr.get('number')
                pr_title = pr.get('title', 'N/A')
                pr_url = pr.get('html_url', '#')
                pr_state = pr.get('state', 'N/A')
                pr_user = pr.get('user', {}).get('login', 'N/A')
                content_parts.append(f"- [#{pr_number}]({pr_url}) {pr_title} (State: {pr_state}, by {pr_user})")
        else:
            content_parts.append(f"最近 {days} 天内没有关闭或合并的 Pull Requests。\n")

        # Add formatted releases section
        content_parts.append("\n" + self._format_releases_markdown(recent_releases))

        return "\n".join(content_parts)

    def generate_github_project_report(self, owner: str, repo_name: str, days: int = None) -> str:
        """
        Generates a report for a single GitHub project, including recent releases.
        It first compiles factual data, then optionally uses an LLM for a summary.
        """
        if days is None:
            # Assuming settings has a method to get this default value
            days = self.settings.get_github_progress_frequency_days()
        LOG.info(f"准备为 {owner}/{repo_name} 生成项目报告 (过去 {days} 天)...")

        # 1. Generate the factual Markdown content
        factual_markdown = self._generate_github_project_basic_info_markdown(owner, repo_name, days)

        # 2. (Optional) Pass to LLM for summarization/analysis
        # Check if a specific prompt for "github" type is loaded and LLM is available
        system_prompt = self.prompts.get("github") # Get preloaded prompt
        if system_prompt and self.llm and hasattr(self.llm, 'generate_report'):
            LOG.debug(f"使用 LLM 为 {owner}/{repo_name} 生成摘要报告。")
            try:
                report_content = self.llm.generate_report(system_prompt, factual_markdown)
                # One could choose to prepend/append factual_markdown to LLM summary here,
                # or let the prompt guide the LLM on how to use the factual data.
                # For now, the LLM output is considered the final report if successful.
            except Exception as e:
                LOG.error(f"LLM 生成报告 for {owner}/{repo_name} 失败: {e}")
                LOG.warning(f"LLM 生成失败，将返回原始数据报告 for {owner}/{repo_name}。")
                report_content = factual_markdown # Fallback to factual data
        else:
            LOG.info(f"LLM 提示或 LLM 实例未完全配置，返回原始数据报告 for {owner}/{repo_name}。")
            report_content = factual_markdown # Fallback to factual data

        # Note: Saving the report to a file is removed from this method.
        # The caller (e.g., Streamlit app or a batch process) should handle saving if needed.

        return report_content

    def generate_github_report(self, markdown_file_path):
        """
        DEPRECATED/TO BE REFACTORED.
        This method is based on pre-generated markdown files and does not fit the new model
        of fetching data directly via GitHubClient and then formatting/summarizing.
        Consider removing or adapting if a use case for processing external markdown remains.
        生成 GitHub 项目的报告，并保存为 {original_filename}_report.md。
        """
        LOG.warning("DEPRECATED: generate_github_report(markdown_file_path) called. This method is outdated.")
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        system_prompt = self.prompts.get("github", "Summarize the provided GitHub project information:") # Ensure default
        report = self.llm.generate_report(system_prompt, markdown_content)
        
        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path} (using deprecated method)")
        return report, report_file_path

    def generate_github_subscription_report(self) -> str:
        """
        Generates a combined report for all subscribed GitHub repositories.
        """
        LOG.info("准备生成 GitHub 订阅总报告...")
        # Assuming settings has a method to get subscriptions,
        # e.g., get_github_subscriptions() -> list of dicts like [{"owner": "o", "repo": "r"}, ...]
        subscriptions = self.settings.get_github_subscriptions()
        if not subscriptions:
            LOG.warning("配置文件中没有找到 GitHub 订阅。")
            return "没有配置 GitHub 仓库订阅，无法生成报告。"

        full_report_parts = [f"# GitHub 订阅总报告 - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}\n"]
        days = self.settings.get_github_progress_frequency_days()

        for sub in subscriptions:
            owner = sub.get("owner")
            # repo_name = sub.get("repo") # Original assumed key
            repo_name = sub.get("repo_name") or sub.get("repo") # Accommodate "repo" or "repo_name"

            if not owner or not repo_name:
                LOG.warning(f"订阅条目格式不正确（缺少 owner 或 repo_name），跳过: {sub}")
                continue

            LOG.debug(f"为订阅仓库 {owner}/{repo_name} 生成单项目报告部分...")
            # Generate basic info markdown for each repo
            repo_markdown_content = self._generate_github_project_basic_info_markdown(owner, repo_name, days)
            full_report_parts.append(f"\n---\n{repo_markdown_content}\n---")
        
        combined_markdown_content = "\n".join(full_report_parts)

        # Option 2: Pass the combined markdown to LLM for a summary (if desired)
        # Assuming a specific prompt key like "github_subscription" or "github_summary"
        # For this example, let's use "github_digest" as a potential key
        system_prompt = self.prompts.get("github_digest") # Or "github_subscription_summary"
        if system_prompt and self.llm and hasattr(self.llm, 'generate_report'):
            LOG.debug("使用 LLM 为 GitHub 订阅总报告生成摘要。")
            try:
                final_report = self.llm.generate_report(system_prompt, combined_markdown_content)
                return final_report
            except Exception as e:
                LOG.error(f"LLM 生成 GitHub 订阅总报告失败: {e}")
                LOG.warning("LLM 生成 GitHub 订阅总报告失败，将返回组合数据报告。")
                return combined_markdown_content # Fallback
        else:
            LOG.info("LLM 提示 (e.g., github_digest) 或 LLM 实例未完全配置，返回组合数据报告。")
            return combined_markdown_content


    def generate_hacker_news_hours_topic_report(self, content: str) -> str:
        """
        Generates a report for Hacker News hourly topics using provided content.
        """
        if not content: # Check if content is None or empty
            LOG.error("Hacker News 小时主题报告需要 content 参数。")
            return "错误: 未提供Hacker News小时主题报告的内容。"
        
        system_prompt = self.prompts.get("hacker_news_hours_topic", "Summarize the top Hacker News topics from the last hour:")
        LOG.debug(f"使用提示生成 HN 小时主题报告: '{system_prompt[:50]}...'")
        try:
            report = self.llm.generate_report(system_prompt, content)
        except Exception as e:
            LOG.error(f"LLM 生成 HN 小时主题报告失败: {e}")
            return f"错误: LLM 生成 HN 小时主题报告失败 - {e}"
        
        LOG.info("Hacker News 小时主题报告已生成。")
        return report

    def generate_hacker_news_daily_report(self, aggregated_content: str) -> str:
        """
        Generates a daily summary report for Hacker News from aggregated hourly topics content.
        """
        if not aggregated_content: # Check if content is None or empty
            LOG.error("Hacker News 每日摘要报告需要 aggregated_content 参数。")
            return "错误: 未提供Hacker News每日摘要报告的内容。"

        system_prompt = self.prompts.get("hacker_news_daily_report", "Summarize the main Hacker News trends from the day:")
        LOG.debug(f"使用提示生成 HN 每日摘要报告: '{system_prompt[:50]}...'")
        try:
            report = self.llm.generate_report(system_prompt, aggregated_content)
        except Exception as e:
            LOG.error(f"LLM 生成 HN 每日摘要报告失败: {e}")
            return f"错误: LLM 生成 HN 每日摘要报告失败 - {e}"

        LOG.info("Hacker News 每日摘要报告已生成。")
        return report

    # _aggregate_topic_reports is removed as its functionality is moved to the caller.

if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    from llm import LLM
    # Placeholder for GitHubClient if needed for main block testing
    # from github_client import GitHubClient

    LOG.info("ReportGenerator __main__ block for testing (partially active).")
    # Mock or simplified settings and clients for basic __init__ testing
    class MockSettings:
        def get_report_types(self):
            LOG.debug("[MockSettings] get_report_types called")
            return ["github", "hacker_news_hours_topic", "hacker_news_daily_report", "github_digest", "non_existent_prompt_type"]

        def get_prompt_file_path(self, key):
            LOG.debug(f"[MockSettings] get_prompt_file_path called with key: {key}")
            dummy_prompt_dir = "prompts"
            os.makedirs(dummy_prompt_dir, exist_ok=True)

            # Specific prompt for github_digest
            if key == "github_digest_mock_model":
                path = os.path.join(dummy_prompt_dir, "github_digest_mock_model_prompt.txt")
                if not os.path.exists(path):
                    with open(path, "w") as f: f.write("Summarize this collection of GitHub project updates.")
                return path

            # Generic prompt for github (single project)
            if key == "github_mock_model":
                path = os.path.join(dummy_prompt_dir, "github_mock_model_prompt.txt")
                if not os.path.exists(path):
                    with open(path, "w") as f: f.write("This is a mock GitHub prompt for testing.")
                return path

            # For HN, assume they might not have specific files and will use default from .get() in _preload_prompts
            if key.startswith("hacker_news"):
                 return os.path.join(dummy_prompt_dir, f"{key}_prompt.txt") # Path that might not exist

            return None

        def get_github_progress_frequency_days(self):
            LOG.debug("[MockSettings] get_github_progress_frequency_days called")
            return 7

        def get_github_subscriptions(self):
            LOG.debug("[MockSettings] get_github_subscriptions called")
            return [
                {"owner": "mockowner1", "repo": "mockrepo1"},
                {"owner": "mockowner2", "repo_name": "mockrepo2"} # Test with "repo_name" too
            ]

    class MockLLM:
        def __init__(self):
            self.model = "mock_model"
        def generate_report(self, system_prompt, user_content):
            LOG.debug(f"[MockLLM] generate_report called. System prompt starts with: '{system_prompt[:50]}...'")
            return f"LLM Summary: {user_content[:150]}..."

    class MockGitHubClient:
        def fetch_commits(self, repo_full_name, since): return [{"sha": "abc1234", "commit": {"message": f"Commit for {repo_full_name}"}, "author": {"login": "dev"}, "html_url": "#"}]
        def fetch_issues(self, repo_full_name, since): return [{"number": 1, "title": f"Issue for {repo_full_name}", "html_url": "#", "user": {"login": "reporter"}}]
        def fetch_pull_requests(self, repo_full_name, since): return [{"number": 2, "title": f"PR for {repo_full_name}", "html_url": "#", "state": "closed", "user": {"login": "merger"}}]
        def get_recent_releases(self, owner, repo_name, days_limit, count_limit=5):
            return [{"name": f"Release for {owner}/{repo_name}", "tag_name": "v1.0", "html_url": "#", "author_login": "releaser", "published_at": datetime.now(timezone.utc).isoformat(), "body": "Release notes."}]

    try:
        settings_mock = MockSettings()
        llm_mock = MockLLM()
        github_client_mock = MockGitHubClient()

        LOG.info("Initializing ReportGenerator with Mocks for full test...")
        report_generator = ReportGenerator(llm=llm_mock, settings=settings_mock, github_client=github_client_mock)
        LOG.info(f"ReportGenerator initialized successfully.")
        LOG.info(f"Loaded report types: {report_generator.report_types}")
        LOG.info(f"Loaded prompts: {report_generator.prompts.keys()}")
        # Check if the github prompt was loaded and others handled
        assert "github" in report_generator.prompts and report_generator.prompts["github"] != "Please summarize the following content:"
        assert "hacker_news_hours_topic" in report_generator.prompts and report_generator.prompts["hacker_news_hours_topic"] == "Please summarize the following content:"
        assert "non_existent_prompt_type" in report_generator.prompts # It will get a default prompt

        # Example of testing _format_releases_markdown (can be uncommented for local testing)
        # LOG.info("Testing _format_releases_markdown...")
        # sample_releases_data = [
        #     {"name": "Awesome Release v1.1", "tag_name": "v1.1", "html_url": "https://example.com/releases/v1.1",
        #      "author_login": "release-guru", "published_at": "2023-10-27T10:00:00Z", "body": "## New Features\n- Feature A\n- Feature B"},
        #     {"name": "Hotfix v1.1.1", "tag_name": "v1.1.1", "html_url": "https://example.com/releases/v1.1.1",
        #      "author_login": "fixer", "published_at": "2023-10-28T15:30:00Z", "body": "Fixed critical bug #123."}
        # ]
        # formatted_md = report_generator._format_releases_markdown(sample_releases_data)
        # LOG.debug("Sample Formatted Releases Markdown:\n" + formatted_md)
        # formatted_empty_md = report_generator._format_releases_markdown([])
        # LOG.debug("Sample Formatted Empty Releases Markdown:\n" + formatted_empty_md)

        # Test generate_github_project_report (requires MockGitHubClient methods to be implemented)
        # LOG.info("Testing generate_github_project_report...")
        # test_owner, test_repo = "testowner", "testrepo"
        # if hasattr(github_client_mock, 'fetch_commits'): # Check if mock methods are ready
        #     project_report_content = report_generator.generate_github_project_report(test_owner, test_repo)
        #     LOG.debug(f"Generated project report for {test_owner}/{test_repo}:\n{project_report_content[:300]}...")
        # else:
        #     LOG.warning("MockGitHubClient methods not fully implemented. Skipping generate_github_project_report test.")


    except Exception as e:
        LOG.error(f"Error in __main__ block during ReportGenerator testing: {e}", exc_info=True)

    LOG.info("ReportGenerator __main__ testing (for __init__ and _preload_prompts) finished.")