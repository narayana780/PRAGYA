# PRAGYA — Stage 7: Personalized Learning Recommendation Engine & Provider Architecture

## 1. Executive Summary

Stage 7 implements the **Personalized Learning Recommendation Engine**, the **Multi-Provider Content Architecture**, and the **Structured Explainability System** for the PRAGYA platform.

This engine bridges the gap between identified competency deficits (from Stage 5 assessment evidence and Stage 6 prioritized skill gaps) and actionable cadre development. Rather than presenting generic course catalogues or opaque black-box suggestions, PRAGYA generates mathematically deterministic, explainable recommendations from multiple learning providers—specifically **iGOT Karmayogi**, the **National Statistical Systems Training Academy (NSSTA / TPAC)**, and **PRAGYA In-Platform Labs**.

---

## 2. Architecture & Design Principles

```
+-----------------------------------------------------------------------------------+
|                            PRAGYA RECOMMENDATION ENGINE                            |
+-----------------------------------------------------------------------------------+
                                         |
     +-----------------------------------+-----------------------------------+
     |                                   |                                   |
     v                                   v                                   v
+-----------------------+   +-------------------------+   +-------------------------+
| Stage 5 Evidence &    |   | Stage 6 Prioritized     |   | Employee Profile &      |
| Demonstrated Scores   |   | Skill Gaps (P1..P4)     |   | Historical Training     |
+-----------------------+   +-------------------------+   +-------------------------+
     |                                   |                                   |
     +-----------------------------------+-----------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |   Candidate Generation & Filtering  |
                      |   - Status: PUBLISHED               |
                      |   - Ineligible / Dismissed Filter   |
                      |   - Completed Content Demoted       |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    7-Factor Scoring & Ranking       |
                      |    Sum(Weight_i * Factor_i) = 100   |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |   Structured Explainability Engine  |
                      |   (Human-readable Reasons & Audits) |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    Progressive Learning Pathway     |
                      |    (Foundation -> Lab -> Applied    |
                      |     -> Institutional Immersion)     |
                      +-------------------------------------+
```

### Key Principles

1. **Deterministic & Audit-Ready**: Recommendation scores are computed using an explicit mathematical model ($0 \le \text{Score} \le 100$). No random weights, no hallucinated scores.
2. **Transparent Explainability**: Every recommended item provides a structured breakdown detailing exactly *why* it was selected, which gap it addresses, how well its proficiency level matches, and how prerequisite knowledge was evaluated.
3. **Provider Agnostic**: Providers implement a standard `LearningProvider` abstraction. PRAGYA can query internal catalogues, external government portals (iGOT Karmayogi), or specialized academies (NSSTA/TPAC) through a unified interface.
4. **Honest Mock Boundaries**: Synthetic records are marked with `source_mode = "MOCK"` and displayed with badges in the UI. No live government APIs are falsely claimed.

---

## 3. Provider Abstraction Architecture

### 3.1 Interface Definition

The provider interface (`apps/api/app/modules/recommendations/providers/base.py`) defines a contract that all content sources must satisfy:

```python
class LearningProvider(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    async def get_items(self, filters: Dict[str, Any] | None = None) -> List[ProviderLearningItem]: ...

    @abstractmethod
    async def get_item_by_id(self, external_id: str) -> ProviderLearningItem | None: ...

    @abstractmethod
    async def search_items(self, query: str, limit: int = 10) -> List[ProviderLearningItem]: ...
```

### 3.2 Implemented Providers

| Provider Code | Display Name | Content Focus | Default Source Mode |
|---|---|---|---|
| `IGOT` | iGOT Karmayogi | Civil services core competencies, digital governance, procurement, ethics | `MOCK` |
| `NSSTA` | NSSTA / TPAC | Official statistics, national accounts, survey methodology, price indices | `MOCK` |
| `PRAGYA` | PRAGYA Platform | Interactive scenario simulations, practical data audits, diagnostic labs | `INTERNAL` |

### 3.3 Provider Registry

The `ProviderRegistry` manages provider lifecycles and handles multi-provider catalogue aggregation:

```python
registry = ProviderRegistry()
registry.register(MockIGOTProvider())
registry.register(MockNSSTAProvider())
registry.register(PragyaLearningProvider())
```

### 3.4 Production Integration Roadmap

To connect to live government endpoints in future phases:
1. **iGOT Karmayogi**: Implement an `IGOTKarmayogiProvider` utilizing OAuth2 client credentials to query the Karmayogi Open API / Sunbird RC registry. Set `source_mode = "LIVE"`.
2. **NSSTA-TPAC**: Implement an `NSSTALearningProvider` integrating with the MoSPI training management portal using REST/SOAP endpoints. Set `source_mode = "LIVE"`.
3. The recommendation engine remains 100% untouched because it operates strictly against the normalized `LearningItem` model.

