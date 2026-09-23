# PRAGYA: AI-Powered Competency & Workforce Intelligence Platform

> **Problem Statement:** SIH26101  
> **Supporting Phrase:** *Assess • Learn • Improve • Predict*  
> **Domain:** Capacity Building in India's Official Statistical System (MoSPI)

---

## 1. Project Overview

**PRAGYA** is an AI-powered competency-based personalized learning and workforce intelligence platform custom-designed for the officers, researchers, and field personnel of India's Official Statistical System.

The platform is **NOT a generic LMS** and **NOT a generic chatbot**. It operates on an evidence-based, closed-loop competency cycle:

$$\text{Role Requirements} \longrightarrow \text{Competency Assessment} \longrightarrow \text{Evidence-Based Profile} \longrightarrow \text{Skill Gap Analysis} \longrightarrow \text{Prioritization} \longrightarrow \text{Personalized Learning} \longrightarrow \text{AI Assistance} \longrightarrow \text{Recalibration} \longrightarrow \text{Workforce Intelligence}$$

> [!NOTE]
> **Implementation Status:** Stages 1, 2, 3, and 4 are complete and fully verified.
> - **Stage 1 (Application Foundation)**: Monorepo, Next.js 16 frontend, FastAPI backend, PostgreSQL database, and native Windows runner.
> - **Stage 2 (Design System & Dual-Persona Navigation)**: Full design system, dark glassmorphism aesthetic, 25 application route shells.
> - **Stage 3 (Real Employee Domain & PostgreSQL Foundation)**: `departments`, `job_roles`, `employees`, and `training_history` relational models with real live database connection.
> - **Stage 4 (Competency Dictionary, Framework & Role Mapping)**: Approved SIH26101 4-domain taxonomy (33 competencies), 5-level proficiency model (0–100 score ranges), role requirement matrix for 5 cadre roles, competency relationships graph, and course mapping abstraction. Real `/employee/competency` and `/admin/competencies` views live.
> Future domain capabilities (skill-gap engine, adaptive assessment, RAG assistant, recommendation ranking) will be added in subsequent stages.

---

## 2. Architecture

PRAGYA is structured as a **Modular Monolith** with an AI Service Layer:
- **Shared Unified Backend:** Single source of truth for competency models, evidence scoring, learning catalogs, and analytics.
- **Unified Dual-Persona Frontend:** 
  - **Employee / Learner View:** Focuses on *"What should I learn next?"*
  - **Administrator / Workforce Training Manager View:** Focuses on *"What does my workforce need next?"*
- **AI Engine Abstraction:** Decoupled `LLMProvider` and `EmbeddingProvider` protocols ensuring vendor independence (native Ollama, local open-weight LLMs, or mock providers).
- **Integration Layer:** Adapter pattern abstracting future government ecosystem endpoints (iGOT Karmayogi, NSSTA / TPAC) with mock development providers.
- **Native Windows Execution:** All services (Next.js, FastAPI, PostgreSQL, Ollama) run natively on Windows during development without Docker or container virtualization overhead.

```text
┌────────────────────────────────────────────────────────┐
│             PRAGYA Frontend (Next.js 16)               │
│    Employee View               Administrator View      │
│  "What should I learn next?"    "What does workforce   │
│                                      need next?"       │
└──────────────────────────┬─────────────────────────────┘
                           │ REST / JSON (JWT / RBAC)
┌──────────────────────────▼─────────────────────────────┐
│              PRAGYA Backend API (FastAPI)              │
│  Core Modules:                                         │
│  ├── Identity & RBAC       ├── Recommendation Engine   │
│  ├── Competencies (MoSPI)  ├── Grounded RAG Assistant  │
│  ├── Skill Gap Engine      ├── Workforce Analytics     │
│  └── Assessment Engine     └── Ecosystem Adapters      │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
┌─────────────▼──────────────┐ ┌──────────▼──────────────┐
│ Native Windows PostgreSQL  │ │ Native AI Service Layer │
│   16 + pgvector extension  │ │ (Ollama on Windows/Py)  │
└────────────────────────────┘ └─────────────────────────┘
```

---

## 3. Technology Stack (Locked)

| Layer | Technologies | Development Mode |
| :--- | :--- | :--- |
| **Frontend** | TypeScript, Next.js 16 (App Router), Tailwind CSS v4, Lucide React, Framer Motion, Recharts, TanStack Query, React Hook Form, Zod | Native Windows (`npm run dev`) |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Pytest, HTTPX | Native Windows (`uvicorn app.main:app --reload`) |
| **Database & Search** | Native PostgreSQL 16 on Windows with `pgvector` extension | Native Windows Service (`localhost:5432`) |
| **AI / ML Layer** | `LLMProvider` / `EmbeddingProvider` abstractions, Native Ollama / HuggingFace Transformers | Native Windows Service (`localhost:11434`) |
| **Document Processing** | PyMuPDF, python-pptx, FFmpeg + faster-whisper (Architecture ready) | Native Python libraries |

---

## 4. Folder Structure

