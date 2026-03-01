"""分析 API 路由

提供股票分析接口
"""

from flask import Blueprint, jsonify, request
from src.services.analysis_service import get_analysis_service, generate_stock_report
from src.services.data_provider import StockQuoteClient

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/stock/<symbol>/analyze', methods=['GET'])
def analyze_stock(symbol):
    """分析股票

    Query params:
        use_llm: 是否使用 LLM 分析 (true/false)

    Args:
        symbol: 股票代码

    Returns:
        JSON 分析结果
    """
    try:
        use_llm = request.args.get('use_llm', 'false').lower() == 'true'

        service = get_analysis_service(use_llm=use_llm)
        result = service.analyze_stock(symbol)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Analysis failed',
            'error': str(e)
        }), 500


@analysis_bp.route('/stock/<symbol>/report', methods=['GET'])
def get_stock_report(symbol):
    """获取股票分析报告

    Args:
        symbol: 股票代码

    Returns:
        JSON 报告文本
    """
    try:
        use_llm = request.args.get('use_llm', 'false').lower() == 'true'

        service = get_analysis_service(use_llm=use_llm)
        report = service.generate_report(symbol)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'symbol': symbol,
                'report': report
            }
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Report generation failed',
            'error': str(e)
        }), 500


@analysis_bp.route('/stock/<symbol>/quote', methods=['GET'])
def get_stock_quote(symbol):
    """获取股票实时行情

    Args:
        symbol: 股票代码

    Returns:
        JSON 行情数据
    """
    try:
        df = StockQuoteClient.get_quote([symbol])

        if df.empty:
            return jsonify({
                'code': 404,
                'message': 'Stock not found',
                'data': None
            }), 404

        data = df.iloc[0].to_dict()

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Failed to get quote',
            'error': str(e)
        }), 500
