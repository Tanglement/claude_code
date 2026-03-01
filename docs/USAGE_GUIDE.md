# 股票信息系统 - 完整使用说明

## 一、项目概述

这是一个基于 Python + Flask 的股票信息系统，支持：
- 实时行情查询 (Tushare/AKShare)
- 用户管理 (注册/登录/自选股)
- 多智能体股票分析 (23个AI智能体)
- 推送通知
- 数据可视化

---

## 二、快速启动

### 2.1 环境准备

```bash
# 1. 克隆项目并进入目录
cd D:\claude-code-project

# 2. 创建虚拟环境 (推荐)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量 (可选)
# Windows
set OPENAI_API_KEY=your-api-key
set TUSHARE_TOKEN=your-tushare-token
```

### 2.2 初始化数据库

```bash
# MySQL 数据库
mysql -u root -p stock_db < sql/schema.sql
```

### 2.3 启动服务

```bash
# 启动后端
python -m src.api.app

# 访问前端
# 浏览器打开: http://localhost:5000
```

---

## 三、功能模块

### 3.1 用户功能

| 功能 | 说明 |
|------|------|
| 注册/登录 | 用户认证 |
| 自选股管理 | 添加/删除/查看自选股 |
| 推送设置 | 配置预警时间和类型 |

### 3.2 股票数据

| 功能 | 接口 | 说明 |
|------|------|------|
| 实时行情 | `/api/v1/stock/{symbol}/realtime` | 实时价格 |
| 历史K线 | `/api/v1/stock/{symbol}/history` | 历史走势 |
| 热门股票 | `/api/v1/stock/hot` | 热度排行 |
| 公司公告 | `/api/v1/stock/{symbol}/announcements` | 公告列表 |
| **股票搜索** | `/api/v1/stock?q=关键词` | **全A股模糊搜索** |

### 3.3 股票搜索功能

```bash
# 搜索示例
curl "http://localhost:5000/api/v1/stock?q=茅台"
curl "http://localhost:5000/api/v1/stock?q=600519"
curl "http://localhost:5000/api/v1/stock?q=海尔"
```

**搜索特性：**
- 支持按股票代码搜索（如 `600`、`0027`）
- 支持按股票名称搜索（如 `茅台`、`平安`）
- 优先使用Tushare，失败则自动切换到AKShare
- 内存缓存，首次加载后搜索速度极快
- 搜索5300+只A股股票

### 3.3 扩展数据接口

#### 财务数据
| 接口 | 说明 |
|------|------|
| `/api/v1/stock/{symbol}/financials` | 财务指标摘要 |
| `/api/v1/stock/{symbol}/income` | 利润表 |
| `/api/v1/stock/{symbol}/balance` | 资产负债表 |

#### 行业/概念
| 接口 | 说明 |
|------|------|
| `/api/v1/industry/list` | 行业板块列表 |
| `/api/v1/industry/{name}/stocks` | 行业成分股 |
| `/api/v1/concept/list` | 概念板块列表 |
| `/api/v1/concept/{name}/stocks` | 概念成分股 |

#### 研报/资金流
| 接口 | 说明 |
|------|------|
| `/api/v1/stock/{symbol}/reports` | 个股研报 |
| `/api/v1/stock/{symbol}/forecast` | 业绩预测 |
| `/api/v1/stock/{symbol}/fund-flow` | 资金流向 |
| `/api/v1/sector/fund-flow` | 板块资金流 |

#### 龙虎榜/融资融券
| 接口 | 说明 |
|------|------|
| `/api/v1/top/list` | 当日龙虎榜 |
| `/api/v1/stock/{symbol}/top-inst` | 机构明细 |
| `/api/v1/stock/{symbol}/margin` | 融资融券 |
| `/api/v1/margin/sx` | 融资融券余额 |

#### 宏观数据
| 接口 | 说明 |
|------|------|
| `/api/v1/macro/gdp` | GDP数据 |
| `/api/v1/macro/cpi` | CPI数据 |
| `/api/v1/macro/m2` | 货币供应量 |
| `/api/v1/macro/pmi` | PMI数据 |
| `/api/v1/macro/lpr` | LPR利率 |

#### 大宗交易/股东
| 接口 | 说明 |
|------|------|
| `/api/v1/block/trades` | 大宗交易 |
| `/api/v1/stock/{symbol}/holders` | 股东增减持 |

---

## 四、多智能体系统

### 4.1 团队架构 (23个智能体)

