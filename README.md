# PayFast

🚀 **PayFast** is a high-performance, strictly asynchronous Core Payment Gateway architecture built natively on FastAPI, PostgreSQL, and Redis. Engineered strictly around rigorous financial principles, it enforces deterministic local-locks ensuring explicit double-entry mathematical integrity throughout thousands of highly concurrent money-transfer threads effortlessly!

The UI layer is managed gracefully in a single **Turborepo** monorepo environment natively orchestrating both **Next.js** (Web) and **Expo / React Native** (Mobile) over unified topologies.

## System Overview

Designed cleanly inside a modular rollout, PayFast natively balances extreme developer scalability bridging rigid real-world infrastructure parameters natively into dynamic Docker configurations.

### Key Features
- **Deterministic Double-Entry Ledger**: Maps transfers safely mapping `SELECT ... FOR UPDATE NOWAIT` preventing transaction deadlocks gracefully!
- **Fraud Engine Signatures**: Dynamically inspects P2P execution triggers evaluating raw request signatures and freezing accounts actively on velocity spikes.
- **Unified Monorepo Architecture**: Manages complex `React 19` and `TypeScript` ecosystems natively orchestrating Next.js and React Native builds simultaneously leveraging **Turborepo** caches out of the box.
- **Premium User Interfaces**: Glassmorphism logic mapping strictly over customized `neon` glow tokens securely rendering interactive high-throughput interfaces flawlessly!
- **WebSocket Webhooks**: Routes real-time JSON pull/collect requests seamlessly to connected native clients securely over WebSockets utilizing strict Token extraction geometries.
- **Idempotency Wrappers**: Enforces a distributed cached locking geometry around execution states preventing duplicate processing vectors if client networks re-request data unexpectedly!

---

## Technical Stack

### Shared / Root Infrastructure
- **Monorepo Manager**: `Turborepo` via native `NPM Workspaces`.
- **Relational Base**: `PostgreSQL 16` paired precisely with `alembic` & `asyncpg`.
- **Cache**: `Redis 7` mapped natively into API `slowapi` boundaries.

### Backend (`src/`)
- **Framework**: `FastAPI` + `uvicorn` (ASGI / asyncio mapping).
- **Asynchronous Execution**: `Celery` + `redis` tracking background Cronjobs securely.
- **Deploy**: Customized `Dockerfile` configurations targeting `Terraform` orchestrators over AWS Fargate natively.

### Frontend Applications (`apps/`)
- **Web App (`apps/web`)**: Next.js 15 App Router natively triggering Server Actions executing exclusively via Vanilla CSS Modules.
- **Mobile App (`apps/mobile`)**: Expo natively integrated via `expo-router` running strictly over 60FPS fluid UI parameters.

---

## Quick Setup

> **Note**: Operating `PayFast` locally actively requires a local execution of Docker configuring internal Postgres architectures natively alongside internal Redis mappings locally before executing APIs successfully.

### 1. Launch Platform Dependencies (Backend)
```bash
docker-compose up -d
```
This securely constructs the Native Postgres execution instance on `5432` and Redis cache target globally.

### 2. Configure Python Backend Target

Execute these sequentially to deploy your Python architectures correctly:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn src.main:app --reload
```

Your API is now active locally natively streaming on `http://127.0.0.1:8000`

### 3. Launch UI Ecosystems (Turborepo)
Launch into standard client parsing sequentially spinning up both the **Next.js Web App** and **React Native Mobile App** in parallel pipelines!

```bash
npm install
npm run dev
```

If you prefer to independently run either ecosystem:
- **Web Only**: `npx turbo run dev --filter=web`
- **Mobile Only**: `npx turbo run dev --filter=mobile`

*(Next.js will naturally bind to `http://localhost:3000` executing seamlessly).*

---

## Code Quality & Builds

We securely wrap all pipelines checking strict TypeScript formatting alongside native python checks!

**Validate TS Compilations (Across Web & Mobile):**
```bash
npx turbo run build
```

**Validate Python Backend Integrity:**
```bash
pytest
```

---

## AWS Containerization Bounds

Deploy natively configuring pure infrastructure configurations dropping components out to external production execution environments seamlessly leveraging Amazon!

1. Compile the framework inside securely built minimal structures:
```bash
docker build -t payfast .
```
2. Navigate securely routing into Amazon structures recursively mapping local states safely:
```bash
cd terraform
terraform init
terraform apply 
```
3. Your CI/CD triggers dynamically execute over local Github hooks inside `.github/workflows/deploy.yml` cleanly.
