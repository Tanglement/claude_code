"""News API routes."""

from flask import Blueprint, jsonify, request

from src.services.news_service import get_news_service
from src.models.exceptions import StockNotFoundError

news_bp = Blueprint('news', __name__)


@news_bp.route('/news/latest', methods=['GET'])
def get_latest_news():
    """Get latest news.

    Query params:
        limit: Number of news to return (default: 10)

    Returns:
        JSON response with news list
    """
    try:
        limit = int(request.args.get('limit', 10))

        service = get_news_service()
        news = service.get_latest_news(limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': news
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@news_bp.route('/news/search', methods=['GET'])
def search_news():
    """Search news by keyword.

    Query params:
        keyword: Search keyword
        limit: Number of results (default: 10)

    Returns:
        JSON response with news list
    """
    try:
        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 10))

        if not keyword:
            return jsonify({
                'code': 400,
                'message': 'Keyword is required'
            }), 400

        service = get_news_service()
        news = service.search_news(keyword, limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': news
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@news_bp.route('/news/<news_id>', methods=['GET'])
def get_news_by_id(news_id):
    """Get news by ID.

    Args:
        news_id: News ID

    Returns:
        JSON response with news details
    """
    try:
        service = get_news_service()
        news = service.get_news_by_id(news_id)

        if not news:
            return jsonify({
                'code': 404,
                'message': 'News not found'
            }), 404

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': news
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@news_bp.route('/stock/<symbol>/news', methods=['GET'])
def get_stock_news(symbol):
    """Get news related to a specific stock.

    Args:
        symbol: Stock code

    Query params:
        limit: Number of news to return (default: 10)

    Returns:
        JSON response with news list
    """
    try:
        limit = int(request.args.get('limit', 10))

        service = get_news_service()
        news = service.get_news_by_stock(symbol, limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': news
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


# ==================== Announcements ====================

@news_bp.route('/announcement/latest', methods=['GET'])
def get_latest_announcements():
    """Get latest announcements.

    Query params:
        limit: Number of announcements (default: 10)

    Returns:
        JSON response with announcements
    """
    try:
        limit = int(request.args.get('limit', 10))

        service = get_news_service()
        announcements = service.get_latest_announcements(limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': announcements
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@news_bp.route('/stock/<symbol>/announcements', methods=['GET'])
def get_stock_announcements(symbol):
    """Get announcements for a specific stock.

    Args:
        symbol: Stock code

    Query params:
        limit: Number of announcements (default: 10)

    Returns:
        JSON response with announcements
    """
    try:
        limit = int(request.args.get('limit', 10))

        service = get_news_service()
        announcements = service.get_announcements_by_stock(symbol, limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': announcements
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


# ==================== Comments ====================

@news_bp.route('/stock/<symbol>/comments', methods=['GET'])
def get_stock_comments(symbol):
    """Get comments for a specific stock.

    Args:
        symbol: Stock code

    Query params:
        limit: Number of comments (default: 20)

    Returns:
        JSON response with comments
    """
    try:
        limit = int(request.args.get('limit', 20))

        service = get_news_service()
        comments = service.get_comments_by_stock(symbol, limit=limit)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': comments
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@news_bp.route('/stock/<symbol>/comments', methods=['POST'])
def add_comment(symbol):
    """Add a comment for a stock.

    Headers:
        X-User-Id: User ID

    Request body:
        content: Comment content

    Returns:
        JSON response with comment ID
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        data = request.get_json()
        content = data.get('content', '')

        # Get username from query param or use default
        username = data.get('username', 'anonymous')

        service = get_news_service()
        comment_id = service.add_comment(
            user_id=int(user_id),
            username=username,
            content=content,
            target_stock=symbol
        )

        return jsonify({
            'code': 201,
            'message': 'Comment added',
            'data': {'id': comment_id}
        }), 201

    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e),
            'error': 'Validation error'
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500
