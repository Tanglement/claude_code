"""Authentication middleware."""

from functools import wraps
from flask import request, jsonify

from src.services.user_service import get_auth_service


def require_auth(f):
    """Decorator to require authentication.

    Checks for valid token in Authorization header.
    Adds user_id to request context on success.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized',
                'error': 'Missing authorization header'
            }), 401

        # Parse Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({
                'code': 401,
                'message': 'Unauthorized',
                'error': 'Invalid authorization format'
            }), 401

        token = parts[1]

        # TODO: Implement proper token verification
        # For now, we'll use a simplified approach
        # In production, use JWT or similar

        # For demo purposes, accept X-User-Id header
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized',
                'error': 'Missing user ID'
            }), 401

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                'code': 401,
                'message': 'Unauthorized',
                'error': 'Invalid user ID'
            }), 401

        # Add user_id to request
        request.user_id = user_id

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """Decorator for optional authentication.

    If token is provided, validates it.
    Adds user_id to request if authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')

        if user_id:
            try:
                request.user_id = int(user_id)
            except ValueError:
                request.user_id = None
        else:
            request.user_id = None

        return f(*args, **kwargs)

    return decorated_function
