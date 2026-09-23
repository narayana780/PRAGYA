# PRAGYA Competency Framework & Dictionary

> **Stage 4 Documentation — Approved SIH26101 Competency Taxonomy**  
> **Source Reference**: `SIH26101`  
> **Notice**: Prototype demonstration mappings and role assumptions. The competency requirements and proficiency expectations mapped below represent architectural prototype configurations for the PRAGYA competency intelligence engine, not official published cadre recruitment rules or statutory service guidelines.

---

## 1. Domain Taxonomy Architecture

PRAGYA structures statistical and organizational capability using the canonical 4-domain taxonomy approved for SIH26101. Competencies are first-class database entities with immutable codes, rich metadata, and strict relationship integrity.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   COMPETENCY FRAMEWORK ARCHITECTURE                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼ 1                             ▼ 2                             ▼ 3
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│     STATISTICAL      │ │      TECHNICAL       │ │  DIGITAL GOVERNANCE  │ │BEHAVIOURAL/MANAGERIAL│
│  (10 Competencies)   │ │  (12 Competencies)   │ │  (5 Competencies)    │ │  (6 Competencies)    │
│  Code: STATISTICAL   │ │  Code: TECHNICAL     │ │  Code: DIGITAL_GOV   │ │  Code: BEHAVIOURAL   │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
           │                        │                        │                        │
           └────────────────────────┴────────┬───────────────┴────────────────────────┘
                                             │ 1..*
                                             ▼
                               ┌───────────────────────────┐
                               │       COMPETENCIES        │
                               │      (Total: 33)          │
                               └─────────────┬─────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             │ *                             │ *                             │ *
             ▼                               ▼                               ▼
┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
│  competency_requirements  │  │ competency_relationships  │  │    course_competencies    │
│    (Role Expectations)    │  │ (Prerequisites/Lineage)   │  │  (Curriculum Development) │
└─────────────▲─────────────┘  └───────────────────────────┘  └───────────────────────────┘
              │ *
