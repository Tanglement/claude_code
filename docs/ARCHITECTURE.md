# 股票信息收集系统 - 项目架构文档

> 更新时间: 2026-02-28

---

## 一、项目架构总览

```
stock-information-system/
├── src/                          # 源代码目录
│   ├── db/                       # 数据库连接层
│   │   ├── mysql_db.py          # MySQL 连接管理
│   │   ├── mongodb.py           # MongoDB 连接管理
│   │   ├── redis_db.py          # Redis 连接管理
│   │   └── database.py          # 数据库初始化入口
│   │
│   ├── models/                   # 数据模型层
│   │   ├── exceptions.py        # 自定义异常类
│   │   ├── stock.py            # 股票数据模型
│   │   ├── user.py             # 用户数据模型
│   │   ├── news.py             # 新闻/公告数据模型
│   │   └── models.py           # 模型导出入口
│   │
│   ├── repositories/            # 数据访问层（仓储层）
│   │   ├── stock_repo.py       # 股票数据访问
│   │   ├── user_repo.py        # 用户数据访问
│   │   ├── news_repo.py        # 新闻数据访问
│   │   └── repositories.py     # 仓储导出入口
│   │
│   ├── services/                # 业务逻辑层（待补充）
│   │
│   ├── api/                    # API 接口层（待补充）
│   │
│   ├── crawlers/               # 数据采集层（待补充）
│   │
│   ├── tasks/                  # 定时任务层（待补充）
│   │
│   └── utils/                  # 工具模块
│       ├── config.py           # 配置管理
│       └── logger.py           # 日志配置
│
├── tests/                       # 测试目录
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── docs/                        # 文档目录
│   ├── PRD.md                  # 需求文档
│   ├── SDD.md                  # 设计文档
│   └── TDD.md                  # 测试文档
│
├── requirements.txt             # 依赖清单
└── README.md                    # 项目说明
```

---

## 二、架构完整性评估

### ✅ 已完成模块

| 模块 | 状态 | 说明 |
|------|------|------|
| db/ | ✅ 完成 | MySQL、MongoDB、Redis 连接管理 |
| models/ | ✅ 完成 | 异常类、股票/用户/新闻模型 |
| repositories/ | ✅ 完成 | 股票/用户/新闻数据访问层 |
| utils/ | ✅ 完成 | 配置管理、日志工具 |
| services/ | ✅ 完成 | 业务逻辑层（Stock/User/News服务） |
| api/ | ✅ 完成 | REST API 接口层（Flask蓝图） |
| crawlers/ | ✅ 完成 | 数据采集层（行情/新闻/公告） |
| tasks/ | ✅ 完成 | 定时任务调度层（APScheduler） |
| tests/unit/ | ✅ 完成 | 单元测试（含Mock） |

### ✅ 全部模块已完成

---

## 三、各模块功能说明

### 1. db/ - 数据库连接层

**职责**: 统一管理数据库连接，提供连接池和基础操作封装

| 文件 | 功能 |
|------|------|
| `mysql_db.py` | MySQL 连接管理、CRUD 操作封装、上下文管理器支持 |
| `mongodb.py` | MongoDB 连接管理、文档操作封装 |
| `redis_db.py` | Redis 连接管理、缓存操作、Hash/List/ZSet 操作 |
| `database.py` | 统一初始化入口、批量关闭连接 |

---

### 2. models/ - 数据模型层

**职责**: 定义数据结构、异常类型、API 数据传输格式

| 文件 | 功能 |
|------|------|
| `exceptions.py` | 自定义异常：StockNotFoundError, UserNotFoundError, AuthenticationError 等 |
| `stock.py` | StockBasic, StockRealtime, StockHistory, StockQuote 数据模型 |
| `user.py` | User, UserHolding, UserSession 数据模型 |
| `news.py` | News, Announcement, Comment, Log 数据模型 |
| `models.py` | 模块导出入口 |

---

### 3. repositories/ - 数据访问层

**职责**: 封装数据库操作，提供增删改查接口

| 文件 | 功能 |
|------|------|
| `stock_repo.py` | 股票基本信息、实时行情、历史行情的增删改查 |
| `user_repo.py` | 用户注册/登录、持仓管理、密码验证 |
| `news_repo.py` | 新闻、公告、评论、日志的 CRUD 操作 |

---

### 4. utils/ - 工具模块

**职责**: 提供配置管理、日志等基础设施

| 文件 | 功能 |
|------|------|
| `config.py` | 配置类（DatabaseConfig, AppConfig），支持环境变量加载 |
| `logger.py` | 日志配置，支持文件轮转、控制台输出 |

---

## 四、各模块详细说明

### 4.1 services/ - 业务逻辑层

```
src/services/
├── __init__.py
├── services.py         # 模块导出
├── stock_service.py    # 股票业务逻辑
├── user_service.py     # 用户业务逻辑
└── news_service.py     # 新闻业务逻辑
```