---

## 4. Multi-Factor Scoring Model

Every eligible learning candidate is scored across 7 deterministic dimensions. The overall score is bounded in $[0, 100]$.

$$\text{Final Score} = \sum_{i=1}^{7} (W_i \times F_i)$$

### 4.1 Factors and Weights

| Factor ($F_i$) | Weight ($W_i$) | Description |
|---|---|---|
| **Gap Priority** | $35\%$ ($0.35$) | Rewards alignment with high-priority skill gaps identified in Stage 6. |
| **Competency / Semantic Match** | $25\%$ ($0.25$) | Evaluates explicit primary competency mapping or keyword semantic overlap. |
| **Proficiency Level Fit** | $15\%$ ($0.15$) | Assesses alignment between item difficulty/level and target proficiency level. |
| **Outcome Coverage** | $10\%$ ($0.10$) | Measures how many learning outcomes address required indicators. |
| **Prerequisite Fit** | $5\%$ ($0.05$) | Validates whether the officer possesses baseline prerequisite competencies. |
| **Duration Fit** | $5\%$ ($0.05$) | Rewards manageable, high-impact modules over excessively short or long courses. |
| **Novelty** | $5\%$ ($0.05$) | Ensures fresh content; penalizes already completed or repetitive courses. |

### 4.2 Factor Calculation Formulas

#### 1. Gap Priority Score ($F_{\text{gap}} \in [0, 100]$)
Derived directly from the Stage 6 `priority_score` ($0$ to $100$):
- Critical Gap ($P1$): Score $\ge 75$
- High Gap ($P2$): Score $50 - 74$
- Medium Gap ($P3$): Score $25 - 49$
- Low Gap ($P4$): Score $< 25$
- No open gap for competency: Default score $20.0$

#### 2. Competency / Semantic Match ($F_{\text{match}} \in [0, 100]$)
- Explicit primary competency match: $100.0$
- Related competency tag match: $75.0$
- Keyword semantic overlap: Jaccard similarity between item keywords/syllabus and competency description $\times 100$.
- Baseline fallback: $20.0$

#### 3. Proficiency Level Fit ($F_{\text{level}} \in [0, 100]$)
Let $\Delta_{\text{level}} = \text{Item Level} - \text{Target Level}$:
- Exact match ($\Delta = 0$): $100.0$
- Slightly lower ($\Delta = -1$, preparatory): $75.0$
- Slightly higher ($\Delta = +1$, stretch): $65.0$
- Substantial mismatch ($|\Delta| \ge 2$): $\max(10.0, 100.0 - |\Delta| \times 35.0)$

#### 4. Outcome Coverage ($F_{\text{outcome}} \in [0, 100]$)
$$\min(100.0, 40.0 + \text{Count}(\text{learning\_outcomes}) \times 15.0)$$

#### 5. Prerequisite Fit ($F_{\text{prereq}} \in [0, 100]$)
- No prerequisites required: $100.0$
- All prerequisites met (demonstrated score $\ge 60$): $100.0$
- Partially met: Ratio of satisfied prerequisites $\times 100.0$
- None met: $25.0$

#### 6. Duration Fit ($F_{\text{duration}} \in [0, 100]$)
Optimized for working civil service officers:
- $60 - 300$ minutes (1 to 5 hours): $100.0$ (Ideal micro/meso-learning)
- $300 - 1200$ minutes (5 to 20 hours): $85.0$ (Substantial workshop)
- $1200 - 2400$ minutes (20 to 40 hours): $70.0$ (Full institutional program)
- $> 2400$ minutes: $50.0$
- $< 60$ minutes: $75.0$

#### 7. Novelty ($F_{\text{novelty}} \in [0, 100]$)
- Never taken: $100.0$
- Previously completed within 12 months: $10.0$ (Heavy penalty)
- Previously completed $> 12$ months ago: $40.0$ (Refresher value)

---

## 5. Structured Explainability

Each recommendation generates a structured explanation model (`RecommendationReason`) containing:

1. `primary_reason`: Synthesized executive explanation (e.g., *"Directly addresses CRITICAL gap in Survey Design for Target Role Senior Statistical Officer"*).
2. `gap_reason`: Detailed breakdown of the gap priority and required vs. demonstrated score.
3. `role_reason`: Role transition context (Current Role vs. Target Role).
4. `competency_reason`: Mapping between course outcomes and required competency.
5. `level_reason`: Fit analysis between course difficulty (e.g., Level 3) and target requirement (Level 3).
6. `novelty_reason`: Freshness confirmation verifying the officer has not previously completed this material.

In the user interface, officers can click **"Why recommended?"** on any card to open a slide-out drawer displaying this structured rationale along with the complete 7-factor scoring matrix.

