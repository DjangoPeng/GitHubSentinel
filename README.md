# GitHub Sentinel

GitHub Sentinel is an open-source tool AI Agent designed for developers and project managers. It automatically retrieves and aggregates updates from subscribed GitHub repositories on a regular basis (daily/weekly). Key features include subscription management, update retrieval, notification system, and report generation.

## Features
- Subscription management
- Update retrieval
- Notification system
- Report generation

## Getting Started
1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Configure the application by editing `config.json`.

3. Run the application:
    ```sh
    python src/main.py
    ```

## Configuration
The configuration file `config.json` should contain the following settings:
```json
{
    "github_token": "your_github_token",
    "notification_settings": {
        "email": "your_email@example.com",
        "slack_webhook_url": "your_slack_webhook_url"
    },
    "subscriptions_file": "subscriptions.json",
    "update_interval": 86400
}
```
