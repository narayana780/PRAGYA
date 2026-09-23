# PRAGYA — Stage 11: Adaptive Assessment & Closed-Loop Competency Recalibration

## 1. Architecture Overview

PRAGYA Stage 11 closes the continuous learning and capability loop for India's Official Statistical System:
$$\text{Learning} \longrightarrow \text{Assessment} \longrightarrow \text{Evidence Logging} \longrightarrow \text{Competency Recalibration} \longrightarrow \text{Skill Gap Synchronization} \longrightarrow \text{Recommendation Update}$$

Rather than overwriting an employee's demonstrated competency score based on a single evaluation attempt, Stage 11 treats every completed assessment as **auditable evidence**. Multiple empirical evidence records (including prior diagnostic assessments, verified training, and practical experience) are deterministically synthesized into an updated demonstrated competency score, which immediately triggers the recalculation of downstream skill gaps and learning recommendations.

```
+-----------------------------------------------------------------------------------+
|                           PRAGYA Closed-Loop Flow                                 |
+-----------------------------------------------------------------------------------+
|  [Learning / Courses / Documents]                                                 |
|          |                                                                        |
|          v                                                                        |
|  [Stage 10: RAG-Grounded Quiz / Assessment]                                       |
|          |                                                                        |
|          v                                                                        |
|  [Stage 11: Adaptive Assessment Session] (Deterministic 1-step ladder)            |
|          |                                                                        |
|          v                                                                        |
|  [Stage 5: Competency Evidence Table] (ADAPTIVE_ASSESSMENT evidence logged)       |
|          |                                                                        |
|          v                                                                        |
|  [CompetencyRecalibrationService] (Weighted evidence aggregation, bounded, delta) |
|          |                                                                        |
|          +---> [Competency Recalibrations Audit Table]                            |
|          |                                                                        |
|          v                                                                        |
|  [Stage 6: Skill Gap Engine] (recalculate_gap triggered)                          |
|          |                                                                        |
|          v                                                                        |
|  [Stage 7: Recommendation Engine] (Rankings automatically reflect updated gap)   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Adaptive Question Selection & Serving

When an employee initiates an adaptive assessment session:
1. **Target Competency & Starting Level**: The system inspects the employee's current demonstrated score for the target competency.
   - Initial starting difficulty is determined deterministically:
     - `Score < 30.0` $\implies$ `BEGINNER`
     - `30.0 <= Score < 60.0` $\implies$ `INTERMEDIATE`
     - `Score >= 60.0` $\implies$ `ADVANCED`
   *(PRAGYA prototype methodology)*
2. **Grounded Question Serving**:
   - The engine searches for existing validated questions for the target competency matching the requested difficulty level.
   - If questions already exist from previous grounded generation, they are served immediately without redundant LLM calls.
   - If no validated question exists at the requested difficulty, the engine invokes the grounded RAG quiz pipeline with retrieved document chunks to generate validated MCQs on demand.
3. **No Redundant Embeddings**: The system reuses the singleton embedding model (`sentence-transformers/all-MiniLM-L6-v2`) initialized at application startup.

---

## 3. Deterministic Difficulty Adaptation Rules

PRAGYA strictly enforces a **deterministic single-step ladder**. The difficulty never jumps across multiple steps:

| Current Question Difficulty | Answer Result | Next Question Difficulty | Boundary Rule Applied |
|:---|:---:|:---|:---|
| `BEGINNER` | Correct | `INTERMEDIATE` | Single-step promotion |
| `BEGINNER` | Incorrect | `BEGINNER` | Bounded at minimum `BEGINNER` |
| `INTERMEDIATE` | Correct | `ADVANCED` | Single-step promotion |
| `INTERMEDIATE` | Incorrect | `BEGINNER` | Single-step demotion |
| `ADVANCED` | Correct | `ADVANCED` | Bounded at maximum `ADVANCED` |
| `ADVANCED` | Incorrect | `INTERMEDIATE` | Single-step demotion |

> **Learner Transparency Rule**: The adaptation mechanics operate entirely on the backend. The UI does not present distracting system-level messages such as *"Difficulty increased because you got the previous answer correct."*

---

## 4. Session Stop Conditions

An adaptive session terminates deterministically when any of the following conditions are met:
1. **Maximum Question Count**:
   `question_count >= MAX_ADAPTIVE_QUESTIONS (15)`
2. **Confidence Convergence**:
   `question_count >= MIN_ADAPTIVE_QUESTIONS (5)` **AND** `calculated_confidence >= TARGET_CONFIDENCE (0.85)`
3. **Question Exhaustion**:
   The engine cannot retrieve or generate further validated, grounded questions for the target competency.

*(Parameters `MIN_ADAPTIVE_QUESTIONS = 5`, `MAX_ADAPTIVE_QUESTIONS = 15`, and `TARGET_CONFIDENCE = 0.85` represent PRAGYA prototype methodology).*

---

## 5. Confidence Calculation Formula

To prevent arbitrary or non-deterministic estimations, confidence is computed using a closed-form formula rather than an LLM:

$$\text{Depth Factor} = \min\left(\frac{N}{\text{MAX\_QUESTIONS}}, 1.0\right)$$

$$\text{Coverage Factor} = \frac{|\text{Unique Difficulties Tested}|}{3.0}$$

$$\text{Consistency Factor} = 1.0 - \min\left(\frac{|\text{Correct} - \text{Incorrect}|}{N}, 0.5\right)$$

$$\text{Raw Confidence} = 0.40 \cdot \text{Depth} + 0.35 \cdot \text{Coverage} + 0.25 \cdot \text{Consistency}$$

$$\text{Confidence} = \text{clamp}(\text{Raw Confidence}, 0.20, 1.00)$$

*(PRAGYA prototype methodology. Clearly documented as an empirical prototype formula and not official MoSPI policy).*

---

## 6. Weighted Evidence Aggregation

When an adaptive assessment completes, the assessment performance is converted into an empirical score:

$$\text{Assessment Score} = \frac{\sum_{i=1}^N \text{Score}(Q_i)}{\sum_{i=1}^N \text{MaxScore}(Q_i)} \times 100$$

Where question points are weighted by difficulty: `BEGINNER = 1.0`, `INTERMEDIATE = 2.0`, `ADVANCED = 3.0`.

This score is logged as a new evidence record in `competency_evidence` under `evidence_type = "ADAPTIVE_ASSESSMENT"`.

### Evidence Source Weights
Existing validated evidence is retained and aggregated alongside the new adaptive assessment evidence:

| Evidence Type | Baseline Weight | Notes |
|:---|:---:|:---|
| `DIAGNOSTIC` | 0.40 | Initial baseline competency evaluation |
| `ADAPTIVE_ASSESSMENT` | 0.25 | Recent multi-difficulty adaptive session evidence |
| `RECENT_ASSESSMENT` | 0.15 | Other structured assessments or periodic evaluations |
| `TRAINING` | 0.10 | Verified training completions (e.g. iGOT / NSSTA) |
| `EXPERIENCE` | 0.05 | Cadre role experience and field service records |
| `SELF_ASSESSMENT` | 0.05 | Employee self-evaluations |

*(PRAGYA prototype methodology. Weights are renormalized across currently available evidence sources for the employee).*

---

## 7. Recalibration Formula

The new raw demonstrated competency score is computed as:

$$\text{New Raw Score} = \sum_{e \in \text{Evidence}} w_e \times \text{Score}_e$$

Where $\sum w_e = 1.0$ (renormalized across present evidence).

---

## 8. Anti-Oscillation & Max Delta Protection

To prevent noisy individual assessment sessions from destabilizing capability records:

$$\Delta_{\text{raw}} = \text{New Raw Score} - \text{Previous Score}$$

$$\Delta_{\text{clamped}} = \text{clamp}(\Delta_{\text{raw}}, -\text{MAX\_RECALIBRATION\_DELTA}, +\text{MAX\_RECALIBRATION\_DELTA})$$

$$\text{Recalibrated Score} = \text{clamp}(\text{Previous Score} + \Delta_{\text{clamped}}, 0.0, 100.0)$$

Where:
- $\text{MAX\_RECALIBRATION\_DELTA} = 20.0$ points.
- Bounded strictly to $[0.0, 100.0]$.

*(PRAGYA prototype methodology).*

---

## 9. Downstream Skill Gap Integration (Stage 6)

Immediately following database commit of the recalibrated competency score:
1. `CompetencyRecalibrationService` triggers `SkillGapService.recalculate_gap(employee_id, competency_id)`.
2. Stage 6 determines the required score from the employee's cadre role requirements:
   $$\text{Gap Score} = \max(0, \text{Required Score} - \text{Recalibrated Score})$$
3. Priority level and score are recalculated based on criticality, mission urgency, and the updated gap magnitude.

---

## 10. Downstream Learning Recommendation Integration (Stage 7)

Stage 7 recommendation queries rank learning items by:
1. Active skill gap priority score (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`)
2. Cadre role alignment
3. Provider accreditation (iGOT Karmayogi, NSSTA, MoSPI In-House)

