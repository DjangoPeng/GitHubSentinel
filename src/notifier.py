import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify_github_report(self, repo, report):
        """
        发送 GitHub 项目报告邮件
        :param repo: 仓库名称
        :param report: 报告内容
        """
        if self.email_settings:
            subject = f"[GitHub] {repo} 进展简报"
            self.send_email(subject, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 GitHub 报告通知")
    
    def notify_hn_report(self, date, report):
        """
        发送 Hacker News 每日技术趋势报告邮件
        :param date: 报告日期
        :param report: 报告内容
        """
        if self.email_settings:
            subject = f"[HackerNews] {date} 技术趋势"
            self.send_email(subject, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 Hacker News 报告通知")
    
    def send_email(self, subject, report):
        LOG.info(f"准备发送邮件:{subject}")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = subject
        
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

    # 测试 GitHub 报告邮件通知
    test_repo = "DjangoPeng/openai-quickstart"
    test_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    notifier.notify_github_report(test_repo, test_report)

    # 测试 Hacker News 报告邮件通知
    hn_report = """
# Hacker News 前沿技术趋势 (2024-09-01)

## Top 1：硬盘驱动器的讨论引发热门讨论

关于硬盘驱动器的多个讨论，尤其是关于未使用和不需要的硬盘驱动器的文章，显示出人们对科技过时技术的兴趣。

详细内容见相关链接：

- http://tom7.org/harder/
- http://tom7.org/harder/

## Top 2：学习 Linux 的重要性和 Bubbletea 程序开发

有关于 Linux 的讨论，强调了 Linux 在现代开发中的重要性和应用性，以及关于构建 Bubbletea 程序的讨论，展示了 Bubbletea 在开发中的应用性和可能性。

详细内容见相关链接：

- https://opiero.medium.com/why-you-should-learn-linux-9ceace168e5c
- https://leg100.github.io/en/posts/building-bubbletea-programs/

## Top 3：Nvidia 在 AI 领域中的强大竞争力

有关于 Nvidia 的四个未知客户，每个人购买价值超过 3 亿美元的讨论，显示出 N 维达在 AI 领域中的强大竞争力。

详细内容见相关链接：

- https://fortune.com/2024/08/29/nvidia-jensen-huang-ai-customers/

"""
    notifier.notify_hn_report("2024-09-01", hn_report)
