"""数据接口测试脚本

测试 akshare 数据接口是否正常工作
"""

import sys
sys.path.insert(0, '.')

from src.services.data_provider import (
    MarketDataProvider,
    FundamentalProvider,
    QuantFactorProvider,
    MacroRiskProvider,
    get_market_data,
    get_news_for_analysis,
    get_quant_factors
)


def test_market_data():
    """测试行情数据接口"""
    print("\n" + "=" * 60)
    print("1. 测试行情数据接口 (Market Data)")
    print("=" * 60)

    # 测试实时行情
    print("\n[1.1] 实时行情 (get_realtime_quotes)")
    try:
        df = MarketDataProvider.get_realtime_quotes(['002738'])
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df[['代码', '名称', '最新价', '涨跌幅']].head().to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试历史日线
    print("\n[1.2] 历史日线 (get_stock_daily)")
    try:
        df = MarketDataProvider.get_stock_daily('002738', start_date='20250101', end_date='20250228')
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df[['date', 'open', 'close', 'volume']].tail(5).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试行业成分股
    print("\n[1.3] 行业成分股 (get_industry_constituents)")
    try:
        df = MarketDataProvider.get_industry_constituents('BK1043')  # 电池板块
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df[['代码', '名称']].head(5).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")


def test_fundamental():
    """测试基本面与新闻接口"""
    print("\n" + "=" * 60)
    print("2. 测试基本面与新闻接口 (Fundamental & News)")
    print("=" * 60)

    # 测试财务指标
    print("\n[2.1] 财务指标 (get_financial_indicator)")
    try:
        df = FundamentalProvider.get_financial_indicator('002738')
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df.columns.tolist()[:8])
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试个股新闻
    print("\n[2.2] 个股新闻 (get_stock_news)")
    try:
        df = FundamentalProvider.get_stock_news('002738')
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            # 尝试显示可用列
            print(f"列名: {df.columns.tolist()[:5]}")
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试研报
    print("\n[2.3] 个股研报 (get_research_reports)")
    try:
        df = FundamentalProvider.get_research_reports('002738')
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")


def test_quant_factors():
    """测试量化因子接口"""
    print("\n" + "=" * 60)
    print("3. 测试量化因子接口 (Quant Factors)")
    print("=" * 60)

    # 测试资金流
    print("\n[3.1] 个股资金流 (get_fund_flow)")
    try:
        df = QuantFactorProvider.get_fund_flow('002738')
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(f"列名: {df.columns.tolist()[:6]}")
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试北向资金
    print("\n[3.2] 北向资金 (get_hsgt_flow)")
    try:
        df = QuantFactorProvider.get_hsgt_flow()
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df.tail(3).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试龙虎榜
    print("\n[3.3] 龙虎榜明细 (get_lhb_details)")
    try:
        df = QuantFactorProvider.get_lhb_details()
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")


def test_macro_risk():
    """测试宏观风控接口"""
    print("\n" + "=" * 60)
    print("4. 测试宏观风控接口 (Macro & Risk)")
    print("=" * 60)

    # 测试债收益率
    print("\n[4.1] 中美债收益率 (get_bond_rates)")
    try:
        df = MacroRiskProvider.get_bond_rates()
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df.tail(5).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试恐慌指数
    print("\n[4.2] 恐慌指数 VIX (get_vix)")
    try:
        df = MacroRiskProvider.get_vix()
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df.tail(3).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    # 测试黄金价格
    print("\n[4.3] 黄金价格 (get_gold_price)")
    try:
        df = MacroRiskProvider.get_gold_price()
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
            print(df.tail(3).to_string())
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")


def test_convenience_functions():
    """测试便捷函数"""
    print("\n" + "=" * 60)
    print("5. 测试便捷函数")
    print("=" * 60)

    print("\n[5.1] get_market_data('002738', 30)")
    try:
        df = get_market_data('002738', 30)
        if not df.empty:
            print(f"[OK] 成功获取 {len(df)} 条记录")
        else:
            print("[FAIL] 返回空数据")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")

    print("\n[5.2] get_quant_factors('002738')")
    try:
        factors = get_quant_factors('002738')
        print(f"[OK] 获取到 {len(factors)} 种因子数据")
        for k, v in factors.items():
            print(f"  - {k}: {len(v)} 条")
    except Exception as e:
        print(f"[FAIL] 获取失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("AKShare 数据接口测试")
    print("测试股票: 中矿资源 (002738)")
    print("=" * 60)

    test_market_data()
    test_fundamental()
    test_quant_factors()
    test_macro_risk()
    test_convenience_functions()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
