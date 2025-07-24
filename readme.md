
## 功能特性

- 🕸️ **文章抓取**：支持通过文章ID抓取少数派文章内容
- 🤖 **AI摘要**：使用OpenAI GPT-4o-mini生成高质量文章摘要
- 📊 **批量处理**：支持批量处理多篇文章和范围爬取
- 💾 **多种输出格式**：支持JSON、JSONL和Markdown格式输出
- 🚀 **大规模爬取**：支持指定ID范围的批量爬取（如90001-100000）
- 📈 **实时保存**：边爬取边保存，避免数据丢失
- 🛠️ **调试工具**：内置HTML结构分析工具
- 📝 **详细日志**：完整的处理日志记录和进度显示

## 安装

### 环境要求

- Python 3.7+
- OpenAI API密钥

### 克隆项目

```bash
git clone https://github.com/yourusername/sspai-scraper.git
cd sspai-scraper
```

### 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 设置OpenAI API密钥

有两种方式设置API密钥：

**方式1：环境变量（推荐）**

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

或在Windows中：

```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

**方式2：直接传入构造函数**

```python
scraper = SSPaiScraper(openai_api_key="your-openai-api-key-here")
```

## 使用方法

### 基本用法

```python
from sspai_scraper import SSPaiScraper

# 创建爬虫实例
scraper = SSPaiScraper()

# 处理单篇文章
article_id = "92777"
result = scraper.process_article(article_id)

if result:
    print(f"标题: {result['title']}")
    print(f"作者: {result['author']}")
    print(f"摘要: {result['summary']}")
```

### 批量处理

```python
# 方式1：批量处理指定文章ID列表
article_ids = ["92777", "92778", "92779"]
results = scraper.process_multiple_articles(article_ids, delay=2.0)

# 保存结果
scraper.save_results(results, "articles.json")
scraper.generate_markdown_report(results, "articles_report.md")

# 方式2：大规模范围爬取（推荐用于大量数据采集）
scraper.process_article_range(
    start_id=90001,
    end_id=100000,
    output_file="abstract.jsonl",
    delay=0.2
)
```

### 命令行使用

```bash
python main.py
```

## API参考

### SSPaiScraper类

#### 初始化

```python
SSPaiScraper(openai_api_key: Optional[str] = None)
```

- `openai_api_key`: OpenAI API密钥（可选，默认从环境变量读取）

#### 主要方法

- `fetch_article(article_id: str)`: 抓取指定ID的文章
- `generate_summary(article: Dict, max_length: int = 200)`: 生成文章摘要
- `process_article(article_id: str)`: 处理单篇文章（包含抓取和摘要生成）
- `process_multiple_articles(article_ids: List[str], delay: float = 2.0)`: 批量处理文章
- `process_article_range(start_id: int, end_id: int, output_file: str, delay: float = 0.2)`: 范围爬取（大规模采集）
- `save_results(results: List[Dict], filename: str)`: 保存结果为JSON格式
- `generate_markdown_report(results: List[Dict], filename: str)`: 生成Markdown报告

## 输出格式

### JSON/JSONL格式

```json
{
  "id": "92777",
  "url": "https://sspai.com/post/92777",
  "title": "文章标题",
  "author": "作者名",
  "content": "文章内容...",
  "publish_time": "发布时间",
  "fetch_time": "2024-01-01T12:00:00",
  "summary": "AI生成的摘要..."
}
```

### JSONL格式（大规模数据采集）

JSONL（JSON Lines）格式特别适合大规模数据采集，每行一个JSON对象：

```jsonl
{"id": "90001", "title": "文章1", "author": "作者1", "summary": "摘要1..."}
{"id": "90002", "title": "文章2", "author": "作者2", "summary": "摘要2..."}
{"id": "90003", "title": "文章3", "author": "作者3", "summary": "摘要3..."}
```

优势：
- 📈 **流式处理**：边爬取边保存，不占用大量内存
- 🔄 **断点续传**：程序中断后可以继续处理
- 📊 **数据分析友好**：便于后续数据处理和分析

### Markdown报告

生成包含所有文章摘要的格式化Markdown报告，方便阅读和分享。

## 使用场景

### 场景1：研究分析
```python
# 分析特定时期的文章内容
scraper.process_article_range(95000, 96000, "research_data.jsonl")
```

### 场景2：内容监控
```python
# 定期抓取最新文章
latest_articles = scraper.process_multiple_articles(["99990", "99991", "99992"])
```

### 场景3：数据集构建
```python
# 构建大规模文章摘要数据集
scraper.process_article_range(90001, 100000, "dataset.jsonl", delay=0.2)
```

## 性能与优化

- **内存优化**：使用JSONL格式流式保存，避免内存溢出
- **请求控制**：支持自定义请求间隔，避免被反爬虫限制
- **错误处理**：自动跳过失败的文章，继续处理后续内容
- **进度显示**：实时显示处理进度和成功率

## 注意事项

### 使用建议

- **合理设置延迟**：建议设置0.2-2秒的请求间隔，避免对服务器造成压力
- **分批处理**：大规模爬取时建议分批进行，如每次处理1000-5000篇文章
- **监控API费用**：OpenAI API按token计费，大规模使用前请估算费用
- **遵守robots.txt**：请遵守少数派网站的robots.txt和使用条款

### 大规模爬取最佳实践

```python
# 推荐的大规模爬取配置
scraper.process_article_range(
    start_id=90001,
    end_id=95000,        # 分批处理，避免一次性处理过多
    output_file="batch1.jsonl",
    delay=0.5            # 适中的延迟，平衡效率和稳定性
)
```

### 常见问题

**Q: 如何获取文章ID？**
A: 文章ID是少数派文章URL中的数字部分，例如 `https://sspai.com/post/92777` 中的 `92777`

