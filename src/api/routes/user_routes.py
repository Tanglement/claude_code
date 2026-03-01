"""User API routes."""

from flask import Blueprint, jsonify, request

from src.services.user_service import get_user_service
from src.models.exceptions import UserNotFoundError, AuthenticationError, DuplicateError

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/register', methods=['POST'])
def register():
    """User registration endpoint.

    Request body:
        username: Username
        password: Password
        email: Email (optional)
        phone: Phone (optional)

    Returns:
        JSON response with user info
    """
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')

        if not username or not password:
            return jsonify({
                'code': 400,
                'message': 'Username and password are required'
            }), 400

        service = get_user_service()
        result = service.register(username, password, email, phone)

        return jsonify({
            'code': 200,
            'message': 'User registered successfully',
            'data': result
        }), 201

    except DuplicateError as e:
        return jsonify({
            'code': 409,
            'message': str(e),
            'error': 'Username already exists'
        }), 409
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


@user_bp.route('/user/login', methods=['POST'])
def login():
    """User login endpoint.

    Request body:
        username: Username
        password: Password

    Returns:
        JSON response with token
    """
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'code': 400,
                'message': 'Username and password are required'
            }), 400

        service = get_user_service()
        result = service.login(username, password)

        return jsonify({
            'code': 200,
            'message': 'Login successful',
            'data': result
        })

    except AuthenticationError as e:
        return jsonify({
            'code': 401,
            'message': str(e),
            'error': 'Invalid credentials'
        }), 401
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/info', methods=['GET'])
def get_user_info():
    """Get user information.

    Headers:
        Authorization: Bearer token

    Returns:
        JSON response with user info
    """
    try:
        # Get user_id from token (simplified - should use proper auth)
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized',
                'error': 'Missing authorization'
            }), 401

        service = get_user_service()
        result = service.get_user_info(int(user_id))

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })

    except UserNotFoundError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'error': 'User not found'
        }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/holdings', methods=['GET'])
def get_holdings():
    """Get user holdings.

    Headers:
        Authorization: Bearer token

    Returns:
        JSON response with holdings
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        service = get_user_service()
        holdings = service.get_holdings(int(user_id))

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': holdings
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/holdings', methods=['POST'])
def add_holding():
    """Add a new holding.

    Headers:
        Authorization: Bearer token

    Request body:
        symbol: Stock code
        shares: Number of shares
        cost_price: Cost price
        purchase_date: Purchase date (YYYY-MM-DD)

    Returns:
        JSON response with holding ID
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        data = request.get_json()

        service = get_user_service()
        holding_id = service.add_holding(
            user_id=int(user_id),
            symbol=data['symbol'],
            shares=data['shares'],
            cost_price=data['cost_price'],
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d')
        )

        return jsonify({
            'code': 201,
            'message': 'Holding added',
            'data': {'id': holding_id}
        })

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


@user_bp.route('/user/holdings/<symbol>', methods=['DELETE'])
def delete_holding(symbol):
    """Delete a holding.

    Headers:
        Authorization: Bearer token

    Args:
        symbol: Stock code

    Returns:
        JSON response
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        service = get_user_service()
        service.delete_holding(int(user_id), symbol)

        return jsonify({
            'code': 200,
            'message': 'Holding deleted'
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


# Import datetime for the add_holding function
from datetime import datetime


# ==================== Watchlist Routes ====================

@user_bp.route('/user/watchlist', methods=['GET'])
def get_watchlist():
    """Get user watchlist.

    Headers:
        X-User-Id: User ID

    Returns:
        JSON response with watchlist
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        service = get_user_service()
        watchlist = service.get_watchlist(int(user_id))

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': watchlist
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/watchlist', methods=['POST'])
def add_watchlist():
    """Add stock to watchlist.

    Headers:
        X-User-Id: User ID

    Request body:
        symbol: Stock code (required)
        stock_name: Stock name (optional)
        notes: Notes (optional)
        alert_price: Alert price (optional)
        alert_pct: Alert percentage (optional)

    Returns:
        JSON response with watchlist ID
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        data = request.get_json()
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({
                'code': 400,
                'message': 'Stock symbol is required'
            }), 400

        service = get_user_service()
        watchlist_id = service.add_watchlist(
            user_id=int(user_id),
            symbol=symbol,
            stock_name=data.get('stock_name', ''),
            notes=data.get('notes', ''),
            alert_price=data.get('alert_price'),
            alert_pct=data.get('alert_pct')
        )

        return jsonify({
            'code': 201,
            'message': 'Stock added to watchlist',
            'data': {'id': watchlist_id}
        }), 201

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/watchlist/<symbol>', methods=['PUT'])
def update_watchlist(symbol):
    """Update watchlist item.

    Headers:
        X-User-Id: User ID

    Request body:
        stock_name: Stock name (optional)
        notes: Notes (optional)
        alert_price: Alert price (optional)
        alert_pct: Alert percentage (optional)

    Returns:
        JSON response
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        data = request.get_json()
        service = get_user_service()
        result = service.update_watchlist(
            user_id=int(user_id),
            symbol=symbol,
            stock_name=data.get('stock_name'),
            notes=data.get('notes'),
            alert_price=data.get('alert_price'),
            alert_pct=data.get('alert_pct')
        )

        return jsonify({
            'code': 200,
            'message': 'Watchlist updated' if result else 'No changes',
            'data': {'success': result}
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/watchlist/<symbol>', methods=['DELETE'])
def delete_watchlist(symbol):
    """Delete watchlist item.

    Headers:
        X-User-Id: User ID

    Args:
        symbol: Stock code

    Returns:
        JSON response
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        service = get_user_service()
        service.delete_watchlist(int(user_id), symbol)

        return jsonify({
            'code': 200,
            'message': 'Stock removed from watchlist'
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


# ==================== Preference Routes ====================

@user_bp.route('/user/preference', methods=['GET'])
def get_preference():
    """Get user notification preferences.

    Headers:
        X-User-Id: User ID

    Returns:
        JSON response with preferences
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        service = get_user_service()
        pref = service.get_preference(int(user_id))

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': pref
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500


@user_bp.route('/user/preference', methods=['POST'])
def save_preference():
    """Save user notification preferences.

    Headers:
        X-User-Id: User ID

    Request body:
        push_enabled: Enable push (default true)
        push_time: Push time like '09:30' (default '09:30')
        push_days: Push days like '1,2,3,4,5' (default '1,2,3,4,5')
        price_alert: Enable price alert (default true)
        news_alert: Enable news alert (default true)
        announcement_alert: Enable announcement alert (default true)

    Returns:
        JSON response
    """
    try:
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized'
            }), 401

        data = request.get_json()
        service = get_user_service()
        result = service.save_preference(
            user_id=int(user_id),
            push_enabled=data.get('push_enabled', True),
            push_time=data.get('push_time', '09:30'),
            push_days=data.get('push_days', '1,2,3,4,5'),
            price_alert=data.get('price_alert', True),
            news_alert=data.get('news_alert', True),
            announcement_alert=data.get('announcement_alert', True)
        )

        return jsonify({
            'code': 200,
            'message': 'Preference saved',
            'data': {'success': result}
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': str(e)
        }), 500
