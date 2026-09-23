# PRAGYA — Stage 6: Skill Gap Calculation & Gap Priority Intelligence Engine

> **Important Prototype Disclaimer**  
> *Gap priority values, mission urgency assignments, and weight parameters documented herein represent a prototype methodology designed for demonstration and architectural validation; they do not constitute official Ministry of Statistics and Programme Implementation (MoSPI) policy or Government of India workforce standards.*

---

## 1. Purpose

The **Skill Gap Engine** is the critical deterministic bridge between an employee's demonstrated competency profile (established via Stage 5 diagnostic assessments, verified training, and professional experience) and role-specific requirements (mandated via Stage 4 organizational taxonomy).

Rather than generating recommendations prematurely, Stage 6 answers the foundational question:
> **"What competencies should the employee focus on improving first, and why?"**

By framing gaps objectively through constructive, non-judgmental language, PRAGYA reinforces civil service professional development without penalizing or stigmatizing public officials.

---

## 2. Core Quantitative Gap Formula

For every competency assigned to an employee's job role:

$$\text{gap} = \max(\text{required\_score} - \text{current\_score}, 0)$$

Where:
- **$\text{current\_score}$**: The employee's calibrated proficiency score ($0 \le \text{current\_score} \le 100$) derived from empirical evidence sources.
- **$\text{required\_score}$**: The threshold score ($0 \le \text{required\_score} \le 100$) established by the cadre role requirement.

### Non-Negative Invariant
- If $\text{current\_score} \ge \text{required\_score}$, then $\text{gap} = 0$ (`NO_GAP`).
- Negative gaps are strictly prevented.
- A score exceeding the requirement indicates that the official **satisfies or exceeds** role requirements; training is not mandated solely because a course exists.

---

## 3. Multi-Factor Priority Score Formulation

A raw numerical gap does not reflect operational urgency. For example, a 20-point deficit in a primary, mission-critical sampling competency is vastly more vital than a 25-point deficit in an elective auxiliary skill.

The **Priority Score** ($0 \le \text{priority\_score} \le 100$) is computed as:

$$\text{priority\_score} = \sum (\text{Component Value} \times \text{Factor Weight})$$

$$\text{priority\_score} = (\text{gap\_score} \times 0.40) + (\text{criticality\_score} \times 0.25) + (\text{task\_relevance\_score} \times 0.15) + (\text{mission\_urgency\_score} \times 0.10) + (\text{confidence\_score} \times 0.10)$$

*Note: When $\text{gap\_score} = 0$, $\text{priority\_score} = 0.0$ and priority level is set unconditionally to `NO_GAP`.*

---

## 4. Configurable Weights (`GapPriorityConfig`)

All weight parameters are defined declaratively in `app.modules.skill_gaps.constants.GapPriorityConfig`:

| Factor | Weight | Rationale |
| :--- | :---: | :--- |
| **Gap Magnitude** | **40%** ($0.40$) | Primary baseline: the absolute numerical difference between required and demonstrated capability. |
| **Role Criticality** | **25%** ($0.25$) | The systemic importance of the competency to the Cadre/Role charter. |
| **Task Relevance** | **15%** ($0.15$) | Operational alignment with current survey operations, field duties, or statistical tasks. |
| **Mission Urgency** | **10%** ($0.10$) | MoSPI organizational priorities, census initiatives, or national statistical release deadlines. |
| **Confidence Factor** | **10%** ($0.10$) | Evidence robustness modifier: higher confidence increases decision certainty without overwhelming gap magnitude. |

---

## 5. Factor Normalization Models

### 5.1 Role Criticality
Normalized to a 0–100 scale:
- `CRITICAL`: **100.0**
- `HIGH`: **75.0**
- `MEDIUM`: **50.0**
- `LOW`: **25.0**

### 5.2 Task Relevance
Normalized to a 0–100 scale:
- `HIGH`: **100.0**
- `MEDIUM`: **60.0**
- `LOW`: **30.0**

### 5.3 Mission Urgency
Normalized to a 0–100 scale:
- `HIGH`: **100.0**
- `MEDIUM`: **60.0**
- `LOW`: **30.0**

### 5.4 Confidence Component
Empirical confidence score ($0.0 \le c \le 1.0$) normalized to 0–100:

$$\text{confidence\_score} = c \times 100$$

---

## 6. Priority Level Classification

The numeric priority score maps to actionable priority classifications using configurable thresholds:

| Priority Score Range | Priority Level | Operational Action |
| :---: | :---: | :--- |
| **$0.0$** | `NO_GAP` | Role requirement met. No remediation required. |
| **$0.01 – 24.99$** | `LOW` | Minor gap or low criticality; elective development. |
| **$25.00 – 49.99$** | `MEDIUM` | Moderate capability deficit; address during regular development cycles. |
| **$50.00 – 74.99$** | `HIGH` | Significant deficit in essential role functions; prompt capacity building required. |
| **$75.00 – 100.00$** | `CRITICAL` | Severe deficiency in critical operational task; highest immediate training priority. |

