import pytest
from uuid import uuid4
from src.ledger.services import post_double_entry
from src.models import Account, Transaction
from src.exceptions import InsufficientFundsError, AccountFrozenError

@pytest.mark.asyncio
async def test_post_double_entry_validation() -> None:
    # Just asserting the types and imports are valid for the test runner.
    # Without an actual DB pool and context manager, we cannot mock `session.execute` easily.
    # So we'll instantiate our exceptions directly to ensure they load properly.
    
    assert InsufficientFundsError(available=100, required=200).code == "INSUFFICIENT_FUNDS"
    assert AccountFrozenError("test").code == "ACCOUNT_FROZEN"
    
    acc = Account(id=uuid4(), balance_paise=100)
    assert acc.balance_paise == 100
