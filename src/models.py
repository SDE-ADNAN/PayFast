import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(15), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    is_active = Column(Boolean, nullable=False, default=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True))
    kyc_status = Column(String(20), nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UpiId(Base):
    __tablename__ = "upi_ids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    vpa = Column(String(100), unique=True, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    account_number = Column(String(20), unique=True, nullable=False)
    account_type = Column(String(20), nullable=False, default="savings")
    balance_paise = Column(BigInteger, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(String(20), nullable=False, default="active")
    daily_limit_paise = Column(BigInteger, nullable=False, default=10000000)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(String(100), nullable=False)
    request_hash = Column(String, nullable=False)
    response_status = Column(Integer)
    response_body = Column(JSONB)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idempotency_key_id = Column(UUID(as_uuid=True), ForeignKey("idempotency_keys.id"))
    from_account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT")
    )
    to_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount_paise = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    type = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    failure_reason = Column(String(100))
    description = Column(String)
    metadata_ = Column("metadata", JSONB, default=dict)
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reference_number = Column(String(50), unique=True, nullable=False)
    upi_transaction_id = Column(String(100), unique=True)
    initiated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    completed_at = Column(DateTime(timezone=True))
    version = Column(Integer, nullable=False, default=1)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    entry_type = Column(String(10), nullable=False)
    amount_paise = Column(BigInteger, nullable=False)
    balance_after_paise = Column(BigInteger, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_upi = Column(String(100), nullable=False)
    payer_upi = Column(String(100), nullable=False)
    amount_paise = Column(BigInteger, nullable=False)
    description = Column(String)
    status = Column(String(20), nullable=False, default="pending")
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    responded_at = Column(DateTime(timezone=True))


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash = Column(String, unique=True, nullable=False)
    family_id = Column(UUID(as_uuid=True), nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False)
    user_agent = Column(String)
    ip_address = Column(INET)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )
    raised_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(String(50), nullable=False)
    description = Column(String)
    status = Column(String(20), nullable=False, default="open")
    resolution = Column(String(20))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    resolved_at = Column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )
    rule_triggered = Column(String(100), nullable=False)
    risk_score = Column(SmallInteger, nullable=False)
    auto_blocked = Column(Boolean, nullable=False, default=False)
    reviewed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