---

## 7. Confidence Flags & Responsible Assessment

Confidence represents the empirical depth and consistency of supporting evidence (assessments, certified courses, years of verified assignments).

| Confidence Range | Confidence Flag | System Behavior |
| :---: | :---: | :--- |
| **$< 0.40$** | `LOW_CONFIDENCE` | **"Potential gap — low confidence."** Displayed transparently with an advisory badge: *"More evidence is recommended before making a strong training decision."* Gap is never hidden. |
| **$0.40 – 0.69$** | `MEDIUM_CONFIDENCE` | Moderate evidentiary support; adequate for regular planning. |
| **$0.70 – 0.84$** | `HIGH_CONFIDENCE` | Robust assessment or multi-source evidence present. |
| **$0.85 – 1.00$** | `VERY_HIGH_CONFIDENCE` | Triangulated multi-modal validation (e.g. diagnostic + certified TPAC + longitudinal experience). |

---

## 8. Explainable Gap Analysis (Deterministic Templates)

In compliance with civil service transparency standards, PRAGYA does not rely on opaque LLM generative text for gap explanations. Explanations are generated deterministically:

- **Constructive Tone**: Officials are never characterized pejoratively (e.g. *"You are bad at GIS"*). The platform asserts:
  > *"GIS is below the required proficiency for Statistical Officer and is highly relevant to current survey duties."*
- **Detailed Factor Breakdown**: Every gap provides a full transparent mathematical breakdown:
  - Gap Magnitude component points
  - Role Criticality component points
  - Task Relevance component points
  - Mission Urgency component points
  - Confidence component points
  - Resulting total priority score and band

---

## 9. Recalculation Triggers & Service Orchestration

Skill gaps are persisted in the `skill_gaps` PostgreSQL table and automatically synchronized via `SkillGapService`:

1. **Assessment Attempt Completion**: When an employee finishes an assessment, `CompetencyScoringService` updates `employee_competencies` and automatically invokes `SkillGapService.recalculate_gap`.
2. **Self-Assessment Submission**: Calibrated score updates trigger instant gap re-evaluation.
3. **Role Reassignment / Cadre Promotion**: Changing an official's `job_role_id` prompts `SkillGapService.recalculate_employee_gaps`, which purges obsolete requirements and initializes new gap targets.
4. **Administrative / Batch Recalculation**: Exposed via `POST /api/v1/employees/{id}/skill-gaps/recalculate`.

---

## 10. Database Schema (`skill_gaps`)

```sql
CREATE TABLE skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    competency_id UUID NOT NULL REFERENCES competencies(id) ON DELETE CASCADE,
    current_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    required_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    gap_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    current_level_id UUID REFERENCES proficiency_levels(id) ON DELETE SET NULL,
    required_level_id UUID NOT NULL REFERENCES proficiency_levels(id) ON DELETE RESTRICT,
    confidence NUMERIC(3, 2) NOT NULL DEFAULT 0.0,
    confidence_flag VARCHAR(30) NOT NULL DEFAULT 'LOW_CONFIDENCE',
    criticality VARCHAR(20) NOT NULL,
    task_relevance VARCHAR(20) NOT NULL,
    mission_urgency VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    priority_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    priority_level VARCHAR(20) NOT NULL DEFAULT 'NO_GAP',
    role_relevance TEXT,
    explanation TEXT NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_skill_gaps_employee_competency UNIQUE (employee_id, competency_id)
);
```

---

## 11. API Endpoints

- `GET /api/v1/employees/{id}/skill-gaps`
  - Query parameters: `priority`, `domain`, `competency`, `confidence`
- `GET /api/v1/employees/{id}/skill-gaps/summary`
  - Aggregates total competencies, gaps count, distribution breakdown, average deficit, and top priority gap.
- `GET /api/v1/employees/{id}/skill-gaps/{competency_id}`
  - Returns individual gap record with comprehensive `priority_breakdown`.
- `POST /api/v1/employees/{id}/skill-gaps/recalculate`
  - Administrative trigger for explicit gap synchronization.

---

## 12. Known Limitations & Future Roadmap

1. **Static Cadre Requirements**: Role competency requirements and weights are currently maintained in organizational reference tables. Future stages will support dynamic department-level customization.
2. **Scope Boundary**: Stage 6 strictly concludes with the identification and prioritization of skill gaps ("What needs improvement first?"). Specific course matchmaking, iGOT Karmayogi course ranking, and learning pathway orchestration are reserved for Stage 7.
