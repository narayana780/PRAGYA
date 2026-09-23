# PRAGYA Employee Domain & Organizational Reference Data

> **Stage 3 Documentation**  
> Notice: SYNTHETIC DEMONSTRATION DATA — NOT REAL GOVERNMENT DATA.  
> All personnel records, names, employee codes, designations, and training histories are synthetic artifacts created strictly for testing and demonstrating the PRAGYA Competency & Workforce Intelligence Platform.

---

## 1. Domain Overview

The Employee Domain represents the foundational business domain of PRAGYA. It introduces real relational entities in PostgreSQL managed by SQLAlchemy 2.0 and versioned by Alembic, serving data through FastAPI REST endpoints to the Next.js frontend.

```
┌─────────────────┐       ┌─────────────────┐
│   departments   │       │    job_roles    │
└────────┬────────┘       └────────┬────────┘
         │ 1                       │ 1
         │                         ├── (current role)
         │                         ├── (target role)
         ▼ *                       ▼ *
┌───────────────────────────────────────────┐
│                 employees                 │
└─────────────────────┬─────────────────────┘
                      │ 1
                      ▼ *
┌───────────────────────────────────────────┐
│             training_history              │
└───────────────────────────────────────────┘
```

---

## 2. Database Tables & Schema

All primary keys use native PostgreSQL `UUID` (`uuid_generate_v4` / `uuid.uuid4()`).

### 2.1 `departments`
Stores official administrative and statistical divisions within the statistical system (e.g., MoSPI).
- `id` (UUID, Primary Key)
- `name` (String 150, Unique, Not Null)
- `code` (String 50, Unique, Not Null, e.g. `DES`, `NAD`, `NSSO`)
- `description` (Text, Nullable)
- `is_active` (Boolean, Default `True`, Not Null)
- `created_at` (DateTime with TimeZone, Server Default `now()`)
- `updated_at` (DateTime with TimeZone, Server Default `now()`, OnUpdate `now()`)

### 2.2 `job_roles`
Defines official statistical cadre levels and roles.
- `id` (UUID, Primary Key)
- `name` (String 150, Not Null, e.g. `Statistical Officer`, `Senior Statistical Officer`)
- `code` (String 50, Unique, Not Null, e.g. `SO`, `SSO`, `AD`, `DD`, `JD`)
- `description` (Text, Nullable)
- `career_level` (String 50, Not Null, e.g. `Level 8`, `Level 10`)
- `is_active` (Boolean, Default `True`, Not Null)
- `created_at` (DateTime with TimeZone, Server Default `now()`)
- `updated_at` (DateTime with TimeZone, Server Default `now()`, OnUpdate `now()`)

### 2.3 `employees`
Core cadre personnel records.
- `id` (UUID, Primary Key)
- `employee_code` (String 50, Unique, Indexed, Not Null, e.g. `EMP-0001`)
- `user_id` (UUID, Nullable — reserved for future authentication identity)
- `full_name` (String 150, Not Null)
- `designation` (String 100, Not Null)
- `department_id` (UUID, Foreign Key `departments.id`, Indexed, Not Null)
- `job_role_id` (UUID, Foreign Key `job_roles.id`, Indexed, Not Null)
- `current_assignment` (String 255, Nullable)
- `education` (String 255, Nullable)
- `experience_years` (Integer, Check Constraint `0 <= experience_years <= 50`, Default `0`)
- `preferred_language` (String 50, Default `'English'`, Not Null)
- `target_role_id` (UUID, Foreign Key `job_roles.id`, Nullable)
- `profile_image_url` (String 500, Nullable)
- `is_active` (Boolean, Default `True`, Not Null)
- `created_at` (DateTime with TimeZone, Server Default `now()`)
- `updated_at` (DateTime with TimeZone, Server Default `now()`, OnUpdate `now()`)

