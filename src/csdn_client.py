import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML内容
from datetime import datetime  # 导入datetime模块用于获取日期和时间
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class CSDNClient:
    def __init__(self):
        self.url = 'https://blog.csdn.net/nav/aigc-0'  # CSDN文章列表的URL
        self.headers = {
            'referer': 'https://blog.csdn.net/nav',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
        }  # 设置浏览器用户代理

    def fetch_article_list(self):
        LOG.debug("准备获取CSDN文章列表。")
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)  # 使用自定义的头部进行请求
            response.raise_for_status()  # 检查请求是否成功
            articles = self.parse_articles(response.text)  # 解析文章数据
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
        with open(file_path, 'w') as file:
            file.write(f"# CSDN Articles List ({date} {hour}:00)\n\n")
            for idx, article in enumerate(articles, start=1):
                file.write(f"{idx}. [{article['title']}]({article['link']})\n")
        
        LOG.info(f"CSDN文章列表文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = CSDNClient()
    client.export_articles()  # 默认情况下使用当前日期和时间