**职责**:
- 封装仓储层，提供业务能力
- 数据校验和转换
- 业务规则处理

**已完成功能**:
- StockService: 行情查询、历史数据、业务逻辑封装
- UserService: 用户注册/登录/JWT Token/持仓管理
- NewsService: 新闻/公告/评论 CRUD

---

### 4.2 api/ - API 接口层

```
src/api/
├── __init__.py
├── app.py              # Flask 应用工厂
├── routes/
│   ├── __init__.py
│   ├── stock_routes.py  # 股票相关接口
│   ├── user_routes.py  # 用户相关接口
│   └── news_routes.py  # 新闻相关接口
└── middleware/
    ├── __init__.py
    └── auth.py         # 认证中间件
```

**职责**:
- RESTful API 接口定义
- 请求参数校验
- 响应格式统一封装
- 路由管理

**已完成接口** (根据 PRD):
```
GET    /api/v1/stock/{symbol}/realtime   # 实时行情
GET    /api/v1/stock/{symbol}/history   # 历史行情
GET    /api/v1/stock/hot                # 热门股票
GET    /api/v1/news/latest              # 最新新闻
POST   /api/v1/user/register            # 用户注册
POST   /api/v1/user/login               # 用户登录
GET    /api/v1/user/holdings            # 用户持仓
```

---

### 4.3 crawlers/ - 数据采集层

```
src/crawlers/
├── __init__.py
├── crawlers.py          # 模块导出
├── base.py              # 爬虫基类（请求重试、UA轮换）
├── quote_crawler.py     # 行情数据采集（新浪/东财）
├── news_crawler.py      # 新闻数据采集（新浪/东财）
└── announcement_crawler.py  # 公告数据采集（巨潮资讯）
```

**已完成功能**:
- BaseCrawler: 请求重试、User-Agent轮换、代理支持
- QuoteCrawler: 新浪财经、东财行情接口
- NewsCrawler: 新闻列表、搜索、股票相关新闻
- AnnouncementCrawler: 公告列表、股票公告

**数据源**:
- 实时行情: 新浪财经 HTTP、东财 HTTP
- 新闻资讯: 新浪财经、东财
- 公司公告: 巨潮资讯网

---

### 4.4 tasks/ - 定时任务层

```
src/tasks/
├── __init__.py
├── tasks.py             # 模块导出
├── scheduler.py         # APScheduler 调度器
└── jobs.py              # 定时任务定义
```

**已完成任务**:
- 每 3 秒: 实时行情采集
- 每小时: 新闻资讯采集
- 每小时: 公告采集
- 每日 17:00: 历史数据更新
- 每日 23:00: 数据备份

---

### 4.5 PRD 需求对照表

## 五、PRD 需求对照表

| PRD 需求 | 当前状态 | 备注 |
|----------|----------|------|
| MySQL 数据库 | ✅ 完成 | stock_basic, stock_realtime, stock_history, user_info, user_holdings |
| MongoDB 数据库 | ✅ 完成 | news_collection, announcement_collection, comment_collection, log_collection |
| Redis 缓存 | ✅ 完成 | 实时行情缓存、会话缓存 |
| 数据模型 | ✅ 完成 | 股票、用户、新闻模型 |
| 仓储层 | ✅ 完成 | 增删改查封装 |
| Flask Web 框架 | ✅ 完成 | 已添加到依赖 |
| 业务逻辑层 | ✅ 完成 | services/ |
| API 接口层 | ✅ 完成 | 15+ REST 接口 |
| 数据采集层 | ✅ 完成 | 行情/新闻/公告爬虫 |
| 定时任务 | ✅ 完成 | APScheduler 调度 |

---

## 六、项目模块总结

| 模块 | 文件 | 功能 |
|------|------|------|
| db/ | mysql_db.py, mongodb.py, redis_db.py | 数据库连接管理 |
| models/ | stock.py, user.py, news.py, exceptions.py | 数据模型定义 |
| repositories/ | stock_repo.py, user_repo.py, news_repo.py | 数据访问层 |
| services/ | stock_service.py, user_service.py, news_service.py | 业务逻辑层 |
| api/ | app.py, stock_routes.py, user_routes.py, news_routes.py | REST API |
| crawlers/ | base.py, quote_crawler.py, news_crawler.py, announcement_crawler.py | 数据采集 |
| tasks/ | scheduler.py, jobs.py | 定时任务调度 |

---

## 七、技术栈清单

| 类别 | 技术 | 版本 |
|------|------|------|
| 编程语言 | Python | 3.9+ |
| Web 框架 | Flask | 3.0.0 |
| 数据库 | MySQL | 8.0+ |
| 文档数据库 | MongoDB | 5.0+ |
| 缓存 | Redis | 6.0+ |
| 爬虫 | requests + BeautifulSoup | - |
| 定时任务 | APScheduler | 3.10.4 |
| 测试 | pytest | 7.4.4 |
| 数据处理 | pandas | 2.2.0 |

---

*本文档将根据项目进度持续更新*
