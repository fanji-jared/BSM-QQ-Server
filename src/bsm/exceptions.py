class BSMError(Exception):
    """Base exception for BSM API errors"""
    pass


class BSMAuthenticationError(BSMError):
    """Authentication failed"""
    pass


class BSMConnectionError(BSMError):
    """Connection to BSM API failed"""
    pass


class BSMNotFoundError(BSMError):
    """Resource not found"""
    pass


class BSMPermissionError(BSMError):
    """Permission denied"""
    pass


class BSMServerError(BSMError):
    """Server error from BSM API"""
    pass