---

## 6. Progressive Learning Pathway

The engine constructs an end-to-end, multi-provider sequential roadmap:

1. **Milestone 1 — Conceptual Foundation**: High-impact foundational course (typically iGOT) addressing the highest-priority gap.
2. **Milestone 2 — Applied Simulation / Lab**: Interactive scenario or audit lab (PRAGYA In-Platform) to practice evidenced skills.
3. **Milestone 3 — Advanced Cadre Competency**: Intermediate-to-advanced module (iGOT or NSSTA) consolidating domain methodology.
4. **Milestone 4 — Institutional Immersion**: Rigorous capstone program (NSSTA / TPAC residential or executive workshop) fulfilling target role certification requirements.

---

## 7. Data Models

### 7.1 `learning_items`
- `id` (UUID, Primary Key)
- `provider` (Enum: `IGOT`, `NSSTA`, `PRAGYA`)
- `external_id` (String, unique per provider)
- `title` (String, indexed)
- `description` (Text)
- `url` (String, external launch URL)
- `duration_minutes` (Integer)
- `level` (Integer, 1 to 5)
- `difficulty` (Enum: `FOUNDATIONAL`, `INTERMEDIATE`, `ADVANCED`, `EXPERT`)
- `format` (Enum: `COURSE`, `MODULE`, `WORKSHOP`, `SIMULATION`, `READING`)
- `learning_outcomes` (JSONB Array)
- `prerequisites` (JSONB Array)
- `syllabus` (JSONB Array)
- `source_mode` (Enum: `LIVE`, `MOCK`, `INTERNAL`)
- `status` (Enum: `PUBLISHED`, `DRAFT`, `ARCHIVED`)
- `metadata` (JSONB)

### 7.2 `learning_recommendations`
- `id` (UUID, Primary Key)
- `employee_id` (UUID, Foreign Key to `employees`)
- `learning_item_id` (UUID, Foreign Key to `learning_items`)
- `target_competency_id` (UUID, Foreign Key to `competencies`)
- `skill_gap_id` (UUID, Nullable Foreign Key to `skill_gaps`)
- `score` (Float, 0 to 100)
- `rank` (Integer, 1 to N)
- `priority_level` (Enum: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)
- `reason` (Text, primary explanation)
- `reason_breakdown` (JSONB, full 7-factor dictionary)
- `status` (Enum: `ACTIVE`, `DISMISSED`, `IN_PROGRESS`, `COMPLETED`)

### 7.3 `learning_paths` & `learning_path_items`
- Ordered sequence of milestones linking an employee to curated `learning_items`.

---

## 8. API Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/recommendations/providers` | Lists all active content providers with health and mock flags. |
| `GET` | `/api/v1/recommendations/items` | Searchable catalogue with filters (provider, competency, level, format). |
| `GET` | `/api/v1/recommendations/items/{id}` | Detailed learning item metadata including syllabus and outcomes. |
| `GET` | `/api/v1/recommendations/employee/{employee_id}` | Ranked personalized recommendations for an officer. |
| `POST` | `/api/v1/recommendations/generate` | Triggers on-demand deterministic recommendation recalculation. |
| `PATCH` | `/api/v1/recommendations/{id}/start` | Transitions recommendation status to `IN_PROGRESS`. |
| `PATCH` | `/api/v1/recommendations/{id}/dismiss` | Dismisses a recommendation from active list. |
| `GET` | `/api/v1/recommendations/employee/{employee_id}/path` | Returns sequential cadre learning roadmap. |
| `POST` | `/api/v1/recommendations/generate-path` | Constructs progressive 4-milestone learning path. |

---

## 9. Verification & Test Suite

The recommendation engine is covered by an automated test suite in `apps/api/tests/test_recommendation_engine.py`:

- **Test Suite Results**: 23 dedicated recommendation tests passed; 81 total project tests passed with zero regressions.
- **Scenarios Validated**:
  1. Catalogue retrieval and pagination
  2. Provider filtering (`IGOT`, `NSSTA`, `PRAGYA`)
  3. Competency-based filtering
  4. Candidate generation logic
  5. Critical gap prioritization (Critical gaps consistently rank above lower gaps)
  6. Keyword semantic matcher fallback
  7. Proficiency level fit penalty curve
  8. Prerequisite checking and fit scoring
  9. Duration fit scoring
  10. Novelty scoring & completed training exclusion
  11. Deterministic scoring repeatability (exact match across multiple runs)
  12. Explanation generation and factor breakdown validation
  13. Progressive learning path sequencing
  14. Provider diversity in generated learning paths
  15. Recommendation dismissal workflow
  16. Role-aware recommendation targeting
  17. Error handling for invalid IDs and non-existent records
