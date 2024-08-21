# src/github_client.py

import requests  # 导入requests库用于HTTP请求
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class GitHubClient:
    def __init__(self, token):
        self.token = token  # GitHub API令牌
        self.headers = {'Authorization': f'token {self.token}'}  # 设置HTTP头部认证信息

    def fetch_updates(self, repo, since=None, until=None):
        # 获取指定仓库的更新，可以指定开始和结束日期
        updates = {
            'commits': self.fetch_commits(repo, since, until),  # 获取提交记录
            'issues': self.fetch_issues(repo, since),  # 获取问题 【修改1：移除 until 参数】
            'pull_requests': self.fetch_pull_requests(repo, since, until)  # 获取拉取请求 【修改2：手动过滤日期】
        }
        return updates

    def fetch_commits(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/commits'  # 构建获取提交的API URL
        params = {}
        if since:
            params['since'] = since  # 如果指定了开始日期，添加到参数中
        if until:
            params['until'] = until  # 如果指定了结束日期，添加到参数中

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # 检查请求是否成功
        except requests.exceptions.RequestException as e:
            LOG.error(f"Failed to fetch commits for repo {repo}: {e}")  # 【修改3：增强的日志记录和异常处理】
            return []

        return response.json()  # 返回JSON格式的数据

    def fetch_issues(self, repo, since=None):
        url = f'https://api.github.com/repos/{repo}/issues'  # 构建获取问题的API URL
        params = {
            'state': 'closed',  # 仅获取已关闭的问题
            'since': since,  # 只使用 since 参数来限制日期范围 【修改1：移除 until 参数】
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_pull_requests(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/pulls'  # 构建获取拉取请求的API URL
        params = {
            'state': 'closed',  # 仅获取已关闭（包括已合并）的拉取请求
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        pull_requests = response.json()
        
        # 【修改2：手动过滤日期范围内的拉取请求】
        if since or until:
            filtered_prs = []
            for pr in pull_requests:
                pr_closed_at = datetime.strptime(pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                if (since is None or pr_closed_at >= datetime.fromisoformat(since)) and \
                   (until is None or pr_closed_at <= datetime.fromisoformat(until)):
                    filtered_prs.append(pr)
            return filtered_prs
        
        return pull_requests

    def export_daily_progress(self, repo):
        today = datetime.now().date().isoformat()  # 获取今天的日期
        updates = self.fetch_updates(repo, since=today)  # 获取今天的更新数据
        
        # 【修改4：手动过滤今天的拉取请求和问题】
        issues_today = [issue for issue in updates['issues'] if issue['closed_at'].startswith(today)]
        pull_requests_today = [pr for pr in updates['pull_requests'] if pr['closed_at'].startswith(today)]
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建存储路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(repo_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for {repo} ({today})\n\n")
            file.write("\n## Issues Closed Today\n")
            for issue in issues_today:  # 写入今天关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write("\n## Pull Requests Merged Today\n")
            for pr in pull_requests_today:  # 写入今天合并的拉取请求
                file.write(f"- {pr['title']} #{pr['number']}\n")
        
        LOG.info(f"Exported daily progress to {file_path}")  # 记录日志
        return file_path

    def export_progress_by_date_range(self, repo, days):
        today = date.today()  # 获取当前日期
        since = today - timedelta(days=days)  # 计算开始日期
        
        updates = self.fetch_updates(repo, since=since.isoformat())  # 获取指定日期范围内的更新
        
        # 【修改5：手动过滤指定日期范围内的拉取请求和问题】
        issues_in_range = [issue for issue in updates['issues'] if since.isoformat() <= issue['closed_at'][:10] <= today.isoformat()]
        pull_requests_in_range = [pr for pr in updates['pull_requests'] if since.isoformat() <= pr['closed_at'][:10] <= today.isoformat()]
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        date_str = f"{since}_to_{today}"  # 更新文件名以包含日期范围
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for issue in issues_in_range:  # 写入在指定日期内关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write(f"\n## Pull Requests Merged in the Last {days} Days\n")
            for pr in pull_requests_in_range:  # 写入在指定日期内合并的拉取请求
                file.write(f"- {pr['title']} #{pr['number']}\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")  # 记录日志
        return file_path
