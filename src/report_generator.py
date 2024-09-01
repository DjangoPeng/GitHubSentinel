import os
from logger import LOG  # 导入日志模块

class ReportGenerator:
    def __init__(self, llm, report_types):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告
        self.report_types = report_types
        self.prompts = {}  # 存储所有预加载的提示信息
        self._preload_prompts()

    def _preload_prompts(self):
        """
        预加载所有可能的提示文件，并存储在字典中。
        """
        for report_type in self.report_types:  # 使用从配置中加载的报告类型
            prompt_file = f"prompts/{report_type}_{self.llm.model}_prompt.txt"
            if not os.path.exists(prompt_file):
                LOG.error(f"提示文件不存在: {prompt_file}")
                raise FileNotFoundError(f"提示文件未找到: {prompt_file}")
            with open(prompt_file, "r", encoding='utf-8') as file:
                self.prompts[report_type] = file.read()

    def generate_github_report(self, markdown_file_path):
        """
        生成 GitHub 项目的报告，并保存为 {original_filename}_report.md。
        """
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        system_prompt = self.prompts.get("github")
        report = self.llm.generate_report(system_prompt, markdown_content)
        
        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")
        return report, report_file_path

    def generate_hn_topic_report(self, markdown_file_path):
        """
        生成 Hacker News 小时主题的报告，并保存为 {original_filename}_topic.md。
        """
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        system_prompt = self.prompts.get("hacker_news_hours_topic")
        report = self.llm.generate_report(system_prompt, markdown_content)
        
        report_file_path = os.path.splitext(markdown_file_path)[0] + "_topic.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        LOG.info(f"Hacker News 热点主题报告已保存到 {report_file_path}")
        return report, report_file_path

    def generate_hn_daily_report(self, directory_path):
        """
        生成 Hacker News 每日汇总的报告，并保存到 hacker_news/tech_trends/ 目录下。
        这里的输入是一个目录路径，其中包含所有由 generate_hn_topic_report 生成的 *_topic.md 文件。
        """
        markdown_content = self._aggregate_topic_reports(directory_path)
        system_prompt = self.prompts.get("hacker_news_daily_report")

        base_name = os.path.basename(directory_path.rstrip('/'))
        report_file_path = os.path.join("hacker_news/tech_trends/", f"{base_name}_trends.md")

        # 确保 tech_trends 目录存在
        os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
        
        report = self.llm.generate_report(system_prompt, markdown_content)
        
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)
        
        LOG.info(f"Hacker News 每日汇总报告已保存到 {report_file_path}")
        return report, report_file_path


    def _aggregate_topic_reports(self, directory_path):
        """
        聚合目录下所有以 '_topic.md' 结尾的 Markdown 文件内容，生成每日汇总报告的输入。
        """
        markdown_content = ""
        for filename in os.listdir(directory_path):
            if filename.endswith("_topic.md"):
                with open(os.path.join(directory_path, filename), 'r') as file:
                    markdown_content += file.read() + "\n"
        return markdown_content


if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    from llm import LLM

    config = Config()
    llm = LLM(config)
    report_generator = ReportGenerator(llm, config.report_types)

    # hn_hours_file = "./hacker_news/2024-09-01/14.md"
    hn_daily_dir = "./hacker_news/2024-09-01/"

    # report, report_file_path = report_generator.generate_hn_topic_report(hn_hours_file)
    report, report_file_path = report_generator.generate_hn_daily_report(hn_daily_dir)
    LOG.debug(report)