```text
PRAGYA/
├── apps/
│   ├── web/                     # Next.js App Router Frontend
│   │   ├── app/                 # App Router (/, /login, /employee, /admin)
│   │   ├── components/          # Reusable UI & Providers
│   │   ├── lib/                 # API client utilities
│   │   ├── styles/              # Global styles & design tokens
│   │   └── package.json
│   └── api/                     # FastAPI Backend
│       ├── app/
│       │   ├── core/            # Config, logging, security, exceptions
│       │   ├── db/              # SQLAlchemy session & Base
│       │   ├── api/             # API v1 routers & dependencies
│       │   ├── modules/         # Domain-driven modular monolith modules
│       │   └── main.py          # App entrypoint
│       ├── tests/               # Pytest suite
│       ├── alembic/             # Database migration scripts
│       ├── requirements.txt
│       └── .venv/               # Dedicated Python 3.11 Virtual Environment
├── packages/
│   ├── types/                   # Shared TypeScript domain contracts
│   ├── ui/                      # Shared UI primitives
│   └── config/                  # Shared configuration
├── data/
│   ├── seed/                    # MoSPI official competency seeds
│   ├── mock/                    # Mock iGOT & NSSTA payloads
│   └── documents/               # Statistical training reference docs
├── docs/                        # Architecture & API specifications
├── scripts/                     # Automation & migration scripts
├── .env.example                 # Environment configuration template
├── package.json                 # Monorepo workspaces definition
└── README.md
```

---

## 5. Prerequisites

- **Node.js**: `v20.x` or `v24.x` (Active: `v24.19.0`)
- **npm**: `v10.x` or `v11.x` (Active: `11.17.0`)
- **Python**: `3.11.x` (Active virtual environment locked to CPython 3.11 via `uv`)
- **uv**: Astral `uv` package manager (Active: `0.12.5`)
- **Git**: `2.x` (Active: `2.55.0`)
- **PostgreSQL**: Native PostgreSQL 16+ on Windows with `pgvector` extension
- **Ollama**: (Optional for later stages) Native Ollama Windows installer

---

## 6. Environment Setup

Copy `.env.example` to `.env` in the repository root:

```powershell
Copy-Item .env.example .env
```

Configure your native Windows PostgreSQL credentials in `.env`:
```ini
# Format: postgresql://<username>:<password>@localhost:5432/pragya
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pragya
VECTOR_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pragya
```

---

## 7. Frontend Startup (Native Windows)

Open a VS Code terminal window:

```powershell
cd apps/web
npm install
npm run dev
```

The PRAGYA frontend portal will be live at [http://localhost:3000](http://localhost:3000).

---

## 8. Backend Startup (Native Windows)

Open a separate VS Code terminal window:

```powershell
cd apps/api

# Activate Python 3.11 virtual environment
.\.venv\Scripts\activate

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```

Backend endpoints will be available at:
- Interactive Swagger API Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Root Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- V1 Subsystem Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

*(Note: Python IDLE may be used for standalone Python experimentation, but the main application backend should be executed and tested via VS Code terminal + Uvicorn).*

---

## 9. Native PostgreSQL Database Setup

1. In native PostgreSQL (pgAdmin or psql on Windows), create the database:
   ```sql
   CREATE DATABASE pragya;
   \c pragya;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. Run database migrations via Alembic:
   ```powershell
   cd apps/api
   .\.venv\Scripts\activate
   alembic upgrade head
   ```

---

## 10. Health Check Endpoints

- **Root Health:** `GET http://localhost:8000/health`
  ```json
  {
    "status": "ok",
    "service": "pragya-api",
    "version": "0.1.0"
  }
  ```
- **V1 Subsystem Health:** `GET http://localhost:8000/api/v1/health`
  ```json
  {
    "status": "ok",
    "service": "pragya-api",
    "version": "0.1.0",
    "environment": "development",
    "database": {
      "connected": true,
      "dialect": "postgresql"
    }
  }
  ```

---

## 11. Development Commands Summary

From monorepo root:
- **Run Frontend:** `npm run dev:web` (or `cd apps/web && npm run dev`)
- **Build Frontend:** `npm run build:web`
- **Run Backend:** `npm run dev:api` (or `cd apps/api && .\.venv\Scripts\activate && uvicorn app.main:app --reload --port 8000`)
- **Run Backend Tests:** `npm run test:api` (or `cd apps/api && uv run pytest tests/`)

---

---

## 13. Stage 3: Employee Domain & Database Foundation

### 13.1 Database Tables (PostgreSQL 18.6)
- `departments`: Statistical system divisions (DES, NAD, NSSO, PCLD, CPD).
- `job_roles`: Cadre levels and roles (Statistical Officer, Senior Statistical Officer, etc.).
- `employees`: Official personnel profiles with foreign keys to department, current role, target role.
- `training_history`: Verified learning records with cascading relationship to employee.

### 13.2 Database Migration & Seeding
```bash
# Run Alembic migrations
cd apps/api
.venv/Scripts/alembic upgrade head

# Run Idempotent Seed Command (Synthetic Demonstration Data)
.venv/Scripts/python -m app.db.seed
```

### 13.3 Endpoints
- `GET /api/v1/employees/me`: Primary demo officer profile (Ananya Sharma - EMP-0001)
- `GET /api/v1/employees/{id}`: Specific officer profile by UUID
- `PATCH /api/v1/employees/{id}`: Update editable fields (assignment, education, experience, language, target role)
- `GET /api/v1/employees/{id}/training-history`: Verified training records
- `GET /api/v1/departments`: Active departments
- `GET /api/v1/job-roles`: Active job roles

### 13.4 Frontend Profile UI
- Real database-backed `/employee/profile` powered by TanStack Query.
- Profile Hero, 6 domain sections, and interactive "Edit Profile" modal with React Hook Form and Zod.

