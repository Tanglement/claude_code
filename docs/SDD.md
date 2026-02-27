# 软件设计说明 (SDD)

## 1. 系统概述

### 1.1 项目名称
股票信息获取系统 (Stock Information System)

### 1.2 系统功能
提供股票基本信息、实时行情、历史行情、新闻资讯、用户管理等信息获取功能。

### 1.3 技术架构
- **关系型数据库**: MySQL (存储股票数据、用户数据)
- **非关系型数据库**: MongoDB (存储新闻、公告、日志)
- **API接口**: RESTful API

---

## 2. 数据库设计

### 2.1 MySQL 表结构

#### 2.1.1 股票基本信息表 (stock_basic)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| symbol | VARCHAR(20) | NOT NULL, UNIQUE | 股票代码 |
| name | VARCHAR(100) | NOT NULL | 股票名称 |
| full_name | VARCHAR(200) | | 股票全称 |
| market | VARCHAR(20) | NOT NULL | 市场类型 |
| industry | VARCHAR(50) | | 所属行业 |
| listing_date | DATE | | 上市日期 |
| delisting_date | DATE | | 退市日期 |
| status | ENUM | DEFAULT '正常' | 股票状态 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 2.1.2 实时行情数据表 (stock_realtime)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| symbol | VARCHAR(20) | NOT NULL | 股票代码 |
| price | DECIMAL(10,2) | NOT NULL | 当前价格 |
| change | DECIMAL(10,2) | NOT NULL | 涨跌额 |
| change_pct | DECIMAL(5,2) | NOT NULL | 涨跌幅(%) |
| open | DECIMAL(10,2) | NOT NULL | 开盘价 |
| high | DECIMAL(10,2) | NOT NULL | 最高价 |
| low | DECIMAL(10,2) | NOT NULL | 最低价 |
| close_yest | DECIMAL(10,2) | NOT NULL | 昨收价 |
| volume | BIGINT | NOT NULL | 成交量(股) |
| amount | DECIMAL(15,2) | NOT NULL | 成交额(万元) |
| turnover | DECIMAL(5,2) | NOT NULL | 换手率(%) |
| pe | DECIMAL(10,2) | | 市盈率 |
| pb | DECIMAL(10,2) | | 市净率 |
| datetime | DATETIME | NOT NULL | 时间戳 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

索引: `idx_symbol_datetime (symbol, datetime)`

#### 2.1.3 历史行情数据表 (stock_history)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| symbol | VARCHAR(20) | NOT NULL | 股票代码 |
| trade_date | DATE | NOT NULL | 交易日期 |
| open | DECIMAL(10,2) | NOT NULL | 开盘价 |
| high | DECIMAL(10,2) | NOT NULL | 最高价 |
| low | DECIMAL(10,2) | NOT NULL | 最低价 |
| close | DECIMAL(10,2) | NOT NULL | 收盘价 |
| volume | BIGINT | NOT NULL | 成交量 |
| amount | DECIMAL(15,2) | NOT NULL | 成交额 |
| adj_close | DECIMAL(10,2) | | 复权收盘价 |
| change_pct | DECIMAL(5,2) | | 涨跌幅(%) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

唯一索引: `idx_symbol_date (symbol, trade_date)`

#### 2.1.4 用户信息表 (user_info)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码(加密存储) |
| email | VARCHAR(100) | | 邮箱 |
| phone | VARCHAR(20) | | 手机号 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 2.1.5 用户持仓表 (user_holdings)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| user_id | INT | NOT NULL | 用户ID |
| symbol | VARCHAR(20) | NOT NULL | 股票代码 |
| shares | INT | NOT NULL | 持股数量 |
| cost_price | DECIMAL(10,2) | NOT NULL | 成本价 |
| purchase_date | DATE | NOT NULL | 购买日期 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

### 2.2 MongoDB 集合设计

#### 2.2.1 新闻资讯集合 (news_collection)

```json
{
    "_id": ObjectId,
    "title": "string",
    "content": "string",
    "publish_time": "datetime",
    "source": "string",
    "url": "string",
    "keywords": ["string"],
    "sentiment": "number",
    "related_stocks": ["string"]
}
```

#### 2.2.2 公司公告集合 (announcement_collection)

```json
{
    "_id": ObjectId,
    "title": "string",
    "content": "string",
    "publish_time": "datetime",
    "announcement_type": "string",
    "company_code": "string",
    "attachments": ["string"]
}
```

#### 2.2.3 用户评论集合 (comment_collection)

```json
{
    "_id": ObjectId,
    "user_id": "int",
    "username": "string",
    "content": "string",
    "target_stock": "string",
    "create_time": "datetime",
    "likes": "int",
    "dislikes": "int"
}
```

#### 2.2.4 系统日志集合 (log_collection)

```json
{
    "_id": ObjectId,
    "level": "string",
    "message": "string",
    "timestamp": "datetime",
    "module": "string"
}
```

---

## 3. 接口设计

### 3.1 数据库操作接口

#### MySQL 接口

##### 股票基本信息

```python
def insert_stock_basic(symbol, name, full_name, market, industry, listing_date):
    """插入股票基本信息"""
    pass

def get_stock_basic(symbol):
    """根据股票代码查询基本信息"""
    pass

def get_all_stocks():
    """查询所有股票基本信息"""
    pass

def update_stock_basic(symbol, **kwargs):
    """更新股票基本信息"""
    pass
```

##### 实时行情

```python
def insert_stock_realtime(symbol, price, change, change_pct, open_price, high, low, close_yest, volume, amount, turnover, pe, pb, datetime):
    """插入实时行情数据"""
    pass

def get_stock_realtime(symbol):
    """根据股票代码查询实时行情"""
    pass
```

