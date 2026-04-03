from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from src.models import Account, LedgerEntry, Transaction
from src.exceptions import InsufficientFundsError, AccountFrozenError, ConcurrentModificationError

async def post_double_entry(
    session: AsyncSession,
    transaction: Transaction,
    from_account_id: UUID,
    to_account_id: UUID,
    amount_paise: int,
) -> tuple[LedgerEntry, LedgerEntry]:
    """
    Core ledger function. MUST be called inside an existing DB transaction.
    Uses SELECT FOR UPDATE NOWAIT to lock both accounts in a consistent
    order (lower UUID first) to prevent deadlocks.
    """
    account_ids = sorted([from_account_id, to_account_id])
    
    try:
        stmt = (
            select(Account)
            .where(Account.id.in_(account_ids))
            .with_for_update(nowait=True)
            .order_by(Account.id)
        )
        result = await session.execute(stmt)
        accounts = {a.id: a for a in result.scalars().all()}
    except DBAPIError as e:
        # Psql gives 55P03 for lock_not_available
        if "55P03" in str(e):
            raise ConcurrentModificationError()
        raise

    if len(accounts) != 2:
        raise ValueError("One or both accounts not found")
        
    from_account = accounts[from_account_id]
    to_account = accounts[to_account_id]
    
    # 2. Validate
    if from_account.status != 'active':
        raise AccountFrozenError(f"Source account is {from_account.status}")
    if to_account.status == 'closed':
        raise ValueError("Destination account is closed")
        
    # 3. Check balance
    if from_account.balance_paise < amount_paise: # type: ignore
        raise InsufficientFundsError(
            available=from_account.balance_paise,
            required=amount_paise
        )
        
    # 4. Apply
    from_account.balance_paise -= amount_paise # type: ignore
    to_account.balance_paise += amount_paise # type: ignore
    
    # 5. Ledger Entries
    debit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=from_account_id,
        entry_type='debit',
        amount_paise=amount_paise,
        balance_after_paise=from_account.balance_paise,
    )
    credit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=to_account_id,
        entry_type='credit',
        amount_paise=amount_paise,
        balance_after_paise=to_account.balance_paise,
    )
    
    session.add_all([debit_entry, credit_entry])
    return debit_entry, credit_entry

async def verify_ledger_integrity(session: AsyncSession, account_id: UUID) -> bool:
    """
    Recomputes balance from ledger history and compares to accounts.balance_paise.
    """
    result = await session.execute(
        text("""
            SELECT
                SUM(CASE WHEN entry_type = 'credit' THEN amount_paise ELSE 0 END) -
                SUM(CASE WHEN entry_type = 'debit'  THEN amount_paise ELSE 0 END) AS computed_balance
            FROM ledger_entries
            WHERE account_id = :account_id
        """),
        {"account_id": str(account_id)}
    )
    computed = result.scalar_one() or 0
    
    account = await session.get(Account, account_id)
    if not account:
        return False
        
    return int(computed) == int(account.balance_paise) # type: ignore
