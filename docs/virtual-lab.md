# PRAGYA — Stage 12: Statistical Virtual Lab Architecture & Specification

## 1. Executive Summary & Objective

The **PRAGYA Statistical Virtual Lab** is an interactive, sandbox simulation environment built to allow government statistical officers and analysts to practice realistic official-statistics workflows before performing them on live administrative systems ("*Practice before performing*").

The simulation enables learners to:
1. **Observe** realistic survey/administrative data scenarios.
2. **Inspect** tabular datasets with pagination and column-level inspection.
3. **Choose** controlled analytical actions (audits, sampling parameters, aggregations, imputation strategies).
4. **Execute** deterministic simulations safely on the backend.
5. **Inspect** authoritative intermediate and final results.
6. **Identify** statistical errors and data anomalies.
7. **Receive** targeted educational feedback and contextual hints.
8. **Earn** an evidence-based lab score and generate closed-loop competency evidence without modifying any real government data.

---

## 2. Architectural Blueprint

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             NEXT.JS FRONTEND                                │
│                                                                             │
│  /employee/labs         /employee/labs/[id]       /employee/labs/[id]/run   │
│  (Catalog Hub)       →  (Scenario Overview)   →   (3-Column Player)         │
│                                                          │                  │
│                                                          ▼                  │
│                                                /employee/labs/[id]/result   │
│                                                (Score & Next Actions)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST API (JSON)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI SIMULATION ENGINE                          │
│                                                                             │
│   POST /api/v1/labs/{id}/sessions  →  Create isolated employee session      │
│   POST /api/v1/lab-sessions/{id}/actions → Deterministic evaluation engine   │
│   POST /api/v1/lab-sessions/{id}/hint    → Deterministic/AI hints            │
│   POST /api/v1/lab-sessions/{id}/complete → Score & Evidence compilation    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌──────────────────────────────────────┐┌──────────────────────────────────────┐
│        VIRTUAL LAB TABLES            ││      PRAGYA CORE ARCHITECTURE        │
│                                      ││                                      │
│  • lab_datasets (synthetic data)     ││  • competencies                      │
│  • lab_scenarios (audit/sample/etc.) ││  • employee_competencies             │
│  • lab_sessions (isolation/state)    ││  • competency_evidence (VIRTUAL_LAB) │
│  • lab_actions (deterministic score) ││  • skill_gaps (gap drawer CTA)       │
│  • lab_results (summary & metrics)   ││  • quizzes (Stage 10 post-lab quiz)  │
│                                      ││  • adaptive assessments (Stage 11)   │
└──────────────────────────────────────┘└──────────────────────────────────────┘
```

---

## 3. Sandboxed Scenarios & Curated Datasets

All datasets in Stage 12 are synthetic and explicitly tagged with `is_synthetic = true`.

| Scenario ID | Title | Scenario Type | Mapped Competency Code | Difficulty | Est. Time | Sample Dataset |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sc-dq-audit-01` | Periodic Labour Survey Quality Audit | `DATA_QUALITY_AUDIT` | `COMP-DATA-QUAL` (Data Quality Frameworks) | Intermediate | 20 min | 35 synthetic household survey records with duplicates, invalid codes, and out-of-range expenditures |
| `sc-survey-sample-02` | Annual Household Consumption Sampling | `SURVEY_SAMPLING` | `COMP-SAMPLING` (Sampling & Estimation) | Intermediate | 25 min | 100 synthetic administrative sampling frame units across North/South regions and Rural/Urban sectors |
| `sc-desc-stats-03` | District Economic Expenditure Profile | `DESCRIPTIVE_STATISTICS` | `COMP-STAT-METH` (Applied Statistical Methods) | Beginner | 15 min | 25 synthetic district expenditure records with high-value outlier skewness |
| `sc-missing-data-04` | Enterprise Survey Missing Data Remediation | `MISSING_DATA_ANALYSIS` | `COMP-DATA-QUAL` (Data Quality Frameworks) | Intermediate | 20 min | 30 synthetic establishment records containing MCAR and MAR missing data patterns |

---

## 4. Simulation Engine (`LabEngine`)

The `LabEngine` provides strict deterministic execution on the backend:

1. **Data Quality Audit Engine**:
   - Compares learner-identified anomalies against ground-truth problem codes (`DUPLICATE_KEY`, `OUT_OF_RANGE_AGE`, `INVALID_GENDER_CODE`, `INVALID_SECTOR_CODE`).
   - Validates selection of National Quality Assurance Framework (NQAF) validation rules.
   - Applies backend deduplication and normalization routines to simulate data cleansing.
