# src/llm.py

import openai

class LLM:
    def __init__(self, api_key):
        openai.api_key = api_key

    def summarize_issues_prs(self, issues, pull_requests):
        prompt = (
            "Summarize the following GitHub issues and pull requests in a formal report format:\n\n"
            "## Issues\n"
        )
        for issue in issues:
            prompt += f"- {issue['title']} #{issue['number']}: {issue['body']}\n"
        prompt += "\n## Pull Requests\n"
        for pr in pull_requests:
            prompt += f"- {pr['title']} #{pr['number']}: {pr['body']}\n"

        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=500
        )

        return response.choices[0].text.strip()
