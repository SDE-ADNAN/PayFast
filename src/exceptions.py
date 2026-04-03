class PayFastError(Exception):
    """Base exception for PayFast application."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InsufficientFundsError(PayFastError):
    def __init__(self, message: str = "Insufficient funds", **kwargs: object):
        super().__init__(message, code="INSUFFICIENT_FUNDS")
        self.details = kwargs


class AccountFrozenError(PayFastError):
    def __init__(self, message: str = "Account is frozen", **kwargs: object):
        super().__init__(message, code="ACCOUNT_FROZEN")
        self.details = kwargs


class ConcurrentModificationError(PayFastError):
    def __init__(
        self,
        message: str = "Concurrent modification detected. Please try again.",
        **kwargs: object,
    ):
        super().__init__(message, code="LOCK_TIMEOUT")
        self.details = kwargs


class DailyLimitExceededError(PayFastError):
    def __init__(self, message: str = "Daily limit exceeded", **kwargs: object):
        super().__init__(message, code="DAILY_LIMIT_EXCEEDED")
        self.details = kwargs