```
┌─────────────────────────────────────────────────────────────┐
│                    多智能体分析系统                           │
├─────────────────────────────────────────────────────────────┤
│  行业分析团队 (11个)                                         │
│  ├── 宏观分析师、基本面分析师、技术分析师                      │
│  ├── 内部信息分析师、研报分析师、地缘政治分析师                │
│  ├── 市场信息分析师、多头/空头研究员                          │
│  └── 核心矛盾研究员、行业秘书                                 │
├─────────────────────────────────────────────────────────────┤
│  资产配置团队 (2个)                                          │
│  ├── 配置交易员                                               │
│  └── 配置秘书                                                 │
├─────────────────────────────────────────────────────────────┤
│  风控团队 (3个)                                              │
│  ├── 风险扫描员                                               │
│  ├── 组合风险分析师                                           │
│  └── 风控秘书                                                 │
├─────────────────────────────────────────────────────────────┤
│  个股精选团队 (5个)                                          │
│  ├── 个股筛选器                                               │
│  ├── 财务侦探、估值专家                                        │
│  ├── Alpha研究员                                              │
│  └── 个股风控师                                               │
├─────────────────────────────────────────────────────────────┤
│  交易执行团队 (1个)                                          │
│  └── 交易执行员                                               │
├─────────────────────────────────────────────────────────────┤
│  最终决策 (1个)                                              │
│  └── 最终决策者                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 智能体API

| 接口 | 说明 |
|------|------|
| `/api/v1/agent/teams` | 获取所有智能体列表 |
| `/api/v1/agent/team-details` | 获取团队详细信息 |
| `/api/v1/agent/prompt/{name}` | 获取智能体提示词 |
| `/api/v1/agent/analyze/{symbol}` | 运行股票分析 |

### 4.3 前端可视化

访问路径: `导航栏 → 智能体分析`

1. **团队概览**: 查看6个团队卡片
2. **智能体列表**: 选择团队，查看智能体
3. **提示词编辑**: 点击编辑，修改AI提示词

---

## 五、使用示例

### 5.1 命令行测试API

```bash
# 1. 启动服务
python -m src.api.app

# 2. 测试接口 (另开终端)

# 热门股票
curl http://localhost:5000/api/v1/stock/hot?limit=10

# 股票详情
curl http://localhost:5000/api/v1/stock/002738/realtime

# 行业列表
curl http://localhost:5000/api/v1/industry/list

# 财务数据
curl http://localhost:5000/api/v1/stock/002738/financials

# 宏观数据
curl http://localhost:5000/api/v1/macro/gdp

# 多智能体分析
curl http://localhost:5000/api/v1/agent/analyze/002738?use_mock=true
```

### 5.2 Python代码调用

```python
from src.services.data_provider import (
    MarketDataProvider,
    FinancialDataProvider,
    IndustryDataProvider,
    FundFlowProvider,
    MacroDataProvider
)

# 实时行情
df = MarketDataProvider.get_stock_daily('002738')

# 财务数据
df = FinancialDataProvider.get_financial_summary('002738')

# 行业列表
df = IndustryDataProvider.get_industry_list()

# 资金流向
df = FundFlowProvider.get_fund_flow('002738')

# GDP数据
df = MacroDataProvider.get_gdp_data()
```

---

## 六、配置说明

### 6.1 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 无 |
| `TUSHARE_TOKEN` | Tushare Token | 已配置 |
| `FLASK_ENV` | 运行环境 | development |
| `DATABASE_URL` | 数据库连接 | localhost:3306 |

### 6.2 配置文件

- `config/prompts.py` - 智能体提示词配置
- `config/llm.py` - LLM配置

---

## 七、开发指南

### 7.1 项目结构

```
src/
├── api/              # API路由
│   ├── app.py       # Flask应用
│   └── routes/      # 路由模块
├── agents/          # 智能体
│   ├── base.py      # 基类
│   ├── multi_agent.py # 多智能体协调器
│   └── ...
├── services/        # 业务服务
│   ├── data_provider.py   # 数据提供
│   ├── stock_service.py   # 股票服务
│   └── news_service.py    # 新闻服务
├── repositories/    # 数据访问
├── models/          # 数据模型
└── utils/          # 工具类

frontend/
└── index.html      # 单页应用

config/
└── prompts.py      # 提示词配置
```

### 7.2 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行特定测试
pytest tests/unit/test_stock_repo.py
```

---

## 八、常见问题

### Q1: 接口返回空数据?
> AKShare可能有访问限制，建议稍后重试或配置Tushare

### Q2: 智能体分析失败?
> 检查OPENAI_API_KEY配置，或使用use_mock=true测试

### Q3: 前端页面空白?
> 确保已启动Flask服务，访问 http://localhost:5000

### Q4: 数据库连接失败?
> 检查MySQL服务是否启动，配置文件是否正确

---

## 九、版本信息

- 当前版本: 1.0.0
- 更新日期: 2026-02-28
- Python版本: 3.8+
- 依赖框架: Flask, Bootstrap 5, ECharts