**Q: 为什么某些文章抓取失败？**
A: 可能的原因包括：
- 文章不存在或已被删除
- 网络连接问题
- 网站结构发生变化
- 反爬虫机制

**Q: 如何自定义摘要长度？**
A: 在调用 `generate_summary()` 时传入 `max_length` 参数

## 开发

### 项目结构

```
sspai-scraper/
├── sspai_scraper.py    # 主要代码
├── main.py             # 使用示例和入口点
├── requirements.txt    # 依赖列表
├── README.md          # 项目说明
├── LICENSE            # 许可证
├── .gitignore         # Git忽略文件
├── abstract.jsonl     # 输出的数据文件（运行后生成）
└── .github/
    └── workflows/
        └── ci.yml     # CI/CD配置
```

### 调试工具

使用内置的HTML结构分析工具来调试和优化选择器：

```python
# 分析本地保存的HTML文件
analysis = scraper.analyze_html_structure("sample.html")
```

## 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 免责声明

本工具仅供学习和研究使用。使用者应当：

- 遵守相关网站的使用条款和robots.txt
- 尊重内容创作者的版权
- 合理使用，避免对目标网站造成过大负担
- 承担使用本工具的一切责任

作者不对使用本工具产生的任何后果承担责任。

## 更新日志

### v1.0.0
- ✨ 初始版本发布
- 🕸️ 支持基本的文章抓取和摘要生成功能
- 📊 支持批量处理和多种输出格式
- 🚀 新增大规模范围爬取功能
- 💾 支持JSONL格式实时保存
- 📈 添加进度显示和统计信息
- 🤖 集成OpenAI GPT-4o-mini模型
- 🛡️ 完善错误处理和日志记录

## 未来计划

- [ ] 数据分析及私人化内容摘要
- [ ] 支持更多摘要模型（如本地模型）
- [ ] 添加数据去重和清洗功能

## 技术架构

### 核心组件

1. **爬虫引擎**：基于requests和BeautifulSoup
2. **摘要生成**：OpenAI API集成，支持备选策略
3. **数据管理**：多格式输出，流式处理
4. **错误处理**：完善的异常处理和重试机制

---

**Q: 如何进行大规模数据采集？**
A: 使用 `process_article_range()` 方法，设置合适的ID范围和延迟。推荐分批处理，每批1000-5000篇文章。

**Q: 如何控制API费用？**
A: 
- 使用 `gpt-4o-mini` 模型（更经济）
- 限制输入内容长度（代码中限制为3000字符）
- 设置合理的 `max_tokens` 参数
- 考虑使用简单摘要作为备选方案

**Q: 程序中断后如何继续？**
A: JSONL格式支持断点续传，检查已有文件的最后ID，从该位置继续爬取。

**Q: 如何提高爬取成功率？**
A: 
- 适当增加请求延迟
- 检查网络连接
- 更新User-Agent和请求头
- 使用代理服务器（如需要）# SSPai Scraper

一个用于抓取少数派（sspai.com）文章并生成AI摘要的Python工具，支持大规模数据采集和智能摘要生成。

如果这个项目对您有帮助，请给个⭐️！