Because Stage 11 updates the canonical skill gaps in real time, subsequent calls to `/api/v1/recommendations` automatically reflect the updated priorities without requiring any secondary recommendation algorithm.

---

## 11. Security & Employee Isolation

- Every endpoint verifies the authenticated `current_employee_id`.
- Accessing sessions, responses, or recalibrations belonging to another employee results in an immediate `HTTP 403 Forbidden`.
- The frontend `employee_id` parameter is never trusted; session authorization is strictly verified against the database record owner.

---

## 12. Idempotency & Transaction Safety

1. **Transactional Recalibration**: Recalibration, evidence creation, score history update, and skill gap recalculation execute inside a single atomic database transaction. If any step fails, the entire transaction rolls back cleanly.
2. **Duplicate Response Protection**: Submitting an answer for the same `(session_id, question_id)` pair returns the existing response record without creating duplicate evidence or altering session question counts.
3. **Duplicate Completion Protection**: Invoking `/complete` on an already completed session safely returns the persisted `CompetencyRecalibration` record without recalibrating a second time.

---

## 13. Failure Handling & Graceful Degradation

- **LLM / Generation Failure**: If on-demand question generation encounters transient timeouts or errors, the session returns existing validated questions or safely pauses the session, allowing the user to complete with existing evidence once $\ge 5$ questions have been answered.
- **Abandoned Sessions**: Sessions inactive for extended periods can be marked `ABANDONED` without corrupting employee competency scores.
- **RAG Grounding Preservation**: All questions served in adaptive sessions retain metadata indicating their source document and page number.

---

## 14. Known Limitations

- Multi-competency bundle assessment: Currently, each adaptive session focuses on a single target competency.
- Offline mode: Adaptive selection requires connectivity to the PRAGYA backend to evaluate correctness and recalculate difficulty.
- Cold start: New employees with zero prior evidence rely on baseline starting thresholds until diagnostic or training evidence is recorded.

---

## 15. Future Improvements

- Item Response Theory (IRT): Migrate from 3-tier difficulty ladders (`BEGINNER`, `INTERMEDIATE`, `ADVANCED`) to continuous item parameter calibration (2PL / 3PL IRT models).
- Spaced Reassessment Scheduling: Automated background cron notifying employees when demonstrated competency confidence decays over time due to evidence aging.
- Multi-domain comprehensive assessments spanning entire functional cadre streams in a single adaptive session.

---
*Note: All weighting factors, difficulty score mappings, and delta caps described herein represent PRAGYA prototype methodology designed for testing and demonstration, and do not constitute official MoSPI administrative policy.*
