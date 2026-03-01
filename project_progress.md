# 智能投研决策系统 - 项目进度

> 基于 Multi-Agent 架构的 AI 量化交易系统
> 更新于 2026-02-28

---

## 1. 系统架构 (Layered Architecture)

| 层级 | 名称 | 状态 | 说明 |
|------|------|------|------|
| **L1** | 基础设施层 | ✅ 已完成 | 爬虫、存储、调度 |
| **L2** | 量化计算层 | ✅ 已完成 | 技术指标、因子计算 |
| **L3** | 智能分析层 | ✅ 已完成 | LLM分析、新闻/研报 |
| **L4** | 决策代理层 | ✅ 已完成 | 决策调度、风控、交易 |

---

## 2. 任务清单

### 阶段一：数据基建夯实 (Infrastructure) ✅
- [x] 搭建 Flask + MySQL + MongoDB 基础框架
- [x] 实现股票实时行情爬取
- [x] 实现新闻/公告爬取
- [x] REST API 接口 (17个)

### 阶段二：量化因子引擎 (Quant Engine) - L2 ✅
- [x] 实现 `src/quant/indicators.py` - MA/EMA/MACD/RSI/KDJ/布林带
- [x] 实现 `src/quant/factors.py` - 资金流/波动率/动量/成交量因子

### 阶段三：AI 分析师 (Analyst Agent) - L3 ✅
- [x] 实现 `src/agents/base.py` - Agent基类/LLM客户端/提示词模板
- [x] 实现 `src/agents/news_analyst.py` - 新闻情感分析
- [x] 实现 `src/agents/report_summarizer.py` - 研报摘要

### 阶段四：多智能体协作 (Multi-Agent Loop) - L4 ✅
- [x] 实现 `src/decision/decision_maker.py` - 决策调度器
- [x] 实现 `src/decision/risk_control.py` - 风控模块
- [x] 实现 `src/decision/trade_executor.py` - 交易执行

### 阶段五：环境配置 ✅
- [x] 安装依赖 `pip install -r requirements.txt`
- [x] 单元测试通过率 38/51 (74%)

---

## 3. 核心代码结构

```
src/
├── quant/                    # L2 量化计算层 ✅
│   ├── indicators.py         # MACD, RSI, KDJ, MA, 布林带
│   └── factors.py           # 资金流, 波动率, 动量因子
│
├── agents/                   # L3 智能分析层 ✅
│   ├── base.py             # Agent基类, LLM客户端
│   ├── news_analyst.py    # 新闻情感分析
│   └── report_summarizer.py # 研报摘要
│
└── decision/                 # L4 决策代理层 ✅
    ├── decision_maker.py    # 决策调度器
    ├── risk_control.py      # 风控模块
    └── trade_executor.py    # 交易执行
```

---

## 4. 决策流程

```
1. Trigger: 定时任务 / 重大新闻
2. Data Agent: 拉取行情 + 舆情
3. Quant Agent: 计算技术指标 (RSI/MACD/资金流)
4. Analyst Agent: LLM分析新闻情感
5. Decision Maker: 综合打分 > 阈值?
6. Risk Control: 检查仓位/回撤限制
7. Trade Executor: 写入 trade_orders 表
```

---

## 5. 下一步优化

- [ ] 接入真实 LLM API (OpenAI/Claude/DeepSeek)
- [ ] 向量化处理 (ChromaDB + RAG)
- [ ] 回测系统 (Backtrader)
- [ ] 实盘接口对接

---

*由 Claude Code 自动维护*
