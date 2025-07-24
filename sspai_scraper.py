import requests
from bs4 import BeautifulSoup
import time
import json
import os
from typing import Dict, List, Optional
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SSPaiScraper:
    """少数派文章爬取和摘要生成器"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        初始化爬虫

        Args:
            openai_api_key: OpenAI API密钥（可选，默认从环境变量读取）
        """
        # 优先使用传入的API密钥，否则从环境变量读取
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量或传入API密钥")

        self.base_url = "https://sspai.com/post/{}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_article(self, article_id: str) -> Optional[Dict[str, str]]:
        """
        爬取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            包含文章标题和内容的字典，失败返回None
        """
        url = self.base_url.format(article_id)

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取文章标题 - 根据实际HTML结构优化
            title_element = soup.find('div', {'id': 'article-title', 'class': 'title'})
            if not title_element:
                # 备用选择器
                title_element = soup.find('div', class_='title')

            title = title_element.text.strip() if title_element else "未找到标题"

            # 提取文章内容 - 使用更精确的选择器
            content_element = soup.find('div', class_='content wangEditor-txt')
            if not content_element:
                # 备用选择器
                content_element = soup.find('div', class_='content')

            if content_element:
                # 移除可能的脚本、样式和图片说明标签
                for tag in content_element(['script', 'style', 'figcaption']):
                    tag.decompose()

                # 获取所有段落和标题
                text_parts = []
                for element in content_element.find_all(
                        ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'ul', 'ol']):
                    text = element.get_text(strip=True)
                    if text:
                        text_parts.append(text)

                content = '\n\n'.join(text_parts)
            else:
                content = "未找到文章内容"

            # 提取作者信息 - 使用更精确的选择器
            author_element = soup.find('a', class_='ss__user__nickname__wrapper nickname')
            if not author_element:
                # 备用选择器
                author_element = soup.find('div', class_='ss__user__nickname')

            if author_element:
                author = author_element.find('span').text.strip() if author_element.find(
                    'span') else author_element.text.strip()
            else:
                author = "未知作者"

            # 提取发布时间（可选）
            time_element = soup.find('div', class_='timer')
            publish_time = time_element.text.strip() if time_element else ""

            logging.info(f"成功爬取文章: {title}")

            return {
                'id': article_id,
                'url': url,
                'title': title,
                'author': author,
                'content': content,
                'publish_time': publish_time,
                'fetch_time': datetime.now().isoformat()
            }

        except requests.RequestException as e:
            logging.error(f"爬取文章 {article_id} 失败: {e}")
            return None
        except Exception as e:
            logging.error(f"处理文章 {article_id} 时出错: {e}")
            return None

    def generate_summary(self, article: Dict[str, str], max_length: int = 200) -> str:
        """
        使用OpenAI API生成文章摘要

        Args:
            article: 文章信息字典
            max_length: 摘要最大长度（字数）

        Returns:
            生成的摘要
        """
        try:
            # 初始化OpenAI客户端（新版本API）
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            # 准备提示词
            prompt = f"""请为以下文章生成一个简洁的中文摘要，摘要应该：
1. 控制在{max_length}字以内
2. 概括文章的主要内容和核心观点
3. 保持客观中立的语气
4. 使用流畅的中文表达

文章标题：{article['title']}
文章内容：
{article['content'][:3000]}  # 限制输入长度以节省token

请生成摘要："""

            # 调用OpenAI API（新版本方式）
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 使用更经济的模型
                messages=[
                    {"role": "system", "content": "你是一个专业的内容摘要生成助手，擅长提取文章核心内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            logging.info(f"成功生成文章 {article['id']} 的摘要")

            return summary

        except Exception as e:
            logging.error(f"生成摘要失败: {e}")
            # 如果API调用失败，尝试生成简单摘要
            return self._generate_simple_summary(article, max_length)

    def _generate_simple_summary(self, article: Dict[str, str], max_length: int = 200) -> str:
        """
        生成简单摘要（不使用AI）

        Args:
            article: 文章信息字典
            max_length: 摘要最大长度

        Returns:
            简单摘要
        """
        content = article['content']
        # 取前几段内容作为摘要
        paragraphs = content.split('\n\n')
        summary = ""

        for para in paragraphs:
            if len(summary) + len(para) <= max_length:
                summary += para + " "
            else:
                remaining = max_length - len(summary)
                if remaining > 20:  # 如果剩余空间足够
                    summary += para[:remaining - 3] + "..."
                break

        return summary.strip() if summary else content[:max_length - 3] + "..."

    def process_article(self, article_id: str) -> Optional[Dict[str, str]]:
        """
        处理单篇文章：爬取并生成摘要

        Args:
            article_id: 文章ID

        Returns:
            包含文章信息和摘要的字典
        """
        # 爬取文章
        article = self.fetch_article(article_id)
        if not article:
            return None

        # 生成摘要
        summary = self.generate_summary(article)
        article['summary'] = summary

        return article

    def process_multiple_articles(self, article_ids: List[str], delay: float = 2.0) -> List[Dict[str, str]]:
        """
        批量处理多篇文章

        Args:
            article_ids: 文章ID列表
            delay: 请求之间的延迟（秒）

        Returns:
            处理结果列表
        """
        results = []

        for i, article_id in enumerate(article_ids):
            logging.info(f"处理第 {i + 1}/{len(article_ids)} 篇文章: {article_id}")

            result = self.process_article(article_id)
            if result:
                results.append(result)

            # 添加延迟，避免请求过快
            if i < len(article_ids) - 1:
                time.sleep(delay)

        return results

    def process_article_range(self, start_id: int, end_id: int, output_file: str = "abstract.jsonl", delay: float = 0.2):
        """
        批量处理指定范围的文章ID，并实时保存到JSONL文件

        Args:
            start_id: 起始文章ID
            end_id: 结束文章ID（不包含）
            output_file: 输出文件路径
            delay: 请求间隔（秒）
        """
        logging.info(f"开始批量处理文章 ID 范围: {start_id} - {end_id-1}")
        
        success_count = 0
        total_count = end_id - start_id
        
        for article_id in range(start_id, end_id):
            time.sleep(delay)
            
            result = self.process_article(str(article_id))
            if result:
                success_count += 1
                print(f"\n[{success_count}/{total_count}] 标题: {result['title']}")
                print(f"作者: {result['author']}")
                print(f"摘要: {result['summary'][:100]}...")

                # 构建记录字典
                record = {
                    "id": result['id'],
                    "title": result['title'],
                    "author": result['author'],
                    "summary": result['summary'],
                    "url": result['url'],
                    "publish_time": result['publish_time'],
                    "fetch_time": result['fetch_time']
                }

                # 以追加模式写入 JSONL 文件
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            else:
                print(f"跳过文章 ID: {article_id}")
        
        logging.info(f"批量处理完成！成功处理 {success_count}/{total_count} 篇文章")

    def save_results(self, results: List[Dict[str, str]], filename: str = "sspai_articles.json"):
        """
        保存处理结果到JSON文件

        Args:
            results: 处理结果列表
            filename: 输出文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logging.info(f"结果已保存到 {filename}")

    def generate_markdown_report(self, results: List[Dict[str, str]], filename: str = "articles_report.md"):
        """
        生成Markdown格式的报告

        Args:
            results: 处理结果列表
            filename: 输出文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 少数派文章摘要报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"共处理文章：{len(results)} 篇\n\n")
            f.write("---\n\n")

            for article in results:
                f.write(f"## {article['title']}\n\n")
                f.write(f"**作者**：{article['author']}  \n")
                f.write(f"**链接**：{article['url']}  \n")
                f.write(f"**爬取时间**：{article['fetch_time']}  \n\n")
                f.write(f"**摘要**：\n\n{article['summary']}\n\n")
                f.write("---\n\n")

        logging.info(f"Markdown报告已保存到 {filename}")

    def analyze_html_structure(self, html_file_path: str) -> Dict[str, str]:
        """
        分析本地HTML文件的结构，用于调试和优化选择器

        Args:
            html_file_path: HTML文件路径

        Returns:
            分析结果字典
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # 分析可能的标题选择器
            title_candidates = []
            for selector in ['h1.title', 'h1', '.article-title', '[class*="title"]']:
                elements = soup.select(selector)
                if elements:
                    title_candidates.append({
                        'selector': selector,
                        'count': len(elements),
                        'first_text': elements[0].text.strip()[:50]
                    })

            # 分析可能的内容选择器
            content_candidates = []
            for selector in ['div.content', 'article', '.article-content', '[class*="content"]', 'main']:
                elements = soup.select(selector)
                if elements:
                    text_length = len(elements[0].get_text(strip=True))
                    content_candidates.append({
                        'selector': selector,
                        'count': len(elements),
                        'text_length': text_length
                    })

            # 分析可能的作者选择器
            author_candidates = []
            for selector in ['a.author-name', '.author', '[class*="author"]', 'span.author']:
                elements = soup.select(selector)
                if elements:
                    author_candidates.append({
                        'selector': selector,
                        'count': len(elements),
                        'first_text': elements[0].text.strip()
                    })

            analysis = {
                'title_candidates': title_candidates,
                'content_candidates': sorted(content_candidates, key=lambda x: x['text_length'], reverse=True),
                'author_candidates': author_candidates
            }

            # 打印分析结果
            print("=== HTML结构分析结果 ===\n")
            print("标题候选选择器:")
            for tc in title_candidates:
                print(f"  {tc['selector']}: 找到 {tc['count']} 个, 示例: {tc['first_text']}")

            print("\n内容候选选择器:")
            for cc in content_candidates[:5]:  # 只显示前5个
                print(f"  {cc['selector']}: 找到 {cc['count']} 个, 文本长度: {cc['text_length']}")

            print("\n作者候选选择器:")
            for ac in author_candidates:
                print(f"  {ac['selector']}: 找到 {ac['count']} 个, 文本: {ac['first_text']}")

            return analysis

        except Exception as e:
            logging.error(f"分析HTML文件失败: {e}")
            return {}


def main():
    """主函数示例"""
    # 创建爬虫实例（自动从环境变量读取API密钥）
    try:
        scraper = SSPaiScraper()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置环境变量 OPENAI_API_KEY")
        return

    # 示例1：处理单篇文章
    # article_id = "92777"
    # result = scraper.process_article(article_id)
    # if result:
    #     print(f"\n标题: {result['title']}")
    #     print(f"作者: {result['author']}")
    #     print(f"摘要: {result['summary']}")

    # 示例2：批量处理多篇文章
    # article_ids = ["92777", "92778", "92779"]  # 替换为实际的文章ID
    # results = scraper.process_multiple_articles(article_ids)
    # if results:
    #     scraper.save_results(results)
    #     scraper.generate_markdown_report(results)

    # 示例3：批量处理文章ID范围（大规模爬取）
    scraper.process_article_range(
        start_id=99999,
        end_id=100000,
        output_file="abstract_test.jsonl",
        delay=0.2
    )


if __name__ == "__main__":
    main()
