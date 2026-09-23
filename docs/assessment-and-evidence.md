# PRAGYA — Stage 5: Competency Assessment & Evidence Engine

> **Methodology Notice & Disclaimer:**
> **The competency scoring methodology implemented here is a prototype methodology and is not an official MoSPI competency scoring standard.**

---

## 1. Purpose

The Stage 5 **Competency Assessment & Evidence Engine** constitutes a core intelligence subsystem in PRAGYA. Its purpose is to answer:

> *"What is this employee's current demonstrated competency based on verified, empirical evidence?"*

In alignment with PRAGYA's foundational product principles:
1. **No Hallucinated Competency:** An LLM or AI agent cannot magically infer an employee's real-world skills without empirical ground-truth data.
2. **Multi-Source Evidence Model:** Competency is evaluated across distinct, verifiable evidence channels rather than relying on a single examination.
3. **Stage Boundary Discipline:** Stage 5 strictly estimates **current demonstrated competency**. It does *not* compute skill gaps, gap priorities, or training recommendations; those belong to Stage 6 and Stage 7 respectively.

---

## 2. Assessment Architecture

The assessment subsystem provides server-authoritative, deterministic psychometric evaluation.

```
                  ┌─────────────────────────────────────┐
                  │             Assessment              │
                  │ (title, type: DIAGNOSTIC, duration) │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌───────────────────────┐                           ┌─────────────────────┐
│ AssessmentCompetency  │                           │ AssessmentQuestion  │
│  (competency mapping) │                           │  (4 options, diff,  │
└───────────────────────┘                           │   server-only ans)  │
                                                    └──────────┬──────────┘
                                                               │
                                                               ▼
┌───────────────────────┐                           ┌─────────────────────┐
│   AssessmentAttempt   │ 1                       * │ AssessmentResponse  │
│  (status, raw, %)     ├──────────────────────────►│ (attempt_id, q_id,  │
└──────────┬────────────┘                           │   is_correct, pts)  │
           │                                        └──────────┬──────────┘
           │ on complete_attempt()                             │
           ▼                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CompetencyEvidence                            │
│  (employee_id, comp_id, type, raw_value, normalized_score, weight, ...) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           EmployeeCompetency                            │
│    (employee_id, comp_id, current_score, confidence, evidence_count)    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CompetencyScoreHistory                          │
│     (prev_score, new_score, prev_conf, new_conf, trigger_reason)        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Entities
1. `assessments`: Defines evaluation sessions (`DIAGNOSTIC`, `QUIZ`, `ADAPTIVE`, `PRACTICE`).
2. `assessment_competencies`: Maps an assessment to the competencies it tests.
3. `assessment_questions`: High-quality, psychometrically deterministic MCQs tagged to a single competency and difficulty (`EASY`, `MEDIUM`, `HARD`).
4. `assessment_attempts`: Tracks learner lifecycle (`IN_PROGRESS`, `COMPLETED`, `ABANDONED`).
5. `assessment_responses`: Records individual question answers incrementally with unique constraint on `(attempt_id, question_id)`.
6. `competency_evidence`: Audit record of empirical evidence points contributing to competency scores.
7. `employee_competencies`: The current demonstrated competency state of an employee.
8. `competency_score_history`: Audit ledger tracking score/confidence modifications with trigger reasons.

---

## 3. Evidence Types

Stage 5 recognizes five empirical evidence sources:

| Evidence Type | Code Key | Base Weight | Description |
| :--- | :--- | :--- | :--- |
| **Diagnostic Assessment** | `DIAGNOSTIC` | **50%** | Comprehensive multi-competency baseline psychometric test |
| **Recent Assessment** | `RECENT_ASSESSMENT` | **20%** | Topical quizzes or milestone evaluations |
| **Verified Training** | `TRAINING` | **15%** | Official ISTM/NSSTA/MoSPI completed training courses |
| **Relevant Experience** | `EXPERIENCE` | **10%** | Cadre service tenure mapped via non-linear tenure curve |
| **Self Assessment** | `SELF_ASSESSMENT` | **5%** | Employee self-appraisal mapped from 5 proficiency levels |

*Note: Supervisor ratings are deliberately deferred to future stages to prevent unverified subjective bias.*

---

## 4. Weighting Configuration

Default weights are defined in `AssessmentWeightConfig`:
- Diagnostic: $0.50$ ($50\%$)
- Recent Assessment: $0.20$ ($20\%$)
- Verified Training: $0.15$ ($15\%$)
- Relevant Experience: $0.10$ ($10\%$)
- Self Assessment: $0.05$ ($5\%$)
- **Total:** $1.00$ ($100\%$)

---

## 5. Available-Evidence Renormalization

When an employee lacks one or more evidence sources (e.g. no diagnostic taken yet, or no course completed for a new competency), **missing sources are never treated as zero**.

Treating missing sources as zero would artificially depress an employee's demonstrated score. Instead, PRAGYA performs available-evidence renormalization:

$$\text{Normalized Weight}_i = \frac{W_i}{\sum_{k \in \text{Available}} W_k}$$

### Example:
- Available: Diagnostic ($0.50$), Training ($0.15$), Experience ($0.10$)
- Total available weight: $0.50 + 0.15 + 0.10 = 0.75$
- Renormalized weights:
  - Diagnostic: $0.50 / 0.75 = 66.67\%$
  - Training: $0.15 / 0.75 = 20.00\%$
  - Experience: $0.10 / 0.75 = 13.33\%$
- Sum of normalized weights: $100.0\%$

---

## 6. Experience Normalization

Cadre experience is contextual evidence. To avoid equating mere tenure with mastery, experience is weighted at only 10% and normalized using an asymptotic tenure curve:

| Experience (Years) | Normalized Score (0–100) | Interpretation |
| :--- | :--- | :--- |
| 0 years | 0 | Entry into service |
| 1 year | 20 | Probationary familiarity |
| 2 years | 35 | Operational onboarding |
| 3 years | 45 | Developing competency |
| 4 years | 55 | Competent practitioner |
| 5 years | 65 | Solid operational experience |
| 6 years | 70 | Seasoned cadre officer |
| 7–10 years | 75 | Extensive institutional tenure |
| 11–15 years | 85 | Senior cadre institutional knowledge |
| 16+ years | 90 | Decades of senior service (capped at 90) |

*Function: `normalize_experience(years: float) -> float`*

---

## 7. Self-Assessment Conversion

Employees can submit self-evaluations across 5 standard proficiency levels. To eliminate client tampering, the API accepts only the integer level `1–5`:

| Selected Level | Proficiency Label | Server Mapped Score |
| :--- | :--- | :--- |
| **Level 1** | Beginner | **20 / 100** |
| **Level 2** | Basic | **40 / 100** |
| **Level 3** | Working | **60 / 100** |
| **Level 4** | Proficient | **80 / 100** |
| **Level 5** | Advanced | **100 / 100** |

Self-assessment contributes a modest 5% default weight to prevent score inflation.

---

## 8. Training Evidence

Training evidence reuses verified records from `training_history` (Stage 3).
- If a course score exists: uses that score directly ($0–100$).
- If course completed without an explicit exam score: uses the conservative prototype default score of **60 / 100**. Course completion does not imply mastery.
- Training records are associated with competencies via the `training_history.competency_id` relationship. Unmapped training records are not synthesized into arbitrary evidence.

---

## 9. Confidence Calculation

Confidence ($0.00$ to $1.00$) measures empirical certainty in the score estimation, independent of the score itself:

$$\text{Confidence} = \text{Base Confidence} + \text{Consistency Modifier} + \text{Recency Modifier}$$

- **Base Confidence:** Ratio of available evidence channels:
  $$\text{Base} = \frac{\text{Available Evidence Count}}{5}$$
- **Consistency Modifier:** $+0.05$ if standard deviation among evidence scores is $< 15$ pts (high consistency), or $-0.05$ if standard deviation $> 30$ pts.
- **Recency Modifier:** $+0.05$ if most recent evidence is within 90 days.
- **Bounds:** Clamped strictly to $[0.05, 1.00]$.

### Confidence Bands

| Confidence Range | Rating Label | Visual Indicator |
| :--- | :--- | :--- |
| $0.00 - 0.39$ | `LOW` | Rose badge |
| $0.40 - 0.69$ | `MEDIUM` | Amber badge |
| $0.70 - 0.84$ | `HIGH` | Cyan badge |
| $0.85 - 1.00$ | `VERY_HIGH` | Emerald badge |

---

## 10. Competency Calculation

When evidence is updated (e.g. diagnostic completion or self-assessment submission):

$$\text{Current Score} = \sum_{i \in \text{Available}} (\text{Normalized Score}_i \times \text{Renormalized Weight}_i)$$

The resulting score ($0.0–100.0$) is mapped to a standard MoSPI Proficiency Level:
- $0.0 - 29.9$: Level 1 — Beginner
- $30.0 - 49.9$: Level 2 — Basic
- $50.0 - 69.9$: Level 3 — Working
- $70.0 - 89.9$: Level 4 — Proficient
- $90.0 - 100.0$: Level 5 — Advanced

---

## 11. Score History & Auditability

Every recalculation of `EmployeeCompetency` writes an immutable record to `competency_score_history`:
- `previous_score` and `new_score`
- `previous_confidence` and `new_confidence`
- `trigger_evidence_id`
- `change_reason` (e.g. "Completed PRAGYA Core Competency Diagnostic", "Submitted Self-Assessment", etc.)
- `created_at` timestamp

This provides a continuous audit trail for the future closed-loop system.

---

## 12. Security Rules

1. **Server-Authoritative Psychometrics:** Correct answers and explanations are never returned in initial assessment payloads (`/assessments/{id}`).
2. **No Client Scoring:** Scores, percentages, points, and competency updates are computed solely on the backend during `complete_attempt()`.
3. **Attempt Immutability:** An attempt marked `COMPLETED` cannot accept new responses or be completed a second time.
4. **Tenant/Cadre Isolation:** Attempts and responses enforce strict `employee_id` validation. Officers cannot respond on behalf of other employees.

---

## 13. Prototype Assumptions

1. Default weights ($50/20/15/10/5$) are heuristic starting points for the PRAGYA prototype.
2. The 24 diagnostic questions represent a psychometric baseline across 8 core statistical/technical competencies.
3. Training completion without an examination score defaults to 60/100.

---

## 14. Known Limitations

1. **No Adaptive Question Sequencing Yet:** Diagnostic questions are served deterministically in fixed order; Computerized Adaptive Testing (CAT) with Item Response Theory (IRT) is slated for Stage 13.
2. **Single Primary Diagnostic:** Currently 1 core diagnostic exists; role-specific diagnostic variants will be added in subsequent milestones.
3. **Skill Gap Engine Deferred:** In accordance with the Stage 5 specification, gap analysis ($Required - Current$) is deferred to Stage 6.