2. **Survey Sampling Engine**:
   - Validates sampling method selection (`STRATIFIED` preferred over `SIMPLE_RANDOM` or `SYSTEMATIC`).
   - Validates sample size sufficiency against population size ($n \ge 25$ recommended).
   - Generates simulated samples using a fixed random seed (`random.Random(42)`) to ensure exact reproducibility.
3. **Descriptive Statistics Engine**:
   - Backend calculates authoritative statistical values:
     $$\text{Mean} = \frac{\sum x_i}{N}$$
     $$\text{Median} = \text{middle value}$$
     $$\text{Standard Deviation} = \sqrt{\frac{\sum (x_i - \bar{x})^2}{N - 1}}$$
   - Evaluates learner diagnosis of right-skewness and recommendation of robust central tendency measures (Median).
4. **Missing Data Analysis Engine**:
   - Evaluates missing value rate detection ($20\%$ missing in turnover, $10\%$ missing in investment).
   - Classifies missingness mechanisms (MCAR vs MAR).
   - Simulates outcome of chosen handling strategy (Median Imputation with missingness indicator vs Listwise Deletion).

---

## 5. Scoring & Confidence Methodology

> [!NOTE]
> All scoring rules, weights, and confidence formulas documented below are designated as **PRAGYA prototype methodology**.

### Scoring Policy
- Each scenario defines a maximum achievable score (100 points) partitioned across steps (e.g., 25 points $\times$ 4 steps).
- Actions are graded based on:
  - **Correct Choice**: $100\%$ of step weight.
  - **Partially Correct / Sub-optimal Choice**: $40\% - 60\%$ of step weight (e.g., selecting SRS instead of Stratified sampling).
  - **Incorrect / Invalid Choice**: $0$ points.
- Learner percentage:
  $$\text{Percentage} = \left(\frac{\sum \text{Score Awarded}}{\sum \text{Max Possible Score}}\right) \times 100$$
- Pass threshold: $\ge 70.0\%$.

### Confidence Policy
Confidence is calculated deterministically based on action accuracy, completion coverage, and scenario difficulty:
$$\text{Confidence} = 0.50 + 0.40 \times \left(\frac{\text{Correct Actions}}{\text{Total Steps}}\right) + 0.05 \times \text{Difficulty Bonus}$$
The resulting value is capped in the range $[0.50, 0.95]$.

---

## 6. Security Sandbox & Anti-Vulnerability Policy

The Virtual Lab operates as a strictly controlled simulation sandbox:
1. **Zero Arbitrary Execution**: No user-submitted Python code, SQL queries, or shell scripts are ever accepted or evaluated.
2. **Controlled Parameter Payloads**: Actions are restricted to predefined schemas (`sampling_method`, `sample_size`, `strata_fields`, `metrics`, `handling_strategy`).
3. **Database Protection**: Real government data, production Postgres tables, and schema definitions are completely isolated from simulation logic.
4. **Employee Isolation**: All sessions and actions enforce strict employee isolation. A learner can only access and submit actions for their own sessions.

---

## 7. Closed-Loop Integrations

### 7.1 Competency Evidence Integration
Upon successful completion of a lab session ($\text{Percentage} \ge 70.0\%$), `LabService` records a new entry in `competency_evidence`:
- `evidence_type`: `VIRTUAL_LAB` (weighted at $0.20$ in `DEFAULT_EVIDENCE_WEIGHTS`)
- `score`: Learner's percentage score ($0 - 100$)
- `confidence_score`: Deterministic confidence score ($0.50 - 0.95$)
- `valid_until`: Current date $+ 180$ days
- Automatically triggers `recalibrate_competency()` to update the employee's current proficiency level.

### 7.2 Skill-Gap Integration
The employee skill gaps view (`/employee/gaps` and `GapDetailDrawer`) includes a contextual **"Practice in Lab"** call to action that automatically filters and launches the relevant lab scenario targeting that specific gap.

### 7.3 Stage 10 Quiz & Stage 11 Adaptive Assessment Integration
The Virtual Lab result screen (`/employee/labs/[id]/result`) provides direct navigation paths:
- **"Test this Skill"**: Navigates to `/employee/quizzes` to test theoretical understanding.
- **"Reassess Competency"**: Navigates to `/employee/adaptive` to trigger adaptive CAT evaluation for the calibrated competency.

---

## 8. Known Limitations & Future Expansion

1. **Pre-defined Scenario Set**: MVP includes 4 canonical scenarios. Future iterations will introduce automated synthetic scenario generation for National Accounts, Consumer Price Index (CPI), and Industrial Statistics (IIP).
2. **Tabular Size**: Current synthetic datasets are sized between 25 and 100 rows for real-time in-memory simulation. Future expansion can leverage WebAssembly / DuckDB-Wasm for larger client-side synthetic simulations.