##### 历史行情

```python
def insert_stock_history(symbol, trade_date, open_price, high, low, close, volume, amount, adj_close, change_pct):
    """插入历史行情数据"""
    pass

def get_stock_history(symbol, start_date, end_date):
    """查询股票历史行情"""
    pass
```

##### 用户管理

```python
def insert_user(username, password, email, phone):
    """创建用户"""
    pass

def get_user_by_username(username):
    """根据用户名查询用户"""
    pass

def verify_password(user_id, password):
    """验证用户密码"""
    pass
```

##### 用户持仓

```python
def insert_user_holding(user_id, symbol, shares, cost_price, purchase_date):
    """插入用户持仓"""
    pass

def get_user_holdings(user_id):
    """查询用户持仓"""
    pass

def update_user_holding(holding_id, shares, cost_price):
    """更新持仓"""
    pass
```

#### MongoDB 接口

##### 新闻资讯

```python
def insert_news(news_data):
    """插入新闻资讯"""
    pass

def get_latest_news(limit=10):
    """获取最新新闻"""
    pass

def get_news_by_stock(symbol, limit=10):
    """获取指定股票相关新闻"""
    pass
```

##### 公司公告

```python
def insert_announcement(announcement_data):
    """插入公司公告"""
    pass

def get_announcements_by_stock(symbol, limit=10):
    """获取指定股票的公告"""
    pass
```

##### 用户评论

```python
def insert_comment(user_id, username, content, target_stock):
    """插入用户评论"""
    pass

def get_comments_by_stock(symbol, limit=10):
    """获取指定股票评论"""
    pass
```

##### 系统日志

```python
def insert_log(level, message, module):
    """插入系统日志"""
    pass

def get_logs(limit=100):
    """查询系统日志"""
    pass
```

---

### 3.2 RESTful API 接口

#### 3.2.1 股票行情接口

**GET /api/v1/stock/{symbol}/realtime**

参数:
- symbol: 股票代码 (必填)

响应:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "symbol": "600519",
        "name": "贵州茅台",
        "price": 1686.00,
        "change": 10.00,
        "change_pct": 0.59,
        "open": 1676.00,
        "high": 1688.00,
        "low": 1675.00,
        "close_yest": 1676.00,
        "volume": 1234567,
        "amount": 2089000000,
        "turnover": 0.23,
        "pe": 58.52,
        "pb": 12.35,
        "datetime": "2021-06-25 15:00:00"
    }
}
```

#### 3.2.2 历史行情接口

**GET /api/v1/stock/{symbol}/history**

参数:
- symbol: 股票代码 (必填)
- start_date: 开始日期 (可选)
- end_date: 结束日期 (可选)

响应:
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "trade_date": "2021-06-25",
            "open": 1676.00,
            "high": 1688.00,
            "low": 1675.00,
            "close": 1686.00,
            "volume": 1234567,
            "amount": 2089000000
        }
    ]
}
```

#### 3.2.3 新闻资讯接口

**GET /api/v1/news/latest**

参数:
- limit: 返回数量 (默认10条)

响应:
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": "60f4b4b9e4b0c8b1d4e8f9a0",
            "title": "A股三大指数集体上涨，沪指涨0.5%",
            "content": "今日A股市场整体表现良好...",
            "publish_time": "2021-06-25 15:30:00",
            "source": "新浪财经",
            "url": "http://finance.sina.com.cn/stock/...",
            "sentiment": 0.3
        }
    ]
}
```

#### 3.2.4 用户登录接口

**POST /api/v1/user/login**

参数 (JSON):
```json
{
    "username": "user123",
    "password": "password123"
}
```

响应:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "user_id": 1,
        "username": "user123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

#### 3.2.5 用户持仓接口

**GET /api/v1/user/holdings**

响应:
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "shares": 100,
            "cost_price": 1600.00,
            "current_price": 1686.00,
            "profit": 8600.00,
            "profit_pct": 5.38
        }
    ]
}
```

---

## 4. 模块设计

### 4.1 模块清单

| 模块名称 | 说明 |
|----------|------|
| db | 数据库连接和配置 |
| models | 数据模型定义 |
| repositories | 数据访问层 |
| services | 业务逻辑层 |
| api | RESTful API接口 |
| utils | 工具函数 |

### 4.2 目录结构

```
src/
├── db/
│   ├── mysql.py      # MySQL连接
│   └── mongodb.py    # MongoDB连接
├── models/
│   ├── stock.py      # 股票模型
│   ├── user.py       # 用户模型
│   └── news.py       # 新闻模型
├── repositories/
│   ├── stock_repo.py       # 股票数据访问
│   ├── user_repo.py        # 用户数据访问
│   └── news_repo.py        # 新闻数据访问
├── services/
│   ├── stock_service.py    # 股票业务逻辑
│   ├── user_service.py     # 用户业务逻辑
│   └── news_service.py     # 新闻业务逻辑
├── api/
│   ├── routes.py           # API路由
│   └── handlers.py         # 请求处理
└── utils/
    ├── config.py           # 配置管理
    └── logger.py           # 日志工具
```

---

## 5. 错误处理

### 5.1 错误码定义

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 5.2 异常类

```python
class StockNotFoundError(Exception):
    """股票不存在异常"""
    pass

class UserNotFoundError(Exception):
    """用户不存在异常"""
    pass

class AuthenticationError(Exception):
    """认证失败异常"""
    pass

class DatabaseError(Exception):
    """数据库操作异常"""
    pass
```
