# 股票分析看板项目文档

## 项目概述

这是一个自动化股票分析报告生成项目，使用 AI（豆包模型）对每日涨停、断板、炸板股票进行分析，并通过 MkDocs 构建成静态文档网站进行展示。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python | 主要开发语言 |
| akshare | 获取股票数据 |
| chinese-calendar | 处理中国交易日历 |
| pandas | 数据处理 |
| python-dotenv | 环境变量管理 |
| volcengine-python-sdk | 豆包 AI 模型调用 |
| mkdocs + mkdocs-material | 文档网站构建 |
| GitHub Actions | 自动化 CI/CD |

## 项目结构

```
stock_review/
├── analyzers/              # 股票分析器模块
│   ├── base_analyzer.py    # 分析器基类
│   ├── zt_analyzer.py      # 涨停股票分析器
│   ├── db_analyzer.py      # 断板股票分析器
│   └── zb_analyzer.py      # 炸板股票分析器
├── reporters/              # 报告生成器模块
│   ├── base_reporter.py    # 报告生成器基类
│   ├── zt_reporter.py      # 涨停报告生成器
│   ├── db_reporter.py      # 断板报告生成器
│   └── zb_reporter.py      # 炸板报告生成器
├── utils/                  # 工具模块
│   ├── stock_utils.py      # 股票数据获取工具
│   ├── doubao_utils.py     # 豆包 API 调用工具
│   ├── log_utils.py        # 日志工具
│   ├── trading_date_utils.py # 交易日历工具
│   └── report_nav_updater.py # 导航更新工具
├── docs/                   # MkDocs 文档源文件
├── logs/                   # 运行日志目录
├── site/                   # 构建后的静态网站
├── tests/                  # 测试文件
├── scripts/                # 脚本文件
├── .github/workflows/      # GitHub Actions 工作流
│   └── daily-analyze.yml   # 每日分析和部署 workflow
├── config/                 # 配置目录
│   └── .env                # 环境变量配置
├── daily_analyze_stock.py  # 主分析脚本
├── auto_analyze.ps1        # PowerShell 自动执行脚本（Windows）
├── mkdocs.yml              # MkDocs 配置
├── requirements.txt        # 依赖列表（版本固定）
├── AGENTS.md               # 本文档
└── Notes.md                # 开发笔记
```

## 核心功能模块

### 1. 股票数据获取 (utils/stock_utils.py)
- `get_zt_stock(date)`: 获取指定日期的涨停股票（已过滤ST/科创/北交所）
- `get_zb_stock(date)`: 获取指定日期的炸板股票
- `get_yes_zt_today_no_zt(yes_date, today_date)`: 获取断板股票（昨日涨停今日未涨停）
- `filter_main_board(df)`: 过滤只保留沪深主板股票（60/000/001开头）

### 2. 分析器模块 (analyzers/)
- `BaseStockAnalyzer`: 抽象基类，提供统一的分析接口
- 支持批量分析，使用上下文缓存优化多轮对话
- 集成联网搜索工具增强分析准确性

### 3. 报告生成器模块 (reporters/)
- `BaseReporter`: 抽象基类，提供统一的报告生成接口
- 自动按年份/月份组织报告文件
- 自动更新 mkdocs.yml 导航配置

### 4. 豆包 AI 集成 (utils/doubao_utils.py)
- `DoubaoClient`: 封装豆包 API 调用
- 支持 text 对话、多模态（图片理解）、流式响应
- 内置联网搜索收费统计
- 单例模式管理全局客户端

### 5. 日志系统 (utils/log_utils.py)
- 同时输出到控制台和文件
- 日志文件按日期存储在 `logs/` 目录
- UTF-8 编码，中文正常显示

## 主要工作流程

### 本地流程
1. **数据获取**: 使用 akshare 从东方财富网获取涨停/炸板股票数据
2. **AI 分析**: 通过豆包模型对股票进行分析，包含：
   - 赛道分类统计
   - 未来想象空间评级
   - 个股详细分析（题材、业绩、资金、政策层面）
   - 逻辑分析与风险提示
3. **报告生成**: 按照预设模板生成 Markdown 格式报告
4. **网站更新**: 自动更新 mkdocs.yml 导航
5. **部署**: 本地执行 `mkdocs gh-deploy` 部署到 GitHub Pages

### GitHub Actions 自动流程
1. **定时触发**: 每个工作日 17:00（北京时间）自动运行
2. **运行分析**: 执行 `daily_analyze_stock.py` 生成报告
3. **提交报告**: 将 `docs/` 目录提交到 main 分支
4. **自动部署**: 执行 `mkdocs gh-deploy` 部署到 GitHub Pages

## 使用方法

### 运行每日分析
```powershell
python daily_analyze_stock.py              # 分析最近交易日
python daily_analyze_stock.py --today      # 分析今天的数据
python daily_analyze_stock.py --date 20260522  # 分析指定日期
```

### MkDocs 命令
```powershell
mkdocs serve      # 本地预览网站
mkdocs build      # 构建静态网站
mkdocs gh-deploy  # 部署到 GitHub Pages
```

### PowerShell 自动执行脚本 (Windows)
```powershell
# 查看帮助
.\auto_analyze.ps1 -Help

# 立即运行一次
.\auto_analyze.ps1 -RunNow

# 设置定时任务（需要管理员权限）
.\auto_analyze.ps1 -Setup

# 删除定时任务
.\auto_analyze.ps1 -Remove
```

### GitHub Actions 配置
1. 在仓库 Settings → Secrets and variables → Actions 中添加：
   - `ARK_API_KEY`: 豆包 API Key
   - `PERSONAL_ACCESS_TOKEN`: GitHub 个人访问令牌（需要 repo 权限）
2. workflow 会在每个工作日 17:00 自动运行

## 配置要求

需要在 `config/.env` 文件中配置：
- `ARK_API_KEY`: 豆包 API Key（必需）
- `ARK_BASE_URL`: API 基础 URL（可选）
- `ARK_DEFAULT_MODEL`: 默认模型（可选）

## 依赖说明 (requirements.txt)

| 依赖 | 版本 | 用途 |
|------|------|------|
| akshare | 1.18.60 | 股票数据获取 |
| pandas | 3.0.2 | 数据处理 |
| chinese_calendar | 1.11.0 | 交易日历 |
| python-dotenv | 1.2.2 | 配置管理 |
| volcengine-python-sdk | 5.0.26 | 豆包 API |
| mkdocs | 1.6.1 | 文档网站 |
| mkdocs-material | 9.7.6 | Material 主题 |

## 报告类型

1. **zt_report**: 涨停股票分析报告
2. **db_report**: 断板股票分析报告
3. **zb_report**: 炸板股票分析报告

## 项目特点

- 面向对象设计，分析器和报告生成器易于扩展
- 自动化程度高，从数据获取到网站部署一条龙
- 支持中国交易日历，自动跳过非交易日
- 使用 Material Design 主题，界面美观
- GitHub Actions 自动化，无需本地电脑值守
- 完整的日志系统，方便排查问题
- 版本固定的依赖，保证运行环境一致性
