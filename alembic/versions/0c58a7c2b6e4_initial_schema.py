"""initial_schema

Revision ID: 0c58a7c2b6e4
Revises: 
Create Date: 2026-04-03 01:23:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c58a7c2b6e4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
-- ──────────────────────────────────────────────────────────────
-- EXTENSIONS
-- ──────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";     -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- fuzzy search on VPAs

-- ──────────────────────────────────────────────────────────────
-- USERS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone           VARCHAR(15) UNIQUE NOT NULL,       -- E.164 format: +919876543210
    email           VARCHAR(255) UNIQUE,
    full_name       VARCHAR(255) NOT NULL,
    password_hash   TEXT NOT NULL,                     -- Argon2id hash
    role            VARCHAR(20) NOT NULL DEFAULT 'customer'
                        CHECK (role IN ('customer', 'merchant', 'admin')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_locked       BOOLEAN NOT NULL DEFAULT FALSE,    -- brute-force lockout
    failed_attempts INT NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    kyc_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (kyc_status IN ('pending', 'verified', 'rejected')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);

-- ──────────────────────────────────────────────────────────────
-- UPI IDs (Virtual Payment Addresses)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE upi_ids (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id  UUID NOT NULL,                          -- FK added after accounts table
    vpa         VARCHAR(100) UNIQUE NOT NULL,           -- e.g. alice@payfast
    is_primary  BOOLEAN NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Only one primary VPA per user
CREATE UNIQUE INDEX idx_upi_primary ON upi_ids(user_id) WHERE is_primary = TRUE;
CREATE INDEX idx_upi_vpa ON upi_ids(vpa);              -- hot lookup path

-- ──────────────────────────────────────────────────────────────
-- ACCOUNTS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    account_number  VARCHAR(20) UNIQUE NOT NULL,        -- system-generated
    account_type    VARCHAR(20) NOT NULL DEFAULT 'savings'
                        CHECK (account_type IN ('savings', 'current', 'wallet')),
    -- Balance stored in SMALLEST UNIT (paise for INR, cents for USD)
    -- NEVER store floats for money. BIGINT = paise.
    balance_paise   BIGINT NOT NULL DEFAULT 0
                        CHECK (balance_paise >= 0),    -- enforced at DB level too
    currency        CHAR(3) NOT NULL DEFAULT 'INR',
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'frozen', 'closed')),
    daily_limit_paise   BIGINT NOT NULL DEFAULT 10000000,  -- 1 lakh INR default
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add FK from upi_ids to accounts (after accounts table exists)
ALTER TABLE upi_ids ADD CONSTRAINT fk_upi_account
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT;

CREATE INDEX idx_accounts_user ON accounts(user_id);

-- ──────────────────────────────────────────────────────────────
-- IDEMPOTENCY KEYS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE idempotency_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key             VARCHAR(255) UNIQUE NOT NULL,       -- client-provided SHA-256 key
    user_id         UUID NOT NULL REFERENCES users(id),
    endpoint        VARCHAR(100) NOT NULL,              -- e.g. POST /payments/transfer
    request_hash    TEXT NOT NULL,                      -- SHA-256 of request body
    response_status INT,
    response_body   JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);  -- for cleanup

-- ──────────────────────────────────────────────────────────────
-- TRANSACTIONS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key_id  UUID REFERENCES idempotency_keys(id),
    from_account_id     UUID REFERENCES accounts(id) ON DELETE RESTRICT,
    to_account_id       UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    amount_paise        BIGINT NOT NULL CHECK (amount_paise > 0),
    currency            CHAR(3) NOT NULL DEFAULT 'INR',
    type                VARCHAR(30) NOT NULL
                            CHECK (type IN (
                                'p2p_transfer',
                                'collect_payment',
                                'merchant_payment',
                                'refund',
                                'reversal',
                                'system_credit',
                                'system_debit'
                            )),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN (
                                'pending',
                                'processing',
                                'success',
                                'failed',
                                'reversed',
                                'disputed'
                            )),
    failure_reason      VARCHAR(100),                   -- enum of known fail codes
    description         TEXT,
    metadata            JSONB DEFAULT '{}',             -- device_id, ip, etc.
    initiated_by        UUID REFERENCES users(id),      -- who pressed "Pay"
    reference_number    VARCHAR(50) UNIQUE NOT NULL,    -- human-readable UTR-style ref
    upi_transaction_id  VARCHAR(100) UNIQUE,            -- if integrating with real UPI
    initiated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    -- Optimistic locking version for concurrent updates
    version             INT NOT NULL DEFAULT 1
);

-- Critical indexes for performance
CREATE INDEX idx_txn_from_account   ON transactions(from_account_id, initiated_at DESC);
CREATE INDEX idx_txn_to_account     ON transactions(to_account_id, initiated_at DESC);
CREATE INDEX idx_txn_status         ON transactions(status) WHERE status = 'pending';
CREATE INDEX idx_txn_reference      ON transactions(reference_number);
CREATE INDEX idx_txn_initiated_by   ON transactions(initiated_by, initiated_at DESC);

-- ──────────────────────────────────────────────────────────────
-- LEDGER ENTRIES (Double-Entry)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE ledger_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id),
    account_id      UUID NOT NULL REFERENCES accounts(id),
    entry_type      VARCHAR(10) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount_paise    BIGINT NOT NULL CHECK (amount_paise > 0),
    balance_after_paise BIGINT NOT NULL,                -- snapshot of balance after this entry
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- For every transaction_id, SUM(debit) MUST equal SUM(credit) — enforced in application layer
CREATE INDEX idx_ledger_account     ON ledger_entries(account_id, created_at DESC);
CREATE INDEX idx_ledger_transaction ON ledger_entries(transaction_id);

-- ──────────────────────────────────────────────────────────────
-- PAYMENT REQUESTS (Collect Flow)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE payment_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_upi   VARCHAR(100) NOT NULL,              -- who is requesting money
    payer_upi       VARCHAR(100) NOT NULL,              -- who should pay
    amount_paise    BIGINT NOT NULL CHECK (amount_paise > 0),
    description     TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled')),
    transaction_id  UUID REFERENCES transactions(id),  -- set on approval
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '15 minutes',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at    TIMESTAMPTZ
);

CREATE INDEX idx_pr_payer  ON payment_requests(payer_upi, status);
CREATE INDEX idx_pr_expire ON payment_requests(expires_at) WHERE status = 'pending';

-- ──────────────────────────────────────────────────────────────
-- REFRESH TOKENS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT UNIQUE NOT NULL,                   -- SHA-256 of the actual token
    family_id   UUID NOT NULL,                          -- for refresh token rotation detection
    is_revoked  BOOLEAN NOT NULL DEFAULT FALSE,
    user_agent  TEXT,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '30 days'
);

CREATE INDEX idx_rt_user    ON refresh_tokens(user_id);
CREATE INDEX idx_rt_family  ON refresh_tokens(family_id);   -- detect token reuse

-- ──────────────────────────────────────────────────────────────
-- DISPUTES
-- ──────────────────────────────────────────────────────────────
CREATE TABLE disputes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id),
    raised_by       UUID NOT NULL REFERENCES users(id),
    reason          VARCHAR(50) NOT NULL
                        CHECK (reason IN (
                            'unauthorized_transaction',
                            'double_charge',
                            'amount_mismatch',
                            'service_not_received',
                            'other'
                        )),
    description     TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'under_review', 'resolved', 'rejected')),
    resolution      VARCHAR(20)
                        CHECK (resolution IN ('refund_issued', 'no_action', 'partial_refund')),
    resolved_by     UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

-- ──────────────────────────────────────────────────────────────
-- AUDIT LOG
-- ──────────────────────────────────────────────────────────────
CREATE TABLE audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id    UUID REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,                  -- e.g. 'account.freeze', 'dispute.resolve'
    target_type VARCHAR(50),                            -- e.g. 'account', 'user'
    target_id   UUID,
    old_value   JSONB,
    new_value   JSONB,
    ip_address  INET,
    user_agent  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_actor  ON audit_log(actor_id, created_at DESC);
CREATE INDEX idx_audit_target ON audit_log(target_type, target_id);

-- ──────────────────────────────────────────────────────────────
-- FRAUD FLAGS
-- ──────────────────────────────────────────────────────────────
CREATE TABLE fraud_flags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id),
    rule_triggered  VARCHAR(100) NOT NULL,              -- e.g. 'velocity_5_per_min'
    risk_score      SMALLINT NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    auto_blocked    BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
    """)


def downgrade() -> None:
    op.execute("""
DROP TABLE IF EXISTS fraud_flags CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS disputes CASCADE;
DROP TABLE IF EXISTS refresh_tokens CASCADE;
DROP TABLE IF EXISTS payment_requests CASCADE;
DROP TABLE IF EXISTS ledger_entries CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS idempotency_keys CASCADE;
ALTER TABLE IF EXISTS upi_ids DROP CONSTRAINT IF EXISTS fk_upi_account;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS upi_ids CASCADE;
DROP TABLE IF EXISTS users CASCADE;
    """)
