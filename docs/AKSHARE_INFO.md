# akshare 可查询信息一览

> 中矿资源(002738) 可用的数据接口

---

## 1. 股票行情数据

| 函数名 | 说明 | 示例 |
|--------|------|------|
| `stock_zh_a_spot_em()` | A股全市场实时行情 | 全部A股实时涨跌幅 |
| `stock_zh_a_daily()` | 个股历史K线 | `ak.stock_zh_a_daily(symbol="sh002738")` |
| `stock_zh_index_spot()` | 指数实时行情 | 上证指数、深证成指 |
| `stock_individual_info_em()` | 个股基本信息 | 股本、PE、换手率 |
| `stock_zh_kline()` | 股票K线数据 | 分钟/日/周/月K线 |

## 2. 资金流向

| 函数名 | 说明 |
|--------|------|
| `stock_individual_fund_flow()` | 个股资金流向(主力/散户) |
| `stock_market_fund_flow()` | 市场资金流向 |
| `stock_hsgt_board_rank()` | 北向资金持股 |

## 3. 财务数据

| 函数名 | 说明 |
|--------|------|
| `stock_financial_abstract()` | 财务摘要(营收/利润) |
| `stock_financial_analysis()` | 财务分析指标 |
| `stock_yjbb()` | 业绩报表(季报/年报) |
| `stock_fhpg()` | 分红配股 |

## 4. 股东与股本

| 函数名 | 说明 |
|--------|------|
| `stock_zh_a_gdhs()` | 股东户数变化 |
| `stock_zh_a_pledge_ratio()` | 股权质押比例 |
| `stock_zh_a_xszg()` | 限售股解禁 |

## 5. 机构持仓

| 函数名 | 说明 |
|--------|------|
| `stock_zh_a_cg()` | 机构持仓明细 |
| `stock_fund_flow_kt()` | 龙虎榜机构买卖 |

## 6. 融资融券

| 函数名 | 说明 |
|--------|------|
| `stock_margin_detail()` | 融资融券明细 |
| `stock_margin_change()` | 融资融券变动 |

## 7. 指数数据

| 函数名 | 说明 |
|--------|------|
| `stock_zh_index_spot()` | 主要指数行情 |
| `index_stock_cons()` | 指数成分股 |

## 8. 宏观经济

| 函数名 | 说明 |
|--------|------|
| `macro_cn_gdp()` | 中国GDP |
| `macro_cn_m2()` | 货币M2 |
| `macro_cn_cpi()` | 居民消费价格指数 |

## 9. 基金数据

| 函数名 | 说明 |
|--------|------|
| `fund_etf_spot_em()` | ETF实时行情 |
| `fund_etf_hist()` | ETF历史数据 |

---

## 中矿资源(002738) 查询示例

```python
import akshare as ak

# 1. 个股基本信息
df = ak.stock_individual_info_em(symbol="002738")
print(df)

# 2. 历史K线数据
df = ak.stock_zh_a_daily(symbol="sh002738")
print(df.tail(10))

# 3. 资金流向
df = ak.stock_individual_fund_flow(symbol="002738")
print(df)

# 4. 财务摘要
df = ak.stock_financial_abstract(symbol="002738")
print(df)
```

---

> akshare 总计提供 **500+** 个金融数据接口