┌─────────────┴─────────────┐
│         job_roles         │
│     (Official Cadre)      │
└───────────────────────────┘
```

---

## 2. Canonical 33 Competencies Dictionary

Every competency record maintains a stable business code, localized operational description, learning objectives, measurement guidance, version number, and source reference.

### 2.1 Domain 1: STATISTICAL (10 Competencies)
| # | Code | Name | Short Description | Source |
|---|------|------|-------------------|--------|
| 1 | `STAT_SURVEY_DESIGN` | Survey Design | Principles of survey instrumentation, questionnaire design, framing, and field protocols. | SIH26101 |
| 2 | `STAT_SAMPLING` | Sampling | Probability sampling designs, stratified random sampling, cluster sampling, and weighting techniques. | SIH26101 |
| 3 | `STAT_NATIONAL_ACCOUNTS` | National Accounts | System of National Accounts (SNA), GDP estimation, supply-use tables, and macroeconomic aggregates. | SIH26101 |
| 4 | `STAT_PRICE_STATISTICS` | Price Statistics | Consumer Price Index (CPI), Wholesale Price Index (WPI), index number theory, and inflation tracking. | SIH26101 |
| 5 | `STAT_LABOUR_STATISTICS` | Labour Statistics | Periodic Labour Force Survey (PLFS) metrics, workforce participation, unemployment ratios, and formalization. | SIH26101 |
| 6 | `STAT_AGRICULTURAL_STATS` | Agricultural Statistics | Crop yield estimation, agricultural censuses, land-use classification, and remote-sensing integration. | SIH26101 |
| 7 | `STAT_INDUSTRIAL_STATS` | Industrial Statistics | Annual Survey of Industries (ASI), Index of Industrial Production (IIP), and enterprise accounting. | SIH26101 |
| 8 | `STAT_SDG_INDICATORS` | SDG Indicators | Sustainable Development Goal monitoring frameworks, national indicator frameworks (NIF), and metadata. | SIH26101 |
| 9 | `STAT_METADATA_STANDARDS` | Metadata Standards | SDMX, DDI, Dublin Core, and national statistical data registry governance frameworks. | SIH26101 |
| 10 | `STAT_DATA_QUALITY_FWK` | Data Quality Frameworks | UN National Quality Assurance Framework (NQAF), error audits, consistency validation, and anomaly checks. | SIH26101 |

### 2.2 Domain 2: TECHNICAL (12 Competencies)
| # | Code | Name | Short Description | Source |
|---|------|------|-------------------|--------|
| 11 | `TECH_PYTHON` | Python | Programming with Python for data engineering, pandas dataframes, automation, and statistical scripting. | SIH26101 |
| 12 | `TECH_R` | R | Statistical computing and graphics with R, tidyverse, econometrics, and survey data processing. | SIH26101 |
| 13 | `TECH_SQL` | SQL | Relational database querying, multi-table aggregation, window functions, and analytics query optimization. | SIH26101 |
| 14 | `TECH_STATA` | Stata | Econometric estimation, panel data modeling, micro-data survey analysis, and do-file pipelines. | SIH26101 |
| 15 | `TECH_SPSS` | SPSS | Survey tabulations, descriptive cross-tabulations, hypothesis testing, and statistical syntax routines. | SIH26101 |
| 16 | `TECH_SAS` | SAS | Enterprise statistical analysis pipelines, data step programming, and large-scale demographic processing. | SIH26101 |
| 17 | `TECH_GIS` | GIS | Spatial data analysis, QGIS/ArcGIS mapping, geo-tagging survey units, and boundary shapefile processing. | SIH26101 |
| 18 | `TECH_DATA_VISUALIZATION` | Data Visualization | Interactive statistical dashboarding, Power BI/Tableau, thematic choropleth generation, and publication graphics. | SIH26101 |
| 19 | `TECH_AI_ML` | AI/ML | Machine learning models, predictive regression, clustering, classification, and natural language processing. | SIH26101 |
| 20 | `TECH_CLOUD_COMPUTING` | Cloud Computing | Cloud architecture, distributed workloads, secure data lakes, and containerized pipeline deployments. | SIH26101 |
| 21 | `TECH_APIS` | APIs | RESTful web services, API integration, data exchange protocols, and automated ingestion feeds. | SIH26101 |
| 22 | `TECH_OPEN_DATA` | Open Data | Open Government Data (OGD) publishing, machine-readable formats (JSON/CSV), and anonymization standards. | SIH26101 |

### 2.3 Domain 3: DIGITAL GOVERNANCE (5 Competencies)
| # | Code | Name | Short Description | Source |
|---|------|------|-------------------|--------|
| 23 | `DIGITAL_CYBERSECURITY` | Cybersecurity | Information security guidelines, ISO 27001 compliance, threat hygiene, and end-point statistical data protection. | SIH26101 |
| 24 | `DIGITAL_DATA_PRIVACY` | Data Privacy | Digital Personal Data Protection (DPDP) Act, de-identification, micro-data anonymization, and confidentiality. | SIH26101 |
| 25 | `DIGITAL_SIGNATURES` | Digital Signatures | Public Key Infrastructure (PKI), e-Sign protocols, digital certificates, and audit trail integrity. | SIH26101 |
| 26 | `DIGITAL_GOV_CLOUD` | Government Cloud | MeghRaj cloud guidelines, government cloud security controls, tenancy isolation, and sovereign hosting. | SIH26101 |
| 27 | `DIGITAL_PUBLIC_INFRA` | Digital Public Infrastructure | India Stack integration, Aadhaar authentication, DigiLocker, and API Setu data exchange frameworks. | SIH26101 |

### 2.4 Domain 4: BEHAVIOURAL / MANAGERIAL (6 Competencies)
| # | Code | Name | Short Description | Source |
|---|------|------|-------------------|--------|
| 28 | `BEHAVIOR_LEADERSHIP` | Leadership | Strategic direction, statistical team mentorship, vision articulation, and institutional stewardship. | SIH26101 |
| 29 | `BEHAVIOR_COMMUNICATION` | Communication | Technical report writing, statistical dissemination to policymakers, public briefing, and stakeholder engagement. | SIH26101 |
| 30 | `BEHAVIOR_PROJECT_MGMT` | Project Management | Survey census lifecycle management, milestone tracking, budget governance, and resource optimization. | SIH26101 |
| 31 | `BEHAVIOR_ETHICS` | Ethics | Fundamental Principles of Official Statistics, integrity, impartiality, and statistical confidentiality. | SIH26101 |
| 32 | `BEHAVIOR_DECISION_MAKING` | Decision Making | Evidence-based governance, risk-weighted statistical judgements, and emergency operational decisioning. | SIH26101 |
| 33 | `BEHAVIOR_CHANGE_MANAGEMENT` | Change Management | Modernizing statistical workflows, institutional adoption of digital tools, and cultural transformation. | SIH26101 |

---

## 3. Proficiency Level Scale & Numerical Scoring

PRAGYA maintains dual representations:
1. **Canonical 1–5 Scale**: Human-readable career level used on reports, dashboards, and role benchmarks.
2. **Normalized 0–100 Score**: Continuous numerical score utilized for gap analysis, regression calculations, and future assessment engines.

```
Score: 0       20 21        40 41        60 61        80 81      100
       ├─────────┤├──────────┤├──────────┤├──────────┤├──────────┤
Scale: [ Level 1 ] [ Level 2 ] [ Level 3 ] [ Level 4 ] [ Level 5 ]
       Awareness   Foundation   Working    Proficient   Advanced
