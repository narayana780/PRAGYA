"""PRAGYA Course Curriculum & Learning Path Content Definitions
Authoritative curriculum content for statistical and official survey methodology courses.
"""
from typing import Any


COURSE_CURRICULUM_CATALOGUE: dict[str, dict[str, Any]] = {
    # Key can be provider_item_id or title
    "IGOT-STAT-004": {
        "course_title": "National Sample Survey Field Methodology & Validation",
        "is_demo_content": True,
        "learning_path_mode": "PRAGYA Demonstration Learning Path",
        "provider_label": "iGOT & PRAGYA",
        "modules": [
            {
                "id": 1,
                "title": "Foundational Theory & Conceptual Framework",
                "duration": "45 mins",
                "description": "Core principles, national statistical architecture, legal mandates, and standard sampling terminology.",
                "is_lab": False,
                "resources": [
                    {
                        "id": "mod1-video-1",
                        "title": "National Statistical Architecture & Official Survey Principles",
                        "type": "VIDEO",
                        "provider": "iGOT",
                        "external_provider": "iGOT",
                        "external_resource_id": None,
                        "external_url": None,
                        "duration_seconds": 2700,
                        "duration_display": "45 mins",
                        "completion_required": True,
                        "description": "Overview of MoSPI survey wings, field operational hierarchy, and core standards under the National Statistical System.",
                    },
                    {
                        "id": "mod1-video-2",
                        "title": "Collection of Statistics Act & Statutory Compliance Protocols",
                        "type": "VIDEO",
                        "provider": "iGOT",
                        "external_provider": "iGOT",
                        "external_resource_id": None,
                        "external_url": None,
                        "duration_seconds": 2700,
                        "duration_display": "45 mins",
                        "completion_required": True,
                        "description": "Legal obligations for informant disclosure, data confidentiality, and official enumerator immunity provisions under Indian law.",
                    },
                    {
                        "id": "mod1-read-1",
                        "title": "Study Guide: Survey Terminology, Sampling Frames & Reference Units",
                        "type": "READING",
                        "provider": "PRAGYA",
                        "external_provider": "PRAGYA",
                        "duration_display": "5 min read",
                        "completion_required": True,
                        "content_markdown": """# Survey Terminology, Sampling Frames & Reference Units

## 1. National Statistical Architecture Overview
Official statistical compilation in India operates under the auspices of the Ministry of Statistics and Programme Implementation (MoSPI), primarily executed through the National Sample Survey Office (NSSO). 

The fundamental premise of large-scale sample surveys is to produce design-unbiased estimates of socioeconomic parameters with quantifiable precision (standard errors).

### Key Administrative Strata
- **State/UT**: Primary domain of estimation for state-level aggregates.
- **National Sample Survey Region**: Formed by grouping contiguous districts within a State having similar agro-climatic features and population densities.
- **FSU (First Stage Unit)**: Census Villages in rural sectors; Urban Frame Survey (UFS) blocks in urban sectors.
- **SSU (Second Stage Unit)**: Selected households or enterprise establishments listed during preliminary field listing.

---

## 2. Regulatory Mandates & Legal Protections
Under the **Collection of Statistics Act, 2008 (Amended 2017)**:
1. **Mandatory Disclosure**: Selected informants are statutorily required to furnish truthful information to designated statistical officers.
2. **Confidentiality Guarantee**: Individual microdata cannot be disclosed, admitted as evidence in judicial proceedings, or used for punitive taxation.
3. **Statistical Immunity**: Field enumerators acting in good faith are indemnified against civil or criminal litigation.

---

## 3. Sampling Frame Integrity
A sampling frame is the physical or electronic listing of all population units from which sample units are selected. 
- In rural India, the primary frame is the **Decennial Population Census Directory of Villages**.
- In urban areas, the **Urban Frame Survey (UFS)** maps and updates non-overlapping geographic blocks of 100–150 households.
- Frame coverage errors (under-coverage and duplication) directly degrade estimation accuracy. Regular frame validation is mandatory prior to sample draw.
""",
                    },
                    {
                        "id": "mod1-read-2",
                        "title": "MoSPI Reference Manual: Standard Field Definitions & Imputation Standards",
                        "type": "READING",
                        "provider": "PRAGYA",
                        "external_provider": "PRAGYA",
                        "duration_display": "4 min read",
                        "completion_required": True,
                        "content_markdown": """# MoSPI Reference Manual: Standard Field Definitions & Imputation

## Standard Reference Periods
Official surveys use mutually exclusive reference periods to record household transactions and demographic events:
- **365-Day Reference Period**: Infrequent capital expenditures (clothing, durable goods, hospitalization, education).
- **30-Day Reference Period**: High-frequency consumables (fuel, light, non-durables).
- **7-Day Reference Period**: Perishable food items (milk, fruits, vegetables) and labour activity status.

## Non-Sampling Error Governance
Non-sampling errors arise from conceptual misunderstandings, respondent fatigue, faulty instruments, or data entry lapses.
- **Field Reconciliation**: All discrepancies identified in computer-assisted schedules must be investigated through supervisory call-backs before schedule finalization.
- **Consistency Verification**: Logical routing checks verify that child responses cannot contradict parent demographic entries.
""",
                    },
                ],
                "knowledge_check": {
                    "title": "Module 1 Knowledge Check: Foundations of Official Surveys",
                    "pass_threshold_percentage": 75.0,
                    "questions": [
                        {
                            "id": "m1-q1",
                            "question": "Under the Collection of Statistics Act, 2008, how is individual informant survey microdata treated?",
                            "options": [
                                "It is publicly published with names and Aadhaar numbers for transparency",
                                "It is strictly confidential and inadmissible as evidence in court or tax proceedings",
                                "It is shared with private marketing agencies for census optimization",
                                "It must be destroyed immediately within 24 hours of collection",
                            ],
                            "correct_index": 1,
                            "explanation": "Section 9 of the Collection of Statistics Act explicitly protects informant data: it remains strictly confidential and cannot be used for tax or legal proceedings.",
                        },
                        {
                            "id": "m1-q2",
                            "question": "What serves as the canonical Primary Sampling Frame for urban household surveys in NSSO?",
                            "options": [
                                "Electoral rolls of Municipal Corporations",
                                "Urban Frame Survey (UFS) blocks maintained and updated by NSSO",
                                "Property tax registers of local civic bodies",
                                "National Postal Index Number (PIN) listings",
                            ],
                            "correct_index": 1,
                            "explanation": "NSSO uses the Urban Frame Survey (UFS) blocks as the canonical First Stage Unit (FSU) frame for urban sector socio-economic inquiries.",
                        },
                        {
                            "id": "m1-q3",
                            "question": "Which reference period is canonically recommended by MoSPI for recording infrequent household durable goods expenditures?",
                            "options": [
                                "Past 24 hours",
                                "Past 7 days",
                                "Past 30 days",
                                "Past 365 days",
                            ],
                            "correct_index": 3,
                            "explanation": "A 365-day recall period minimizes recall bias for high-value, infrequent household capital expenditures like durable goods and institutional healthcare.",
                        },
                        {
                            "id": "m1-q4",
                            "question": "What is the primary First Stage Unit (FSU) in the rural sector for National Sample Surveys?",
                            "options": [
                                "District Headquarter",
                                "Gram Panchayat Secretariat",
                                "Census Village (or Panchayat ward in specified regions)",
                                "Agricultural Holding Plot",
                            ],
                            "correct_index": 2,
                            "explanation": "In the rural sector, the Census Village (as mapped in the latest decennial Population Census) serves as the First Stage Unit (FSU).",
                        },
                    ],
                },
            },
            {
                "id": 2,
                "title": "Applied Methodology & Implementation Protocols",
                "duration": "60 mins",
                "description": "Stratified sampling protocols, Neyman optimal allocation, sample size determination, and practical scenario decisions.",
                "is_lab": False,
                "resources": [
                    {
                        "id": "mod2-video-1",
                        "title": "Multi-Stage Stratified Sampling & Cluster Allocation Protocols",
                        "type": "VIDEO",
                        "provider": "iGOT",
                        "external_provider": "iGOT",
                        "external_resource_id": None,
                        "external_url": None,
                        "duration_seconds": 3600,
                        "duration_display": "60 mins",
                        "completion_required": True,
                        "description": "Deep dive into cluster sampling, PPS without replacement, design effect (deff), and stratum sample weights.",
                    },
                    {
                        "id": "mod2-read-1",
                        "title": "Applied Guidelines: Stratification Strategy, Sample Weighting & Non-Response Mitigation",
                        "type": "READING",
                        "provider": "PRAGYA",
                        "external_provider": "PRAGYA",
                        "duration_display": "6 min read",
                        "completion_required": True,
                        "content_markdown": """# Stratification Strategy, Sample Weighting & Non-Response Mitigation

## 1. Principles of Stratified Sampling
Stratification partitions a heterogeneous target population of size $N$ into $L$ non-overlapping sub-populations (strata) of sizes $N_1, N_2, \\dots, N_L$, such that:
$$\\sum_{h=1}^L N_h = N$$

Stratification achieves three critical goals:
1. **Variance Reduction**: When within-stratum variance $\\sigma_h^2$ is much smaller than across-stratum variance, stratified estimation yields substantial efficiency gains over simple random sampling (SRS).
2. **Administrative Efficiency**: Fieldwork can be localized and monitored independently across strata.
3. **Sub-Domain Precision**: Pre-specified sampling fractions ensure adequate precision for minority geographical or socioeconomic domains.

---

## 2. Sample Allocation Strategies
When allocating a total sample of $n$ units across $L$ strata:

### A. Proportional Allocation
$$n_h = n \\cdot \\frac{N_h}{N}$$
Used when stratum standard deviations $\\sigma_h$ are approximately equal.

### B. Neyman Optimal Allocation
$$n_h = n \\cdot \\frac{N_h \\sigma_h}{\\sum_{k=1}^L N_k \\sigma_k}$$
Used when stratum standard deviations $\\sigma_h$ vary significantly across strata. Stratum with higher variance and larger population receives proportionally greater sample allocations, minimizing overall estimator variance for a fixed sample size $n$.

---

## 3. Design Weight Calculation & Non-Response Adjustment
In a two-stage design with probability of FSU selection $P_{1i}$ and household selection $P_{2ij}$, the base design weight is:
$$w_{ij} = \\frac{1}{P_{1i} \\cdot P_{2ij}}$$

When non-response occurs, an adjustment factor $f_h = \\frac{n_{h,\\text{selected}}}{n_{h,\\text{responded}}}$ inflates base weights to prevent downward estimation bias. A 10%–15% over-sample buffer is routinely incorporated in survey design.
""",
                    },
                ],
                "assignment": {
                    "id": "mod2-assignment",
                    "title": "Practical Survey Design Scenario: District Household Survey Allocation",
                    "instructions": "Review the administrative and statistical parameters of the target district below. Select the appropriate sampling methodology, stratum allocation strategy, non-response buffer, and technical justification.",
                    "scenario": {
                        "district_name": "Dakshina Coastal District",
                        "total_households": 240000,
                        "budgeted_sample_size": 600,
                        "stratum_a": {
                            "name": "Stratum 1: Coastal Fishing & Maritime Belt",
                            "households": 80000,
                            "estimated_std_dev": 18500.0,
                            "description": "High income volatility, seasonal maritime activities",
                        },
                        "stratum_b": {
                            "name": "Stratum 2: Agrarian Inland Plain",
                            "households": 160000,
                            "estimated_std_dev": 9200.0,
                            "description": "Low income volatility, staple crop agriculture",
                        },
                    },
                    "fields": [
                        {
                            "name": "sampling_method",
                            "label": "Select Sampling Methodology",
                            "options": [
                                {"value": "STRATIFIED_TWO_STAGE", "label": "Stratified Two-Stage Probability Sampling (FSUs: Villages/Blocks, SSUs: Households)"},
                                {"value": "SIMPLE_RANDOM", "label": "Unstratified Simple Random Sampling across District Register"},
                                {"value": "CONVENIENCE_SAMPLING", "label": "Quota Sampling at Weekly Village Markets"},
                            ],
                            "correct_value": "STRATIFIED_TWO_STAGE",
                        },
                        {
                            "name": "allocation_strategy",
                            "label": "Select Stratum Allocation Strategy",
                            "options": [
                                {"value": "NEYMAN_OPTIMAL", "label": "Neyman Optimal Allocation (accounts for differing stratum variances)"},
                                {"value": "EQUAL_ALLOCATION", "label": "Equal Allocation (300 households per stratum)"},
                                {"value": "PROPORTIONAL_ALLOCATION", "label": "Proportional Allocation (purely by household count ratio 1:2)"},
                            ],
                            "correct_value": "NEYMAN_OPTIMAL",
                        },
                        {
                            "name": "non_response_buffer",
                            "label": "Non-Response Over-Sampling Buffer",
                            "options": [
                                {"value": "12_PERCENT", "label": "10% - 15% Buffer (Compensates for locked houses and seasonal migration)"},
                                {"value": "ZERO_BUFFER", "label": "0% Buffer (Expect 100% field compliance)"},
                                {"value": "60_PERCENT", "label": "60% Buffer (Triples enumerator workload)"},
                            ],
                            "correct_value": "12_PERCENT",
                        },
                        {
                            "name": "justification_code",
                            "label": "Methodological Justification",
                            "options": [
                                {"value": "VARIANCE_MINIMIZATION", "label": "Stratum 1 has double the standard deviation of Stratum 2; Neyman allocation minimizes overall estimator variance for fixed sample size n=600."},
                                {"value": "EASIEST_ADMINISTRATION", "label": "Coastal areas are pleasant for enumerator lodging."},
                                {"value": "EQUAL_WEIGHTS", "label": "Proportional allocation always guarantees zero standard error."},
                            ],
                            "correct_value": "VARIANCE_MINIMIZATION",
                        },
                    ],
                },
                "knowledge_check": {
                    "title": "Module 2 Knowledge Check: Sampling Methodology & Design Calculations",
                    "pass_threshold_percentage": 75.0,
                    "questions": [
                        {
                            "id": "m2-q1",
                            "question": "When stratum standard deviations differ significantly, which allocation formula minimizes the variance of the overall mean estimator for a fixed sample size?",
                            "options": [
                                "Equal Allocation",
                                "Proportional Allocation",
                                "Neyman Optimal Allocation",
                                "Cluster Purposive Allocation",
                            ],
                            "correct_index": 2,
                            "explanation": "Neyman Optimal Allocation (1934) allocates sample sizes proportionally to $N_h \\sigma_h$, minimizing overall estimation variance.",
                        },
                        {
                            "id": "m2-q2",
                            "question": "What is the Design Effect (Deff) of a complex survey sample?",
                            "options": [
                                "The ratio of the variance of the estimator under complex sampling to the variance under SRS with the same sample size",
                                "The total travel cost incurred by enumerators per village",
                                "The ratio of non-response households to surveyed households",
                                "The multiplier used to calculate interviewer remuneration",
                            ],
                            "correct_index": 0,
                            "explanation": "Deff measures the design efficiency: $\\text{Deff} = \\frac{\\text{Var}_{\\text{complex}}}{\\text{Var}_{\\text{SRS}}}$.",
                        },
                        {
                            "id": "m2-q3",
                            "question": "How is the base sampling weight calculated for a sample unit selected with probability P?",
                            "options": [
                                "$w = P$",
                                "$w = 1 / P$",
                                "$w = 1 - P$",
                                "$w = P^2$",
                            ],
                            "correct_index": 1,
                            "explanation": "The Horvitz-Thompson base design weight is the inverse of the inclusion probability: $w = 1 / P$.",
                        },
                        {
                            "id": "m2-q4",
                            "question": "Why is a non-response buffer (e.g., 10%–15%) incorporated into the preliminary survey sample frame draw?",
                            "options": [
                                "To substitute non-responding households with random neighbors ad-hoc",
                                "To prevent sample attrition from reducing the effective sample size below the required statistical power benchmark",
                                "To guarantee that all enumerators finish before noon",
                                "To inflate final population estimates artificially",
                            ],
                            "correct_index": 1,
                            "explanation": "Non-response buffers preserve the pre-calculated statistical power and confidence limits despite unavoidable field non-contacts or refusals.",
                        },
                    ],
                },
            },
            {
                "id": 3,
                "title": "Official MoSPI Standards & Quality Checkpoints",
                "duration": "45 mins",
                "description": "National Quality Assurance Framework (NQAF-India), 3-tier field validation, and SDMX metadata reporting standards.",
                "is_lab": False,
                "resources": [
                    {
                        "id": "mod3-read-1",
                        "title": "MoSPI Data Quality Assurance Framework (NQAF-India) Implementation",
                        "type": "READING",
                        "provider": "PRAGYA",
                        "external_provider": "PRAGYA",
                        "duration_display": "5 min read",
                        "completion_required": True,
                        "content_markdown": """# MoSPI Data Quality Assurance Framework (NQAF-India)

## 1. Principles of NQAF-India
Adapted from the United Nations National Quality Assurance Framework (UN-NQAF), NQAF-India establishes 19 core quality dimensions categorized into four structural levels:
1. **Managing the Statistical System**: Legal mandates, professional independence, adequate resources.
2. **Managing Institutional Environment**: Impartiality, transparency, confidentiality.
3. **Managing Statistical Processes**: Sound methodology, appropriate statistical procedures, cost-effectiveness.
4. **Managing Statistical Outputs**: Relevance, accuracy, reliability, timeliness, coherence, and comparability.

---

## 2. Multi-Tier Microdata Validation Hierarchy
To ensure zero corruption and logical fidelity in national data releases, field schedules follow a rigorous 3-tier validation protocol:
- **Tier 1 (Interviewer Validation)**: In-field Computer Assisted Personal Interviewing (CAPI) real-time range and logical cross-checks during data entry.
- **Tier 2 (Supervisory Inspection & Concurrent Re-Interview)**: 10% of listed households undergo independent partial re-interviewing by Field Supervisors within 48 hours.
- **Tier 3 (Central Quality Audit Rules)**: Central automated Python/SQL validation scripts enforce demographic consistency, outlier detection (Mahalanobis distance & Box-Cox transformations), and national balancing.
""",
                    },
                    {
                        "id": "mod3-read-2",
                        "title": "Statistical Metadata & International Classifications (NIC 2008 & NCO 2015)",
                        "type": "READING",
                        "provider": "PRAGYA",
                        "external_provider": "PRAGYA",
                        "duration_display": "5 min read",
                        "completion_required": True,
                        "content_markdown": """# Statistical Metadata & International Classifications

## 1. Standard National Classifications
Official socio-economic and economic surveys mandate canonical coding:
- **National Industrial Classification (NIC-2008)**: 5-digit structure aligned with ISIC Rev. 4, categorizing economic activities of enterprises and employed persons.
- **National Classification of Occupations (NCO-2015)**: Aligned with ISCO-08, categorizing occupational job profiles and skill requirements.

## 2. Statistical Data and Metadata eXchange (SDMX)
MoSPI mandates SDMX compliance for open data dissemination. Data Structure Definitions (DSDs) ensure automated machine-to-machine interoperability across international reporting bodies (UN, World Bank, IMF).
""",
                    },
                ],
                "knowledge_check": {
                    "title": "Module 3 Knowledge Check: Quality Standards & Validation",
                    "pass_threshold_percentage": 75.0,
                    "questions": [
                        {
                            "id": "m3-q1",
                            "question": "What is the primary role of Tier 2 Supervisory Validation in MoSPI field operations?",
                            "options": [
                                "To negotiate enumerator daily travel allowances",
                                "To conduct independent concurrent re-interviews on a sample of households to detect enumerator bias and verify listing accuracy",
                                "To rewrite the survey questionnaire midway through the round",
                                "To approve media press releases before statistical compilation",
                            ],
                            "correct_index": 1,
                            "explanation": "Tier 2 supervisory re-interviews verify that enumerators physically visited selected households and recorded factual entries without fabrication.",
                        },
                        {
                            "id": "m3-q2",
                            "question": "Which international metadata standard is adopted by MoSPI to ensure cross-border interoperability of published statistical aggregates?",
                            "options": [
                                "CSV 2.0",
                                "Statistical Data and Metadata eXchange (SDMX)",
                                "HTML5 Semantic Tables",
                                "ISO-9001 Manufacturing Spec",
                            ],
                            "correct_index": 1,
                            "explanation": "SDMX (Statistical Data and Metadata eXchange) is the global standard for exchanging statistical data and metadata.",
                        },
                        {
                            "id": "m3-q3",
                            "question": "Which canonical classification is required in official Indian surveys to categorize the economic activities of enterprises and workers?",
                            "options": [
                                "National Industrial Classification (NIC-2008)",
                                "Harmonized System of Nomenclature (HSN)",
                                "Unified Tariff Schedule",
                                "Census Village Codebook",
                            ],
                            "correct_index": 0,
                            "explanation": "NIC-2008 (National Industrial Classification) is the official classification standard for economic activities in India.",
                        },
                    ],
                },
            },
            {
                "id": 4,
                "title": "Practical Virtual Lab Workbench: Household Survey Sampling",
                "duration": "20 mins",
                "description": "Mandatory practical simulation exercise: execute all 4 analytical steps in the PRAGYA Virtual Lab workbench to earn competency evidence.",
                "is_lab": True,
                "lab_scenario_id": "22222222-3333-4444-5555-666666666602",
                "topics": [
                    "Step 1: Select Probability Sampling Method (Stratified vs SRS)",
                    "Step 2: Determine Sample Size (Statistical Power Analysis)",
                    "Step 3: Configure Strata Variables & Proportional Allocation Strategy",
                    "Step 4: Execute Deterministic MoSPI Simulation Run",
                ],
            },
        ],
        "final_assessment": {
            "title": "Final Course Comprehensive Assessment",
            "description": "Cross-cutting final examination testing foundational principles, sampling calculations, and official quality standards.",
            "pass_threshold_percentage": 70.0,
            "questions": [
                {
                    "id": "fa-q1",
                    "question": "A national household survey requires sub-state regional estimates with equal relative standard errors across both high-density urban areas and sparse desert regions. What sampling framework is most appropriate?",
                    "options": [
                        "Unstratified Simple Random Sampling of entire state",
                        "Stratified Sampling with disproportionate allocation ensuring sufficient sample in sparse regions",
                        "Convenience sampling of households nearest to national highways",
                        "Voluntary online self-reporting questionnaire",
                    ],
                    "correct_index": 1,
                    "explanation": "Stratification with disproportionate allocation guarantees target precision in sparsely populated sub-domains without being overwhelmed by high-density regions.",
                },
                {
                    "id": "fa-q2",
                    "question": "Under NQAF-India guidelines, what is the primary consequence of failing to adjust sampling weights for systematic unit non-response?",
                    "options": [
                        "The overall population aggregates will suffer from non-response bias and underestimate or distort target totals",
                        "The survey budget will automatically lapse",
                        "The data file size will become too large for storage",
                        "The confidence intervals will become artificially negative",
                    ],
                    "correct_index": 0,
                    "explanation": "Systematic unit non-response distorts sample representation; failure to apply non-response re-weighting introduces estimation bias into national aggregates.",
                },
                {
                    "id": "fa-q3",
                    "question": "In a 2-stage stratified design, if village A has selection probability 0.05 and household B within village A has selection probability 0.10, what is the base sampling weight for household B?",
                    "options": [
                        "0.005",
                        "200",
                        "20",
                        "15",
                    ],
                    "correct_index": 1,
                    "explanation": "Overall selection probability $P = 0.05 \\times 0.10 = 0.005$. The base design weight is $w = 1 / P = 1 / 0.005 = 200$.",
                },
                {
                    "id": "fa-q4",
                    "question": "Which legal statute grants MoSPI enumerators official authorization to collect statistical data from citizens while guaranteeing informant confidentiality?",
                    "options": [
                        "Right to Information Act, 2005",
                        "Collection of Statistics Act, 2008 (Amended 2017)",
                        "Indian Penal Code, Section 420",
                        "National Food Security Act, 2013",
                    ],
                    "correct_index": 1,
                    "explanation": "The Collection of Statistics Act, 2008 (Amended 2017) is the governing statutory mandate for official statistical collection in India.",
                },
                {
                    "id": "fa-q5",
                    "question": "What is the key advantage of Neyman Optimal Allocation over Proportional Allocation?",
                    "options": [
                        "It requires zero knowledge of stratum population sizes",
                        "It minimizes the variance of the estimated population total by allocating more samples to strata with higher internal variability",
                        "It ensures that every stratum has exactly 10 households",
                        "It eliminates the need for field supervisors",
                    ],
                    "correct_index": 1,
                    "explanation": "Neyman Optimal Allocation accounts for differing within-stratum standard deviations, achieving the minimum possible variance for a fixed overall sample size.",
                },
                {
                    "id": "fa-q6",
                    "question": "What is the official purpose of SDMX Data Structure Definitions (DSDs) in MoSPI's dissemination policy?",
                    "options": [
                        "To password-protect Excel files distributed to newspapers",
                        "To establish standardized multidimensional data cubes enabling automated exchange with global statistical repositories",
                        "To encrypt enumerator salary records",
                        "To replace all human survey interviewers with automated bots",
                    ],
                    "correct_index": 1,
                    "explanation": "SDMX DSDs define dimensions, attributes, and measures for automated, standardized statistical data interchange across institutions.",
                },
            ],
        },
    }
}


def get_curriculum_for_item(learning_item_id: str, provider_item_id: str | None = None, title: str | None = None) -> dict[str, Any]:
    """Retrieves authoritative curriculum. Matches by provider_item_id, item_id, or defaults to canonical."""
    if provider_item_id and provider_item_id in COURSE_CURRICULUM_CATALOGUE:
        return COURSE_CURRICULUM_CATALOGUE[provider_item_id]

    if learning_item_id in COURSE_CURRICULUM_CATALOGUE:
        return COURSE_CURRICULUM_CATALOGUE[learning_item_id]

    # Default to canonical statistical survey methodology curriculum
    return COURSE_CURRICULUM_CATALOGUE["IGOT-STAT-004"]
