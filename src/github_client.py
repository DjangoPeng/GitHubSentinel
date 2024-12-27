# src/github_client.py

import requests
import datetime

class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

    def fetch_updates(self, repos):
        updates = {}
        for repo in repos:
            updates[repo] = {
                'commits': self.fetch_commits(repo),
                'issues': self.fetch_issues(repo),
                'pull_requests': self.fetch_pull_requests(repo)
            }
        return updates

    def fetch_commits(self, repo):
        url = f'https://api.github.com/repos/{repo}/commits'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_issues(self, repo):
        url = f'https://api.github.com/repos/{repo}/issues'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_pull_requests(self, repo):
        url = f'https://api.github.com/repos/{repo}/pulls'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def export_daily_progress(self, repo):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        issues = self.fetch_issues(repo)
        pull_requests = self.fetch_pull_requests(repo)
        commits = self.fetch_commits(repo)
        filename = f"{repo.replace('/', '_')}_{date_str}.md"

        with open(filename, 'w') as f:
            f.write(f"# {repo} Daily Progress - {date_str}\n\n")
            f.write("## Issues\n")
            for issue in issues:
                f.write(f"- {issue['title']} #{issue['number']}\n")
            f.write("\n## Pull Requests\n")
            for pr in pull_requests:
                f.write(f"- {pr['title']} #{pr['number']}\n")
            f.write("\n## Commits\n")
            for commit in commits:
                f.write(f"- {commit['commit']['message']} (SHA: {commit['sha']})\n")

        print(f"Exported daily progress to {filename}")

        return filename
