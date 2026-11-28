# Excel 数据分析助手

基于 Python、Pandas、Streamlit 和大语言模型 API 开发的智能数据分析工具，支持 Excel/CSV 文件上传、数据质量检测、数据清洗、统计分析、数据可视化、AI 智能问答和 PDF 报告导出。

## 项目功能

- 支持 CSV、Excel 文件上传
- 自动展示数据基本信息
- 检测缺失值、重复数据和字段类型
- 支持多种缺失值处理方式
- 支持删除重复数据
- 生成数值字段描述性统计
- 使用 Plotly 生成交互式数据图表
- 接入通义千问 API，实现自然语言数据问答
- 支持清洗后数据 CSV 导出
- 自动生成 PDF 数据分析报告

## 技术栈

| 技术 | 用途 |
| --- | --- |
| Python | 核心开发语言 |
| Pandas | 数据处理与分析 |
| Streamlit | Web 应用界面 |
| Plotly | 交互式数据可视化 |
| OpenAI SDK | 大模型 API 调用 |
| 通义千问 | AI 数据分析问答 |
| ReportLab | PDF 报告生成 |
| Pytest | 自动化测试 |
| Ruff | 代码质量检查 |

## 项目结构

```text
ai-excel-analyst/
├── app.py
├── report_utils.py
├── test_report.py
├── test_ai.py
├── sales_data.csv
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── .venv/
```

## 环境要求

- Python 3.10+
- pip

## 安装与运行

克隆项目：

```bash
git clone https://github.com/你的GitHub用户名/ai-excel-analyst.git
cd ai-excel-analyst
```

创建虚拟环境：

```bash
python -m venv .venv
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动项目：

```bash
streamlit run app.py
```

浏览器访问：

```text
http://localhost:8501
```

## AI 模型配置

项目通过阿里云百炼兼容接口调用通义千问模型。

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=你的API_KEY
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
```

请根据 API Key 创建地域选择正确的接口地址。

注意：`.env` 文件包含个人密钥，不要上传到 GitHub。

## 自动化测试

运行测试：

```bash
python -m pytest -v
```

## 代码质量检查

```bash
python -m ruff check .
```

## 项目截图

运行项目后，可以将应用界面截图放在 `screenshots/` 目录，并在这里展示：

```markdown
![数据分析界面](screenshots/dashboard.png)
```

## 后续优化方向

- 增加更多数据清洗策略
- 支持多工作表 Excel 分析
- 增加 AI 自动生成分析结论
- 增加更多图表类型
- 优化大型数据文件处理性能
- 增加更全面的业务逻辑自动化测试

## License

MIT
