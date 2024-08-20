# GitHub Sentinel

<p align="center">
    <br> <a href="README-EN.md">English</a> | 中文
</p>

GitHub Sentinel 是一个开源的工具 AI 代理，专为开发人员和项目经理设计。它会定期（每日/每周）自动从订阅的 GitHub 仓库中检索和汇总更新。主要功能包括订阅管理、更新检索、通知系统和报告生成。

## 功能
- 订阅管理
- 更新检索
- 通知系统
- 报告生成

## 快速开始

### 1. 安装依赖

首先，安装所需的依赖项：

```sh
pip install -r requirements.txt
```

### 2. 配置应用

编辑 `config.json` 文件，以设置您的 GitHub 令牌、通知设置、订阅文件和更新间隔：

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

### 3. 如何运行

GitHub Sentinel 支持以下三种运行方式：

#### A. 作为命令行工具运行

您可以从命令行交互式地运行该应用：

```sh
python src/command_tool.py
```

在此模式下，您可以手动输入命令来管理订阅、检索更新和生成报告。

#### B. 作为后台进程运行（带调度器）

要将该应用作为后台服务（守护进程）运行，它将定期检查更新：

1. 确保您已安装 `python-daemon` 包：

    ```sh
    pip install python-daemon
    ```

2. 启动后台进程：

    ```sh
    nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
    ```

   - 这将启动后台调度器，按照 `config.json` 中指定的间隔定期检查更新。
   - 日志将保存到 `logs/daemon_process.log` 文件中。

#### C. 作为 Gradio 服务器运行

要使用 Gradio 界面运行应用，允许用户通过 Web 界面与该工具交互：

```sh
python src/gradio_server.py
```

- 这将在您的机器上启动一个 Web 服务器，允许您通过用户友好的界面管理订阅和生成报告。
- 默认情况下，Gradio 服务器将可在 `http://localhost:7860` 访问，但如果需要，您可以公开共享它。