# PayFast

🚀 **PayFast** is a high-performance, strictly asynchronous Core Payment Gateway architecture built natively on FastAPI, PostgreSQL, and Redis. Engineered strictly around rigorous financial principles, it enforces deterministic local-locks ensuring explicit double-entry mathematical integrity throughout thousands of highly concurrent money-transfer threads effortlessly!

## System Overview

Designed cleanly inside a 7-Phase modular rollout, PayFast natively balances extreme developer scalability bridging rigid real-world infrastructure parameters natively into dynamic Docker configurations.

### Key Features
- **Deterministic Double-Entry Ledger**: Maps transfers safely mapping `SELECT ... FOR UPDATE NOWAIT` inside strictly ordered UUID configurations preventing transaction deadlocks gracefully!
- **Fraud Engine Signatures**: Dynamically inspects P2P execution triggers evaluating raw request signatures and temporal speed checks (Velocity Bounds) actively freezing accounts blocking large payload attacks immediately!
- **Idempotency Wrappers**: Enforces a distributed cached locking geometry around execution states preventing duplicate processing vectors if client networks re-request data unexpectedly!
- **WebSocket Webhooks**: Routes real-time JSON pull/collect requests seamlessly to connected native clients securely over WebSockets utilizing strict Token extraction geometries natively inside ASGI routines!
- **Native PDF Streaming**: Configures raw historical transaction offsets emitting generated HTML logic seamlessly wrapping `weasyprint` dynamically exposing statement PDFs! 
- **HMAC Triggers**: Autonomously structures Webhook outputs targeting massive outbound event endpoints explicitly via `Celery` task threads wrapped in `X-PayFast-Signature` hashes executing safely via delayed retries!
- **Dynamic QR Ecosystems**: Embeds dynamic URI targets inside heavily formatted HTTP payloads implicitly streaming raw `image/png` maps formatted precisely for user phones dynamically generating endpoints on load!

---

## Technical Stack

- **Framework**: `FastAPI` + `uvicorn` (ASGI / asyncio mapping).
- **Relational Data Base**: `PostgreSQL 16` paired precisely with `alembic` & `asyncpg`.
- **Cache / Distributed Locks**: `Redis 7` mapped natively into API `slowapi` boundaries.
- **Asynchronous Execution Manager**: `Celery` + `redis` acting specifically tracking background Cronjobs securely natively wrapping `acks_late=True` queue execution routines.
- **Cryptography & Tokens**: Custom integration generating ephemeral RS256 token mappings validating dynamically against raw `argon2` authentication wrappers.
- **Observability**: Raw structural processing mapped universally over `structlog` & explicit Metric hooks outputting Prometheus compatible endpoint mappings transparently dynamically scaling into Grafana bounds locally.
- **Container Infrastructure**: Terraform topologies built purely structurally targeting Fargate executing ECS deployment models automatically linked safely inside customized minimal `Dockerfile` bindings utilizing continuous `OIDC` GitHub integrations!

---

## Quick Setup

> **Note**: Operating `PayFast` locally actively requires a local execution of Docker configuring internal Postgres architectures natively alongside internal Redis mappings locally before executing APIs successfully to prevent local binding failures!

### 1. Launch Platform Dependencies
```bash
docker-compose up -d
```
This securely constructs the `10.x` native Postgres execution instance bounding internal data targets natively securely onto `5432`.

### 2. Configure Python Topologies
Configure native testing sets properly evaluating local system configurations:
*(If generating transaction PDFs, natively install `pango`/`cairo` locally!)*
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Apply Schema Topology
```bash
alembic upgrade head
```

### 4. Execute Backend Target
```bash
uvicorn src.main:app --reload
```

Your system is officially active! Launch into standard endpoint parsing locally explicitly:
- **Telemetry Specifications**: `http://localhost:8000/metrics`
- **Application Endpoints**: `http://localhost:8000/docs`
- **Component Renderings**: `http://localhost:8000/redoc`

---

## AWS Containerization Bounds

Deploy natively configuring pure infrastructure configurations natively dropping components out to external production execution environments seamlessly leveraging Amazon!

1. Compile the framework inside securely built minimal structures mapping out execution parameters securely via:
```bash
docker build -t payfast .
```
2. Navigate securely routing into Amazon structures implicitly initializing local contexts transparently mapping secure state definitions safely:
```bash
cd terraform
terraform init
terraform apply 
```
3. Watch out your execution routines run dynamically over local Github hooks executing natively inside `.github/workflows/deploy.yml` cleanly pushing securely!

---

## Development & Test

We natively assert functionality executing rigorous synchronous bindings checking logic safely simulating test clients properly against WebSocket logic dynamically mapping routes optimally:

```bash
pytest
```
