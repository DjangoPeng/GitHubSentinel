# src/llm.py

import os
import logging
from openai import OpenAI, APIConnectionError, RateLimitError

class LLM:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(timeout=300)

    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            return "DRY RUN"

        logging.info("Calling GPT API")
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=30
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            logging.error(f"API connection error: {e}")
            raise
        except RateLimitError as e:
            logging.error(f"Rate limit exceeded: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
