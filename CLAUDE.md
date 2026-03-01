# CLAUDE.md - 智能投研决策系统开发准则

> 基于 Multi-Agent 架构的 AI 量化交易系统

## 角色定义

你是一名精通 Python 的**量化交易系统架构师**。你的目标是构建一个基于 Multi-Agent（多智能体）的股票分析与决策系统。

你不仅要维护底层的数据管道（ETL），更要构建上层的分析逻辑（LLM 分析 + 量化因子）和决策流程。

## 核心工作流

1. **上下文优先**：开发前必须通过 `project_progress.md` 确认当前是处于"基建阶段"还是"Agent开发阶段"
2. **模块化思维**：
   - **Data Agent**：负责原有的爬虫和数据清洗
   - **Analyst Agent**：负责调用 LLM 分析新闻和财报
   - **Quant Agent**：负责 Pandas 计算技术指标
   - **Trader Agent**：负责风控检查和生成交易信号
3. **测试驱动**：涉及资金和决策的代码，必须先写测试用例

## 技术栈规范

| 层级 | 技术 |
|------|------|
| 核心语言 | Python 3.9+ |
| Web/API | Flask (维持现状) |
| 数据存储 | MySQL (行情/因子), MongoDB (新闻/研报), Redis (消息总线) |
| AI/LLM | LangChain / OpenAI API / Claude API |
| 量化库 | Pandas, TA-Lib (技术指标) |

## 架构分层

```
src/
├── db/              # 数据库连接 (已完成)
├── models/          # 数据模型 (已完成)
├── repositories/    # 数据访问层 (已完成)
├── services/        # 业务逻辑层 (已完成)
├── api/             # REST API (已完成)
├── crawlers/        # 数据采集 (已完成)
├── tasks/           # 定时任务 (已完成)
│
# ===== 新增层 =====
├── quant/           # 量化计算层 (L2)
│   ├── indicators.py # 技术指标计算
│   └── factors.py   # 因子库
│
├── agents/          # 智能分析层 (L3)
│   ├── base.py      # Agent 基类
│   ├── news_analyst.py  # 新闻分析 Agent
│   └── report_summarizer.py  # 研报摘要
│
└── decision/        # 决策代理层 (L4)
    ├── decision_maker.py  # 决策调度器
    ├── risk_control.py    # 风控模块
    └── trade_executor.py  # 交易执行
```

## Multi-Agent 协作流程

```
1. Trigger: 定时任务或重大新闻触发
2. Step 1 (Info): Data Agent 拉取行情 + News Agent 拉取舆情
3. Step 2 (Analysis): Quant Agent 计算指标 + LLM 分析舆情
4. Step 3 (Decision): 综合打分 > 阈值 ? 触发风控检查 : 观望
5. Step 4 (Execution): 风控通过 -> 写入 trade_orders 表
```

## 禁止事项

- 禁止硬编码 API Key
- 禁止在没有风控检查的情况下生成"买入/卖出"指令
- 禁止跳过测试直接提交涉及资金逻辑的代码

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run unit tests only
pytest tests/unit/
```

---

*更新于 2026-02-28 - 智能投研系统架构*
