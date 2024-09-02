import os  # 导入os模块用于文件和目录操作
import time  # time
from datetime import datetime  # 导入datetime模块用于获取日期和时间
from logger import LOG  # 导入日志模块
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML内容
from selenium import webdriver  # 导入Selenium库用于网页自动化
from selenium.webdriver.chrome.service import Service as ChromeService  # 导入Chrome服务
from webdriver_manager.chrome import ChromeDriverManager  # 导入Chrome驱动管理器

class CSDNClient:
    def __init__(self):
        self.url = 'https://blog.csdn.net/nav/aigc-0'  # CSDN文章列表的URL

    def fetch_article_list(self):
        LOG.debug("准备获取CSDN文章列表。")
        try:
            # 使用Selenium打开网页
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 无头模式
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Enable handling of cookies and redirects
            options.add_argument('--enable-cookies')  # 确保启用Cookies
            options.add_argument('accept-insecure-certificates')  # 接受不安全的证书
            options.add_argument("--enable-javascript")

            # 创建浏览器实例
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            driver.get(self.url)  # 打开指定的URL
            self.driver = driver 
            time.sleep(10)  # 等待页面加载完成（10秒
            # 获取页面源码
            html_content = driver.page_source
            
            driver.quit()  # 关闭浏览器
            articles = self.parse_articles(html_content)  # 
            return articles
        except Exception as e:
            LOG.error(f"获取CSDN文章列表失败：{str(e)}")
            return []

    def parse_articles(self, html_content):
        LOG.debug("解析CSDN页面的HTML内容。")
        soup = BeautifulSoup(html_content, 'html.parser')
        article_tags = soup.find_all('a', class_='blog')  # 查找所有包含文章标题的<a>标签
        
        articles = []
        for tag in article_tags:
            link = tag['href']  # 获取文章链接
            title = tag.find('span', class_='blog-text').text.strip()  # 获取文章标题
            articles.append({'title': title, 'link': link})
        
        LOG.info(f"成功解析 {len(articles)} 篇CSDN文章。")
        return articles

    def export_articles(self, date=None, hour=None):
        LOG.debug("准备导出CSDN文章列表。")
        articles = self.fetch_article_list()  # 获取文章数据
        
        if not articles:
            LOG.warning("未找到任何CSDN文章。")
            return None
        
        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # 构建存储路径
        dir_path = os.path.join('csdn_articles', date)
        os.makedirs(dir_path, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(dir_path, f'{hour}.md')  # 定义文件路径
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# CSDN Articles List ({date} {hour}:00)\n\n")
            for idx, article in enumerate(articles, start=1):
                file.write(f"{idx}. [{article['title']}]({article['link']})\n")
        
        LOG.info(f"CSDN文章列表文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = CSDNClient()
    client.export_articles()  # 默认情况下使用当前日期和时间
