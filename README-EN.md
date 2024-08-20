# GitHub Sentinel

<p align="center">
    <br> English | <a href="README.md">中文</a>
</p>

GitHub Sentinel is an open-source tool AI Agent designed for developers and project managers. It automatically retrieves and aggregates updates from subscribed GitHub repositories on a regular basis (daily/weekly). Key features include subscription management, update retrieval, notification system, and report generation.

## Features
- Subscription management
- Update retrieval
- Notification system
- Report generation

## Getting Started

### 1. Install Dependencies

First, install the required dependencies:

```sh
pip install -r requirements.txt
```

### 2. Configure the Application

Edit the `config.json` file to set up your GitHub token, notification settings, subscription file, and update interval:

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

### 3. How to Run

GitHub Sentinel supports three different ways to run the application:

#### A. Run as a Command-Line Tool

You can run the application interactively from the command line:

```sh
python src/command_tool.py
```

In this mode, you can manually input commands to manage subscriptions, retrieve updates, and generate reports.

#### B. Run as a Daemon Process with Scheduler

To run the application as a background service (daemon) that regularly checks for updates:

1. Ensure you have the `python-daemon` package installed:

    ```sh
    pip install python-daemon
    ```

2. Launch the daemon process:

    ```sh
    nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
    ```

   - This will start the scheduler in the background, checking for updates at the interval specified in your `config.json`.
   - Logs will be saved to the `logs/daemon_process.log` file.

#### C. Run as a Gradio Server

To run the application with a Gradio interface, allowing users to interact with the tool via a web interface:

```sh
python src/gradio_server.py
```

- This will start a web server on your machine, allowing you to manage subscriptions and generate reports through a user-friendly interface.
- By default, the Gradio server will be accessible at `http://localhost:7860`, but you can share it publicly if needed.