```

| Level | Name | Score Range | Operational Meaning |
|-------|------|-------------|---------------------|
| **1** | **Awareness** | 0 – 20 | Understands basic concepts, vocabulary, and primary principles; requires direct guidance to assist. |
| **2** | **Foundation** | 21 – 40 | Can understand and execute basic, guided tasks under supervision using standard procedures. |
| **3** | **Working** | 41 – 60 | Can independently perform routine tasks and analysis in standard, day-to-day operational environments. |
| **4** | **Proficient** | 61 – 80 | Confidently applies competency to complex, non-standard tasks; troubleshoots anomalies; guides team members. |
| **5** | **Advanced** | 81 – 100 | Authoritative expert; designs institutional frameworks, guides cadre-wide strategy, resolves novel problems. |

### Algorithmic Conversion Utilities
- `score_to_proficiency_level(score: float) -> int`: Returns level integer (1 to 5) clamping inputs strictly within 0–100.
- `level_to_score_range(level: int) -> tuple[int, int]`: Returns standard boundaries (e.g., Level 3 returns `(41, 60)`).

---

## 4. Role Requirement Mapping

Requirements link `job_roles` to `competencies` with a specific `required_level_id`, computed `required_score`, `criticality`, `task_relevance`, and descriptive `rationale`.

### Prototype Role Archetypes
```
┌───────────────────────────┬────────────────────────────────────────────────────────────────┐
│ Role                      │ Requirement Profile Highlights                                 │
├───────────────────────────┼────────────────────────────────────────────────────────────────┤
│ Statistical Officer (SO)  │ • Survey Design (Level 4, Critical)                            │
│                           │ • Sampling (Level 4, Critical)                                 │
│                           │ • Python (Level 3, High)                                       │
│                           │ • Data Visualization (Level 3, High)                           │
│                           │ • Data Quality Frameworks (Level 3, High)                      │
│                           │ • Ethics (Level 4, Critical)                                   │
├───────────────────────────┼────────────────────────────────────────────────────────────────┤
│ Senior Statistical        │ • Survey Design (Level 4, Critical)                            │
│ Officer (SSO)             │ • Sampling (Level 4, Critical)                                 │
│                           │ • SQL (Level 3, High)                                          │
│                           │ • Project Management (Level 3, High)                           │
│                           │ • Data Quality Frameworks (Level 4, Critical)                  │
├───────────────────────────┼────────────────────────────────────────────────────────────────┤
│ Assistant Director (AD)   │ • National Accounts (Level 4, Critical)                        │
│                           │ • Price Statistics (Level 4, Critical)                         │
│                           │ • Decision Making (Level 4, High)                              │
│                           │ • Project Management (Level 4, High)                           │
├───────────────────────────┼────────────────────────────────────────────────────────────────┤
│ Deputy Director (DD)      │ • National Accounts (Level 5, Critical)                        │
│                           │ • Leadership (Level 4, High)                                   │
│                           │ • Change Management (Level 4, High)                            │
│                           │ • Decision Making (Level 5, Critical)                          │
├───────────────────────────┼────────────────────────────────────────────────────────────────┤
│ Joint Director (JD)       │ • Leadership (Level 5, Critical)                               │
│                           │ • Ethics (Level 5, Critical)                                   │
│                           │ • Decision Making (Level 5, Critical)                          │
│                           │ • Change Management (Level 5, High)                            │
└───────────────────────────┴────────────────────────────────────────────────────────────────┘
```

---

## 5. Criticality & Task Relevance Classification

- **Criticality Enum**:
  - `CRITICAL`: Essential core competency; inability to perform directly impedes cadre statutory obligations.
  - `HIGH`: Major contributor to primary work responsibilities.
  - `MEDIUM`: Supporting capability that enhances operational speed and accuracy.
  - `LOW`: Ancillary skill with indirect or situational impact.
- **Task Relevance Enum**:
  - `HIGH`: Used on a daily or weekly basis in active assignments.
  - `MEDIUM`: Applied periodically during quarterly/annual statistical cycles.
  - `LOW`: Applied occasionally or in specialized project scenarios.

---

## 6. Competency Prerequisites & Directed Graph

To enable future personalized learning pathways, the `competency_relationships` table captures prerequisite and lineage dependencies:

```
[ Survey Design ] ──────────(PREREQUISITE)──────────► [ Sampling ]
[ Python ] ─────────────────(PREREQUISITE)──────────► [ Data Visualization ]
[ Python ] ─────────────────(PREREQUISITE)──────────► [ AI/ML ]
[ SQL ] ────────────────────(RELATED)───────────────► [ Python ]
[ National Accounts ] ──────(RELATED)───────────────► [ Price Statistics ]
[ Cybersecurity ] ──────────(PREREQUISITE)──────────► [ Government Cloud ]
[ Leadership ] ─────────────(RELATED)───────────────► [ Change Management ]
```

---

## 7. Course & Programme Mapping Abstraction

PRAGYA prepares clean, decoupled junction entities for learning resource development:
- `courses` & `course_competencies`: Maps modular training assets to target competencies with coverage levels (`INTRODUCTORY`, `FOUNDATION`, `WORKING`, `ADVANCED`).
- `training_programmes` & `training_programme_competencies`: Prepares structured alignment for institutional NSSTA (National Statistical Systems Training Academy) and TPAC (Training Programme Advisory Committee) curricula.

---

## 8. Source Provenance & Compliance

All 33 taxonomy entries carry the authoritative `source_reference` marker:
- Primary Taxonomy: `SIH26101`
- Standards Alignment: UN Fundamental Principles of Official Statistics, National Quality Assurance Framework (NQAF), System of National Accounts (SNA), DPDP Act 2023.
- Provenance Guarantee: No invented or unauthorized domain entries exist outside the canonical four.
