"""Flask application factory."""

import os
from flask import Flask, jsonify, send_from_directory
from src.utils.config import get_config
from src.utils.logger import get_logger
from src.db.mysql_db import init_mysql

logger = get_logger(__name__)


def create_app(config=None) -> Flask:
    """Create and configure Flask application.

    Args:
        config: Configuration override

    Returns:
        Flask application instance
    """
    # Initialize MySQL
    app_config = config or get_config()
    try:
        init_mysql(
            host=app_config.database.mysql_host,
            port=app_config.database.mysql_port,
            user=app_config.database.mysql_user,
            password=app_config.database.mysql_password,
            database=app_config.database.mysql_database
        )
        logger.info("MySQL initialized successfully")
    except Exception as e:
        logger.warning(f"MySQL initialization failed: {e}")

    # Preload stock list cache
    try:
        from src.services.data_provider import StockListProvider
        logger.info("Preloading stock list cache...")
        StockListProvider.load_stock_list_to_db()
        logger.info(f"Stock cache loaded: {StockListProvider.get_stock_count()} stocks")
    except Exception as e:
        logger.warning(f"Stock list preload failed: {e}")

    app = Flask(__name__, static_folder=None)

    # Load configuration
    app.config['SECRET_KEY'] = app_config.app.secret_key
    app.config['DEBUG'] = app_config.app.debug

    # Register blueprints
    from src.api.routes.stock_routes import stock_bp
    from src.api.routes.user_routes import user_bp
    from src.api.routes.news_routes import news_bp
    from src.api.routes.analysis_routes import analysis_bp
    from src.api.routes.agent_routes import agent_bp

    app.register_blueprint(stock_bp, url_prefix='/api/v1')
    app.register_blueprint(user_bp, url_prefix='/api/v1')
    app.register_blueprint(news_bp, url_prefix='/api/v1')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1')
    app.register_blueprint(agent_bp, url_prefix='/api/v1')

    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory(os.path.join(os.path.dirname(__file__), '../../frontend'), 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        frontend_path = os.path.join(os.path.dirname(__file__), '../../frontend')
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path):
            return send_from_directory(frontend_path, path)
        return send_from_directory(frontend_path, 'index.html')

    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'code': 400,
            'message': 'Bad request',
            'error': str(error.description)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': 'Not found',
            'error': str(error.description)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({
            'code': 500,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred'
        }), 500

    logger.info("Flask application created")
    return app


def run_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask application.

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Debug mode
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app()
