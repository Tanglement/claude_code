# 智能投研决策系统 (AI Investment Research System)

基于 Multi-Agent 架构的 AI 量化交易系统

## 项目简介

本系统是一个智能股票分析与决策平台，采用 Multi-Agent（多智能体）架构，集成了：
- **数据采集**：Tushare + AKShare 双数据源
- **量化分析**：技术指标计算、因子库
- **LLM 分析**：新闻舆情分析、财报摘要
- **决策引擎**：风控检查、交易信号生成

## 技术栈

| 层级 | 技术 |
|------|------|
| 核心语言 | Python 3.9+ |
| Web 框架 | Flask |
| 数据存储 | MySQL, MongoDB, Redis |
| AI/LLM | LangChain, OpenAI API |
| 量化库 | Pandas, TA-Lib |
| 前端 | Bootstrap 5 + ECharts |

## 项目结构

```
src/
├── api/              # REST API 路由
├── db/               # 数据库连接
├── models/           # 数据模型
├── repositories/     # 数据访问层
├── services/         # 业务逻辑层
├── crawlers/         # 数据采集
├── quant/            # 量化计算层
├── agents/           # 智能分析层
├── decision/         # 决策代理层
└── utils/            # 工具类

frontend/             # 前端页面
sql/                  # 数据库脚本
docs/                 # 项目文档
tests/                # 测试用例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

确保 MySQL 已安装并运行，配置文件位于 `src/utils/config.py`

### 3. 启动服务

```bash
python -m src.api.app
```

访问 http://localhost:5000

### 4. 运行测试

```bash
pytest
```

## 功能特性

- [x] 用户认证与权限管理
- [x] 自选股管理
- [x] 实时行情查询
- [x] 历史K线数据
- [x] 股票基本信息查询
- [x] 行业/概念板块查询
- [x] 资金流向数据
- [x] 融资融券数据
- [x] 龙虎榜数据
- [x] 股票公告查询
- [x] 财务报表查询
- [x] 全A股模糊搜索
- [x] 多智能体可视化

## API 文档

详见 `docs/` 目录下的文档：
- `docs/PRD.md` - 产品需求文档
- `docs/ARCHITECTURE.md` - 架构设计文档
- `docs/USAGE_GUIDE.md` - 使用指南

## License

MIT
