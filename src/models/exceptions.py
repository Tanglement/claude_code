"""Custom exceptions for the stock information system."""


class StockSystemError(Exception):
    """Base exception for stock system."""
    pass


class DatabaseError(StockSystemError):
    """Database operation error."""
    pass


class StockNotFoundError(StockSystemError):
    """Stock not found error."""

    def __init__(self, symbol: str = None):
        self.symbol = symbol
        message = f"Stock not found: {symbol}" if symbol else "Stock not found"
        super().__init__(message)


class UserNotFoundError(StockSystemError):
    """User not found error."""

    def __init__(self, username: str = None):
        self.username = username
        message = f"User not found: {username}" if username else "User not found"
        super().__init__(message)


class AuthenticationError(StockSystemError):
    """Authentication error (invalid credentials)."""
    pass


class AuthorizationError(StockSystemError):
    """Authorization error (permission denied)."""
    pass


class DataSourceError(StockSystemError):
    """Data source error (external API failure)."""
    pass


class ValidationError(StockSystemError):
    """Input validation error."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on {field}: {message}")


class CacheError(StockSystemError):
    """Cache operation error."""
    pass


class ConfigurationError(StockSystemError):
    """Configuration error."""
    pass


class DuplicateError(StockSystemError):
    """Duplicate record error."""

    def __init__(self, entity: str, field: str = None):
        self.entity = entity
        self.field = field
        message = f"{entity} already exists"
        if field:
            message += f" ({field})"
        super().__init__(message)
