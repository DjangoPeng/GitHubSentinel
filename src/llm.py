# src/llm.py

import openai

class LLM:
    def __init__(self, api_key):
        openai.api_key = api_key

    def summarize_issues_prs_commits(self, issues, pull_requests, commits):
        prompt = (
            "Summarize the following GitHub issues, pull requests, and commits in a formal report format:\n\n"
            "## Issues\n"
        )
        for issue in issues:
            prompt += f"- {issue}\n"
        prompt += "\n## Pull Requests\n"
        for pr in pull_requests:
            prompt += f"- {pr}\n"
        prompt += "\n## Commits\n"
        for commit in commits:
            prompt += f"- {commit}\n"

        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=500
        )

        return response.choices[0].text.strip()
