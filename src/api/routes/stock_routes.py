"""Stock API routes."""

from flask import Blueprint, jsonify, request
from datetime import datetime, date

from src.services.stock_service import get_stock_service
from src.models.exceptions import StockNotFoundError

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/stock/<symbol>/realtime', methods=['GET'])
def get_stock_realtime(symbol):
    """Get stock realtime quote.

    Args:
        symbol: Stock code

    Returns:
        JSON response with realtime quote
    """
    try:
        service = get_stock_service()
        quote = service.get_stock_quote(symbol)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': quote
        })
    except StockNotFoundError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'error': 'Stock not found'
        }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/basic', methods=['GET'])
def get_stock_basic(symbol):
    """Get stock basic information.

    Args:
        symbol: Stock code

    Returns:
        JSON response with basic info
    """
    try:
        service = get_stock_service()
        basic = service.get_stock_basic(symbol)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': basic
        })
    except StockNotFoundError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'error': 'Stock not found'
        }), 404


@stock_bp.route('/stock', methods=['GET'])
def get_all_stocks():
    """Get all stocks or search stocks.

    Query params:
        market: Filter by market type
        limit: Maximum number of records
        q: Search keyword (股票代码或名称)

    Returns:
        JSON response with stocks list or search results
    """
    try:
        keyword = request.args.get('q', '')
        market = request.args.get('market')
        limit = int(request.args.get('limit', 1000))

        # 如果有搜索关键词，则执行搜索
        if keyword:
            from src.services.data_provider import StockListProvider
            results = StockListProvider.search_stocks(keyword, limit=limit)
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': results
            })

        # 否则返回全部股票
        service = get_stock_service()
        stocks = service.get_all_stocks(market=market, limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': stocks
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/load', methods=['POST'])
def load_stocks_to_db():
    """Load stock list from Tushare/AKShare to MySQL database.

    Returns:
        JSON response with loading result
    """
    try:
        from src.services.data_provider import StockListProvider
        force = request.args.get('force', 'false').lower() == 'true'
        count = StockListProvider.load_stock_list_to_db(force=force)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {'count': count}
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/count', methods=['GET'])
def get_stock_count():
    """Get stock count in database.

    Returns:
        JSON response with stock count
    """
    try:
        from src.services.data_provider import StockListProvider
        count = StockListProvider.get_stock_count()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {'count': count}
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    """Get stock history data.

    Query params:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of records

    Args:
        symbol: Stock code

    Returns:
        JSON response with history data
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))

        # Parse dates
        start_date = None
        end_date = None
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        service = get_stock_service()
        history = service.get_history(symbol, start_date, end_date, limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': history
        })
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': 'Invalid date format',
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/hot', methods=['GET'])
def get_hot_stocks():
    """Get hot stocks by volume.

    Query params:
        limit: Number of records (default 10)

    Returns:
        JSON response with hot stocks
    """
    try:
        limit = int(request.args.get('limit', 10))

        from src.services.data_provider import MarketDataProvider
        df = MarketDataProvider.get_hot_stocks(limit=limit)

        # Convert to list of dicts
        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/announcements', methods=['GET'])
def get_stock_announcements(symbol):
    """Get stock announcements.

    Query params:
        limit: Number of records (default 20)

    Args:
        symbol: Stock code

    Returns:
        JSON response with announcements
    """
    try:
        limit = int(request.args.get('limit', 20))

        from src.services.data_provider import MarketDataProvider
        df = MarketDataProvider.get_stock_announcements(symbol, limit=limit)

        # Convert to list of dicts
        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


# ============================================================
# 财务数据接口
# ============================================================

@stock_bp.route('/stock/<symbol>/financials', methods=['GET'])
def get_stock_financials(symbol):
    """获取财务指标摘要

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回记录数 (默认5)

    Returns:
        JSON 财务指标数据
    """
    try:
        limit = int(request.args.get('limit', 5))

        from src.services.data_provider import FinancialDataProvider
        df = FinancialDataProvider.get_financial_summary(symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get financials',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/income', methods=['GET'])
def get_stock_income(symbol):
    """获取利润表数据

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回记录数 (默认5)

    Returns:
        JSON 利润表数据
    """
    try:
        limit = int(request.args.get('limit', 5))

        from src.services.data_provider import FinancialDataProvider
        df = FinancialDataProvider.get_income_statement(symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get income statement',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/balance', methods=['GET'])
def get_stock_balance(symbol):
    """获取资产负债表数据

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回记录数 (默认5)

    Returns:
        JSON 资产负债表数据
    """
    try:
        limit = int(request.args.get('limit', 5))

        from src.services.data_provider import FinancialDataProvider
        df = FinancialDataProvider.get_balance_sheet(symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get balance sheet',
            'error': str(e)
        }), 500


# ============================================================
# 行业数据接口
# ============================================================

@stock_bp.route('/industry/list', methods=['GET'])
def get_industry_list():
    """获取行业板块列表

    Returns:
        JSON 行业列表
    """
    try:
        from src.services.data_provider import IndustryDataProvider
        df = IndustryDataProvider.get_industry_list()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get industry list',
            'error': str(e)
        }), 500


@stock_bp.route('/industry/<path:industry>/stocks', methods=['GET'])
def get_industry_stocks(industry):
    """获取行业成分股

    Args:
        industry: 行业名称

    Query params:
        limit: 返回数量 (默认50)

    Returns:
        JSON 成分股列表
    """
    try:
        limit = int(request.args.get('limit', 50))

        # URL解码行业名称
        import urllib.parse
        industry = urllib.parse.unquote(industry)

        from src.services.data_provider import IndustryDataProvider
        df = IndustryDataProvider.get_industry_stocks(industry, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get industry stocks',
            'error': str(e)
        }), 500


@stock_bp.route('/concept/list', methods=['GET'])
def get_concept_list():
    """获取概念板块列表

    Returns:
        JSON 概念列表
    """
    try:
        from src.services.data_provider import IndustryDataProvider
        df = IndustryDataProvider.get_concept_list()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get concept list',
            'error': str(e)
        }), 500


@stock_bp.route('/concept/<path:concept>/stocks', methods=['GET'])
def get_concept_stocks(concept):
    """获取概念成分股

    Args:
        concept: 概念名称

    Query params:
        limit: 返回数量 (默认50)

    Returns:
        JSON 成分股列表
    """
    try:
        limit = int(request.args.get('limit', 50))

        import urllib.parse
        concept = urllib.parse.unquote(concept)

        from src.services.data_provider import IndustryDataProvider
        df = IndustryDataProvider.get_concept_stocks(concept, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get concept stocks',
            'error': str(e)
        }), 500


# ============================================================
# 研报数据接口
# ============================================================

@stock_bp.route('/stock/<symbol>/reports', methods=['GET'])
def get_stock_reports(symbol):
    """获取个股研报

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回数量 (默认10)

    Returns:
        JSON 研报数据
    """
    try:
        limit = int(request.args.get('limit', 10))

        from src.services.data_provider import ReportDataProvider
        df = ReportDataProvider.get_research_reports(symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get research reports',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/forecast', methods=['GET'])
def get_stock_forecast(symbol):
    """获取业绩预测

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回数量 (默认5)

    Returns:
        JSON 业绩预测数据
    """
    try:
        limit = int(request.args.get('limit', 5))

        from src.services.data_provider import ReportDataProvider
        df = ReportDataProvider.get_stock_forecast(symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get forecast',
            'error': str(e)
        }), 500


# ============================================================
# 资金流向接口
# ============================================================

@stock_bp.route('/stock/<symbol>/fund-flow', methods=['GET'])
def get_stock_fund_flow(symbol):
    """获取个股资金流向

    Args:
        symbol: 股票代码

    Query params:
        days: 天数 (默认5)

    Returns:
        JSON 资金流向数据
    """
    try:
        days = int(request.args.get('days', 5))

        from src.services.data_provider import FundFlowProvider
        df = FundFlowProvider.get_fund_flow(symbol, days=days)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get fund flow',
            'error': str(e)
        }), 500


@stock_bp.route('/sector/fund-flow', methods=['GET'])
def get_sector_fund_flow():
    """获取板块资金流向

    Query params:
        limit: 返回数量 (默认10)

    Returns:
        JSON 板块资金流向
    """
    try:
        limit = int(request.args.get('limit', 10))

        from src.services.data_provider import FundFlowProvider
        df = FundFlowProvider.get_sector_fund_flow(limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get sector fund flow',
            'error': str(e)
        }), 500


# ============================================================
# 龙虎榜接口
# ============================================================

@stock_bp.route('/top/list', methods=['GET'])
def get_top_list():
    """获取当日龙虎榜

    Query params:
        date: 日期 (YYYYMMDD)，默认最新

    Returns:
        JSON 龙虎榜数据
    """
    try:
        date = request.args.get('date')

        from src.services.data_provider import TopListProvider
        df = TopListProvider.get_top_list(date=date)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get top list',
            'error': str(e)
        }), 500


@stock_bp.route('/stock/<symbol>/top-inst', methods=['GET'])
def get_top_inst(symbol):
    """获取龙虎榜机构明细

    Args:
        symbol: 股票代码

    Query params:
        date: 日期 (YYYYMMDD)

    Returns:
        JSON 机构明细
    """
    try:
        date = request.args.get('date')

        from src.services.data_provider import TopListProvider
        df = TopListProvider.get_top_inst(symbol=symbol, date=date)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get top inst',
            'error': str(e)
        }), 500


# ============================================================
# 融资融券接口
# ============================================================

@stock_bp.route('/stock/<symbol>/margin', methods=['GET'])
def get_stock_margin(symbol):
    """获取融资融券明细

    Args:
        symbol: 股票代码

    Returns:
        JSON 融资融券明细
    """
    try:
        from src.services.data_provider import MarginProvider
        df = MarginProvider.get_margin_detail(symbol=symbol)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get margin data',
            'error': str(e)
        }), 500


@stock_bp.route('/margin/sx', methods=['GET'])
def get_margin_sx():
    """获取融资融券余额

    Returns:
        JSON 融资融券余额
    """
    try:
        from src.services.data_provider import MarginProvider
        df = MarginProvider.get_margin_sx()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get margin sx',
            'error': str(e)
        }), 500


# ============================================================
# 宏观数据接口
# ============================================================

@stock_bp.route('/macro/gdp', methods=['GET'])
def get_macro_gdp():
    """获取GDP数据

    Query params:
        quarter: 季度 (如 2024Q1)

    Returns:
        JSON GDP数据
    """
    try:
        quarter = request.args.get('quarter')

        from src.services.data_provider import MacroDataProvider
        df = MacroDataProvider.get_gdp_data(quarter=quarter)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get GDP data',
            'error': str(e)
        }), 500


@stock_bp.route('/macro/cpi', methods=['GET'])
def get_macro_cpi():
    """获取CPI数据

    Query params:
        month: 月份 (如 202401)

    Returns:
        JSON CPI数据
    """
    try:
        month = request.args.get('month')

        from src.services.data_provider import MacroDataProvider
        df = MacroDataProvider.get_cpi_data(month=month)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get CPI data',
            'error': str(e)
        }), 500


@stock_bp.route('/macro/m2', methods=['GET'])
def get_macro_m2():
    """获取货币供应量数据

    Returns:
        JSON M2数据
    """
    try:
        from src.services.data_provider import MacroDataProvider
        df = MacroDataProvider.get_money_supply()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get M2 data',
            'error': str(e)
        }), 500


@stock_bp.route('/macro/pmi', methods=['GET'])
def get_macro_pmi():
    """获取PMI数据

    Returns:
        JSON PMI数据
    """
    try:
        from src.services.data_provider import MacroDataProvider
        df = MacroDataProvider.get_pmi_data()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get PMI data',
            'error': str(e)
        }), 500


@stock_bp.route('/macro/lpr', methods=['GET'])
def get_macro_lpr():
    """获取LPR利率数据

    Returns:
        JSON LPR数据
    """
    try:
        from src.services.data_provider import MacroDataProvider
        df = MacroDataProvider.get_interest_rate()

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get LPR data',
            'error': str(e)
        }), 500


# ============================================================
# 大宗交易接口
# ============================================================

@stock_bp.route('/block/trades', methods=['GET'])
def get_block_trades():
    """获取大宗交易数据

    Query params:
        symbol: 股票代码
        date: 日期 (YYYYMMDD)
        limit: 返回数量 (默认20)

    Returns:
        JSON 大宗交易数据
    """
    try:
        symbol = request.args.get('symbol')
        date = request.args.get('date')
        limit = int(request.args.get('limit', 20))

        from src.services.data_provider import BlockTradeProvider
        df = BlockTradeProvider.get_block_trades(symbol=symbol, date=date, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get block trades',
            'error': str(e)
        }), 500


# ============================================================
# 股东数据接口
# ============================================================

@stock_bp.route('/stock/<symbol>/holders', methods=['GET'])
def get_stock_holders(symbol):
    """获取股东增减持数据

    Args:
        symbol: 股票代码

    Query params:
        limit: 返回数量 (默认10)

    Returns:
        JSON 股东增减持数据
    """
    try:
        limit = int(request.args.get('limit', 10))

        from src.services.data_provider import HolderProvider
        df = HolderProvider.get_holder_trade(symbol=symbol, limit=limit)

        data = df.to_dict('records') if not df.empty else []

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get holder data',
            'error': str(e)
        }), 500