### 2.4 `training_history`
Verified historical courses and programmes completed by officers across ecosystem providers.
- `id` (UUID, Primary Key)
- `employee_id` (UUID, Foreign Key `employees.id` ON DELETE CASCADE, Indexed, Not Null)
- `title` (String 255, Not Null)
- `provider` (String 100, Not Null, e.g. `iGOT Karmayogi`, `NSSTA`)
- `provider_type` (String 50, Not Null, e.g. `IGOT`, `NSSTA_TPAC`, `OTHER`)
- `course_id` (String 100, Nullable)
- `programme_id` (String 100, Nullable)
- `completed_at` (DateTime with TimeZone, Nullable)
- `status` (String 50, Default `'COMPLETED'`, Not Null)
- `score` (Float, Nullable)
- `duration_hours` (Float, Nullable)
- `certificate_reference` (String 150, Nullable)
- `created_at` (DateTime with TimeZone, Server Default `now()`)
- `updated_at` (DateTime with TimeZone, Server Default `now()`, OnUpdate `now()`)

---

## 3. Database Seeding

The seed script is idempotent and can be executed anytime to populate or verify demo reference data.

### Seed Execution Command:
```bash
# From apps/api directory:
.venv/Scripts/python -m app.db.seed
```

### Seeded Entities:
- **5 Departments**:
  - `DES`: Department of Economics and Statistics
  - `NAD`: National Accounts Division
  - `NSSO`: National Sample Survey Office
  - `PCLD`: Price & Cost of Living Division
  - `CPD`: Coordination & Publication Division
- **5 Job Roles**:
  - `SO`: Statistical Officer (Level 8)
  - `SSO`: Senior Statistical Officer (Level 10)
  - `AD`: Assistant Director (Level 11)
  - `DD`: Deputy Director (Level 12)
  - `JD`: Joint Director (Level 13)
- **4 Synthetic Employees**:
  - **Primary Demo**: Ananya Sharma (`EMP-0001`), Statistical Officer, DES, M.Sc. Statistics, 5 yrs exp, Target: Senior Statistical Officer, Assignment: Survey Data Analysis
  - Rajesh Verma (`EMP-0002`), Senior Statistical Officer, NAD, Ph.D. Economics, 9 yrs exp
  - Priya Patel (`EMP-0003`), Assistant Director, NSSO, M.Stat. (ISI), 12 yrs exp
  - Vikram Malhotra (`EMP-0004`), Statistical Officer, PCLD, M.Sc. Applied Statistics, 3 yrs exp
- **12 Synthetic Training Records** across iGOT and NSSTA.

---

## 4. REST API Contract

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Description | Response Status |
|---|---|---|---|
| `GET` | `/api/v1/employees/me` | Current demo officer profile (`EMP-0001`) | `200 OK` |
| `GET` | `/api/v1/employees/{id}` | Officer profile by unique UUID | `200 OK` / `404` |
| `PATCH` | `/api/v1/employees/{id}` | Update editable profile attributes | `200 OK` / `400` / `404` |
| `GET` | `/api/v1/employees/{id}/training-history` | List verified training history records | `200 OK` / `404` |
| `GET` | `/api/v1/departments` | List all active statistical departments | `200 OK` |
| `GET` | `/api/v1/job-roles` | List all official job roles and levels | `200 OK` |

### Allowed PATCH Fields:
- `current_assignment` (string, max 255 chars)
- `education` (string, max 255 chars)
- `experience_years` (integer, 0 - 50)
- `preferred_language` (string from supported official languages)
- `target_role_id` (UUID, validated against active `job_roles`)

### Error Format:
```json
{
  "success": false,
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "Employee with ID '...' was not found."
  }
}
```

---

## 5. Frontend Integration Flow

```
Next.js Profile Page (/employee/profile)
       │
       ├── useCurrentEmployee() (TanStack Query)
       │      └── GET /api/v1/employees/me
       │
       ├── useEmployeeTrainingHistory() (TanStack Query)
       │      └── GET /api/v1/employees/{id}/training-history
       │
       └── Edit Profile Interaction (EditProfileModal)
              ├── React Hook Form + Zod Validation
              ├── useJobRoles() (Populates Target Cadre dropdown)
              └── useUpdateEmployee() mutation
                     └── PATCH /api/v1/employees/{id}
                     └── Invalidate & Synchronize Query Cache
```
