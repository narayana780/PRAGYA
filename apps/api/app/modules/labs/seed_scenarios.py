"""
Synthetic Seed Scenarios & Datasets for PRAGYA Virtual Lab.
NOTICE: ALL DATASETS ARE SYNTHETIC DEMONSTRATION DATA — NOT REAL GOVERNMENT DATA.
"""
import uuid
from typing import Any

# Fixed UUIDs for deterministic seed idempotency
DATASET_DQ_ID = uuid.UUID("11111111-2222-3333-4444-555555555501")
DATASET_SAMPLING_ID = uuid.UUID("11111111-2222-3333-4444-555555555502")
DATASET_DESC_ID = uuid.UUID("11111111-2222-3333-4444-555555555503")
DATASET_MISSING_ID = uuid.UUID("11111111-2222-3333-4444-555555555504")

SCENARIO_DQ_ID = uuid.UUID("22222222-3333-4444-5555-666666666601")
SCENARIO_SAMPLING_ID = uuid.UUID("22222222-3333-4444-5555-666666666602")
SCENARIO_DESC_ID = uuid.UUID("22222222-3333-4444-5555-666666666603")
SCENARIO_MISSING_ID = uuid.UUID("22222222-3333-4444-5555-666666666604")


# =============================================================================
# 1. DATA QUALITY AUDIT DATASET & SCENARIO
# =============================================================================
DATA_QUALITY_DATASET_JSON: list[dict[str, Any]] = [
    {"record_id": "REC-1001", "state_code": "07", "district_code": "0701", "household_size": 4, "monthly_expenditure": 14500.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1002", "state_code": "07", "district_code": "0701", "household_size": 5, "monthly_expenditure": 18200.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1003", "state_code": "07", "district_code": "0702", "household_size": 3, "monthly_expenditure": 22000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1004", "state_code": "07", "district_code": "0702", "household_size": 6, "monthly_expenditure": 16400.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1004", "state_code": "07", "district_code": "0702", "household_size": 6, "monthly_expenditure": 16400.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},  # Duplicate
    {"record_id": "REC-1005", "state_code": "07", "district_code": "0703", "household_size": 2, "monthly_expenditure": 31000.0, "primary_source_income": "Manufacturing", "survey_status": "COMPLETED"},
    {"record_id": "REC-1006", "state_code": "09", "district_code": "0901", "household_size": 4, "monthly_expenditure": 12800.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1007", "state_code": "09", "district_code": "0901", "household_size": 5, "monthly_expenditure": 19500.0, "primary_source_income": "agri_cult", "survey_status": "COMPLETED"},  # Inconsistent category
    {"record_id": "REC-1008", "state_code": "09", "district_code": "0902", "household_size": 3, "monthly_expenditure": 24000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1009", "state_code": "09", "district_code": "0902", "household_size": 4, "monthly_expenditure": 15600.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1009", "state_code": "09", "district_code": "0902", "household_size": 4, "monthly_expenditure": 15600.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},  # Duplicate
    {"record_id": "REC-1010", "state_code": "09", "district_code": "0903", "household_size": 7, "monthly_expenditure": 21000.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1011", "state_code": "19", "district_code": "1901", "household_size": 3, "monthly_expenditure": 28500.0, "primary_source_income": "Manufacturing", "survey_status": "COMPLETED"},
    {"record_id": "REC-1012", "state_code": "19", "district_code": "1901", "household_size": 4, "monthly_expenditure": -4500.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},  # Negative Outlier
    {"record_id": "REC-1013", "state_code": "19", "district_code": "1902", "household_size": 5, "monthly_expenditure": 17800.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1014", "state_code": "19", "district_code": "1902", "household_size": 2, "monthly_expenditure": 34000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1015", "state_code": "27", "district_code": "2701", "household_size": 4, "monthly_expenditure": 42000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1016", "state_code": "27", "district_code": "2701", "household_size": 3, "monthly_expenditure": 38000.0, "primary_source_income": "Manufacturing", "survey_status": "COMPLETED"},
    {"record_id": "REC-1017", "state_code": "27", "district_code": "2702", "household_size": 6, "monthly_expenditure": 19200.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1018", "state_code": "27", "district_code": "XX99", "household_size": 4, "monthly_expenditure": 26000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},  # Invalid code
    {"record_id": "REC-1019", "state_code": "33", "district_code": "3301", "household_size": 5, "monthly_expenditure": 23500.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
    {"record_id": "REC-1020", "state_code": "33", "district_code": "3301", "household_size": 3, "monthly_expenditure": 29000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1021", "state_code": "33", "district_code": "3302", "household_size": 4, "monthly_expenditure": 21500.0, "primary_source_income": "Manufacturing", "survey_status": "COMPLETED"},
    {"record_id": "REC-1022", "state_code": "33", "district_code": "3302", "household_size": 2, "monthly_expenditure": 35000.0, "primary_source_income": "Services", "survey_status": "COMPLETED"},
    {"record_id": "REC-1023", "state_code": "33", "district_code": "3303", "household_size": 5, "monthly_expenditure": 18900.0, "primary_source_income": "Agriculture", "survey_status": "COMPLETED"},
]


# =============================================================================
# 2. SURVEY SAMPLING POPULATION DATASET (100 Households)
# =============================================================================
def _generate_sampling_population() -> list[dict[str, Any]]:
    records = []
    strata = [
        ("North", "Rural", 30),
        ("North", "Urban", 20),
        ("South", "Rural", 30),
        ("South", "Urban", 20),
    ]
    uid = 1
    for reg, sec, count in strata:
        for i in range(count):
            records.append({
                "household_id": f"HH-{uid:04d}",
                "region": reg,
                "sector": sec,
                "stratum_code": f"{reg[:1]}-{sec[:1]}",
                "household_size": 2 + ((uid * 3) % 5),
                "income_group": "Low" if (i % 3 == 0) else ("Middle" if (i % 3 == 1) else "High"),
                "head_education": "Primary" if (i % 4 == 0) else ("Secondary" if (i % 4 in (1, 2)) else "Graduate"),
            })
            uid += 1
    return records

SAMPLING_DATASET_JSON = _generate_sampling_population()


# =============================================================================
# 3. DESCRIPTIVE STATISTICS DATASET (30 District Observations)
# =============================================================================
DESCRIPTIVE_DATASET_JSON: list[dict[str, Any]] = [
    {"district_id": f"DST-{i:03d}", "district_name": f"District {chr(65 + (i % 26))}{i}", "per_capita_expenditure_inr": round(12000.0 + (i * 450.0) + ((i % 5) * 1200.0) + (18000.0 if i in (27, 28, 29) else 0.0), 2), "literacy_rate": round(68.5 + (i * 0.7), 1), "reporting_year": 2026}
    for i in range(1, 31)
]


# =============================================================================
# 4. MISSING DATA ANALYSIS DATASET (25 Enterprise Records)
# =============================================================================
MISSING_DATASET_JSON: list[dict[str, Any]] = [
    {"enterprise_id": "ENT-001", "sector": "Manufacturing", "annual_turnover_lakhs": 42.5, "full_time_workers": 12, "gst_registered": True},
    {"enterprise_id": "ENT-002", "sector": "Services", "annual_turnover_lakhs": 18.2, "full_time_workers": 5, "gst_registered": True},
    {"enterprise_id": "ENT-003", "sector": "Manufacturing", "annual_turnover_lakhs": None, "full_time_workers": 8, "gst_registered": True},  # Missing
    {"enterprise_id": "ENT-004", "sector": "Trade", "annual_turnover_lakhs": 12.0, "full_time_workers": 4, "gst_registered": False},
    {"enterprise_id": "ENT-005", "sector": "Services", "annual_turnover_lakhs": 35.0, "full_time_workers": None, "gst_registered": True},  # Missing
    {"enterprise_id": "ENT-006", "sector": "Manufacturing", "annual_turnover_lakhs": None, "full_time_workers": 15, "gst_registered": True},  # Missing
    {"enterprise_id": "ENT-007", "sector": "Trade", "annual_turnover_lakhs": 9.5, "full_time_workers": 3, "gst_registered": False},
    {"enterprise_id": "ENT-008", "sector": "Services", "annual_turnover_lakhs": 28.0, "full_time_workers": 7, "gst_registered": True},
    {"enterprise_id": "ENT-009", "sector": "Manufacturing", "annual_turnover_lakhs": 55.0, "full_time_workers": 18, "gst_registered": True},
    {"enterprise_id": "ENT-010", "sector": "Trade", "annual_turnover_lakhs": None, "full_time_workers": 2, "gst_registered": False},  # Missing
    {"enterprise_id": "ENT-011", "sector": "Services", "annual_turnover_lakhs": 22.4, "full_time_workers": 6, "gst_registered": True},
    {"enterprise_id": "ENT-012", "sector": "Manufacturing", "annual_turnover_lakhs": 38.0, "full_time_workers": 10, "gst_registered": True},
    {"enterprise_id": "ENT-013", "sector": "Trade", "annual_turnover_lakhs": None, "full_time_workers": 4, "gst_registered": False},  # Missing
    {"enterprise_id": "ENT-014", "sector": "Services", "annual_turnover_lakhs": 19.5, "full_time_workers": 5, "gst_registered": True},
    {"enterprise_id": "ENT-015", "sector": "Manufacturing", "annual_turnover_lakhs": 62.0, "full_time_workers": 22, "gst_registered": True},
    {"enterprise_id": "ENT-016", "sector": "Trade", "annual_turnover_lakhs": 14.0, "full_time_workers": 3, "gst_registered": False},
    {"enterprise_id": "ENT-017", "sector": "Services", "annual_turnover_lakhs": None, "full_time_workers": 8, "gst_registered": True},  # Missing
    {"enterprise_id": "ENT-018", "sector": "Manufacturing", "annual_turnover_lakhs": 48.0, "full_time_workers": 14, "gst_registered": True},
    {"enterprise_id": "ENT-019", "sector": "Trade", "annual_turnover_lakhs": 11.2, "full_time_workers": None, "gst_registered": False},  # Missing
    {"enterprise_id": "ENT-020", "sector": "Services", "annual_turnover_lakhs": 31.0, "full_time_workers": 9, "gst_registered": True},
    {"enterprise_id": "ENT-021", "sector": "Manufacturing", "annual_turnover_lakhs": 75.0, "full_time_workers": 25, "gst_registered": True},
    {"enterprise_id": "ENT-022", "sector": "Trade", "annual_turnover_lakhs": 8.0, "full_time_workers": 2, "gst_registered": False},
    {"enterprise_id": "ENT-023", "sector": "Services", "annual_turnover_lakhs": None, "full_time_workers": 6, "gst_registered": True},  # Missing
    {"enterprise_id": "ENT-024", "sector": "Manufacturing", "annual_turnover_lakhs": 51.0, "full_time_workers": 16, "gst_registered": True},
    {"enterprise_id": "ENT-025", "sector": "Trade", "annual_turnover_lakhs": 15.8, "full_time_workers": 4, "gst_registered": False},
]


# =============================================================================
# SCENARIOS SPECIFICATION DEFINITIONS
# =============================================================================
SEED_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": SCENARIO_DQ_ID,
        "title": "National Sample Survey Field Data Quality Audit",
        "description": "Conduct an end-to-end data quality audit on a synthetic multi-district socioeconomic survey dataset. Detect duplicate entries, out-of-range indicators, invalid district codes, and category inconsistencies using official NQAF validation protocols.",
        "scenario_type": "DATA_QUALITY_AUDIT",
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 20,
        "learning_objectives": [
            "Identify structural anomalies including duplicate keys and out-of-range numerical metrics.",
            "Apply official National Quality Assurance Framework (NQAF) validation rules.",
            "Execute controlled data cleansing transformations without compromising survey integrity.",
            "Generate an auditable data verification report for official statistical release.",
        ],
        "instructions": {
            "overview": "You are a Statistical Officer auditing incoming field schedules from the State Socio-Economic Survey. You must ensure 100% compliance with MoSPI NQAF quality dimensions before tabular compilation.",
            "total_steps": 4,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Inspect & Identify Quality Issues",
                    "description": "Inspect the raw survey microdata. Check for duplicated record IDs, out-of-range numeric values, and non-standard administrative codes.",
                    "task_instructions": "Select all anomalies observed in the dataset using the inspection checkboxes.",
                    "action_type": "IDENTIFY_ISSUES",
                },
                {
                    "step_number": 2,
                    "title": "Select Validation Rules",
                    "description": "Select the appropriate NQAF validation rules to enforce against this dataset.",
                    "task_instructions": "Select official validation rules (NQAF_UNIQUE_KEY, NQAF_RANGE_CHECK).",
                    "action_type": "SELECT_VALIDATION_RULE",
                },
                {
                    "step_number": 3,
                    "title": "Apply Cleansing Corrections",
                    "description": "Execute controlled data cleansing actions to remove duplicates and normalize non-standard categories.",
                    "task_instructions": "Select 'Deduplicate and Clean' to apply standard sanitization routines.",
                    "action_type": "APPLY_CORRECTION",
                },
                {
                    "step_number": 4,
                    "title": "Generate Audit Verification Report",
                    "description": "Review final cleaned records and sign off on the data quality certificate.",
                    "task_instructions": "Submit final verification report to complete this lab.",
                    "action_type": "SUBMIT_QUALITY_REPORT",
                },
            ],
        },
        "dataset_id": DATASET_DQ_ID,
        "dataset_meta": {
            "title": "Socioeconomic Survey Raw Field Extract (Synthetic)",
            "description": "Raw multi-district household survey responses containing intentional synthetic anomalies for quality audit practice.",
            "scenario_type": "DATA_QUALITY_AUDIT",
            "row_count": len(DATA_QUALITY_DATASET_JSON),
            "schema_definition": {
                "record_id": {"type": "string", "label": "Record Identifier", "key": True},
                "state_code": {"type": "string", "label": "State Code"},
                "district_code": {"type": "string", "label": "District Code (LGD standard)"},
                "household_size": {"type": "integer", "label": "Household Member Count"},
                "monthly_expenditure": {"type": "float", "label": "Monthly Consumer Expenditure (INR)"},
                "primary_source_income": {"type": "string", "label": "Primary Source of Income"},
                "survey_status": {"type": "string", "label": "Field Schedule Status"},
            },
            "records": DATA_QUALITY_DATASET_JSON,
        },
    },
    {
        "id": SCENARIO_SAMPLING_ID,
        "title": "Stratified Multi-District Household Survey Sampling Design",
        "description": "Formulate a representative probability sampling strategy for an official socio-economic assessment across rural and urban district strata. Choose sampling method, determine sample size, define stratification variables, and evaluate sampling weights.",
        "scenario_type": "SURVEY_SAMPLING",
        "competency_code": "STAT_SAMPLING",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "learning_objectives": [
            "Select appropriate probability sampling methodologies based on population heterogeneity.",
            "Determine statistically adequate sample size balancing survey power and fieldwork resources.",
            "Configure regional and urban-rural stratification with proportional allocation.",
            "Inspect deterministic sample draw and calculate design sampling weights.",
        ],
        "instructions": {
            "overview": "Design an official probability sample for a socio-economic survey covering 100 population units across North and South regional divisions.",
            "total_steps": 4,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Select Probability Sampling Method",
                    "description": "Choose between Simple Random Sampling, Stratified Sampling, or Systematic Sampling.",
                    "task_instructions": "Select STRATIFIED sampling to guarantee balanced representation across urban/rural divides.",
                    "action_type": "SELECT_SAMPLING_METHOD",
                },
                {
                    "step_number": 2,
                    "title": "Determine Sample Size",
                    "description": "Set the target sample size n from population N=100.",
                    "task_instructions": "Enter an optimal sample size (between 25 and 45) for target confidence requirements.",
                    "action_type": "SET_SAMPLE_SIZE",
                },
                {
                    "step_number": 3,
                    "title": "Configure Strata & Allocation Strategy",
                    "description": "Define stratification criteria and allocation method.",
                    "task_instructions": "Select strata variables ('region', 'sector') and 'PROPORTIONAL' allocation.",
                    "action_type": "CONFIGURE_STRATA",
                },
                {
                    "step_number": 4,
                    "title": "Execute Deterministic Simulation",
                    "description": "Simulate drawing the probability sample and inspect stratum representations.",
                    "task_instructions": "Click 'Execute Sample Draw' to compute design weights and sample allocations.",
                    "action_type": "EXECUTE_SIMULATION",
                },
            ],
        },
        "dataset_id": DATASET_SAMPLING_ID,
        "dataset_meta": {
            "title": "Survey Frame Household Population Register (Synthetic)",
            "description": "Synthetic sampling frame containing 100 households across designated regional and urban/rural strata.",
            "scenario_type": "SURVEY_SAMPLING",
            "row_count": len(SAMPLING_DATASET_JSON),
            "schema_definition": {
                "household_id": {"type": "string", "label": "Household Frame ID", "key": True},
                "region": {"type": "string", "label": "Administrative Region"},
                "sector": {"type": "string", "label": "Sector (Rural / Urban)"},
                "stratum_code": {"type": "string", "label": "Stratum Key"},
                "household_size": {"type": "integer", "label": "Household Size"},
                "income_group": {"type": "string", "label": "Income Bracket"},
                "head_education": {"type": "string", "label": "Education Level"},
            },
            "records": SAMPLING_DATASET_JSON,
        },
    },
    {
        "id": SCENARIO_DESC_ID,
        "title": "District Per Capita Household Expenditure Analytics",
        "description": "Inspect synthetic district expenditure microdata, execute authoritative backend computations for central tendency and dispersion (Mean, Median, Min, Max, Standard Deviation), and interpret distribution skewness.",
        "scenario_type": "DESCRIPTIVE_STATISTICS",
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "learning_objectives": [
            "Compute authoritative central tendency metrics (arithmetic mean and median).",
            "Calculate dispersion indicators including range and sample standard deviation.",
            "Analyze the impact of high-expenditure outliers on distribution skewness.",
            "Select robust statistical summary indicators for official publication.",
        ],
        "instructions": {
            "overview": "Compute and interpret authoritative descriptive statistics for per capita consumer expenditure across 30 synthetic district administrative units.",
            "total_steps": 3,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Calculate Central Tendency",
                    "description": "Execute authoritative backend calculation of Mean and Median for district per capita expenditure.",
                    "task_instructions": "Select 'Mean' and 'Median' to trigger authoritative calculation.",
                    "action_type": "CALCULATE_CENTRAL_TENDENCY",
                },
                {
                    "step_number": 2,
                    "title": "Calculate Measures of Dispersion",
                    "description": "Compute Minimum, Maximum, and Standard Deviation to measure inequality and spread.",
                    "task_instructions": "Trigger dispersion analysis on the expenditure variable.",
                    "action_type": "CALCULATE_DISPERSION",
                },
                {
                    "step_number": 3,
                    "title": "Statistical Distribution Interpretation",
                    "description": "Evaluate distribution symmetry based on the relationship between Mean and Median.",
                    "task_instructions": "Diagnose skewness direction and identify the most robust measure of central tendency.",
                    "action_type": "INTERPRET_DISTRIBUTION",
                },
            ],
        },
        "dataset_id": DATASET_DESC_ID,
        "dataset_meta": {
            "title": "District Per Capita Expenditure Indicators (Synthetic)",
            "description": "Synthetic district-level aggregates representing consumption expenditure and literacy indicators.",
            "scenario_type": "DESCRIPTIVE_STATISTICS",
            "row_count": len(DESCRIPTIVE_DATASET_JSON),
            "schema_definition": {
                "district_id": {"type": "string", "label": "District Code", "key": True},
                "district_name": {"type": "string", "label": "District Name"},
                "per_capita_expenditure_inr": {"type": "float", "label": "Per Capita Monthly Expenditure (INR)"},
                "literacy_rate": {"type": "float", "label": "District Literacy Rate (%)"},
                "reporting_year": {"type": "integer", "label": "Survey Year"},
            },
            "records": DESCRIPTIVE_DATASET_JSON,
        },
    },
    {
        "id": SCENARIO_MISSING_ID,
        "title": "Annual Enterprise Survey Non-Response & Imputation Strategy",
        "description": "Analyze missing data patterns across key socioeconomic variables in an enterprise survey dataset. Determine missingness percentage, identify whether data is MCAR/MAR, and select appropriate handling policies (Keep, Drop, or Impute).",
        "scenario_type": "MISSING_DATA_ANALYSIS",
        "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 20,
        "learning_objectives": [
            "Compute item non-response rates across numerical and categorical survey variables.",
            "Diagnose underlying missingness mechanisms (MCAR vs MAR vs MNAR).",
            "Evaluate trade-offs between listwise deletion and statistical imputation.",
            "Assess the post-imputation impact on statistical distribution and sample variance.",
        ],
        "instructions": {
            "overview": "Analyze non-response patterns in an Annual Enterprise Survey extract and select an appropriate imputation policy to preserve statistical power without introducing attrition bias.",
            "total_steps": 4,
            "steps": [
                {
                    "step_number": 1,
                    "title": "Detect Missing Rates",
                    "description": "Scan all variables to quantify the volume and percentage of missing values.",
                    "task_instructions": "Run missing rate detection across enterprise survey attributes.",
                    "action_type": "IDENTIFY_MISSING_RATES",
                },
                {
                    "step_number": 2,
                    "title": "Diagnose Missingness Mechanism",
                    "description": "Determine whether non-response is Missing Completely at Random (MCAR) or Missing at Random (MAR).",
                    "task_instructions": "Select the correct mechanism based on enterprise informality characteristics.",
                    "action_type": "DIAGNOSE_PATTERN",
                },
                {
                    "step_number": 3,
                    "title": "Select Handling Strategy",
                    "description": "Choose between Listwise Deletion, Mean Imputation, or Median/Stratified Imputation.",
                    "task_instructions": "Select 'MEDIAN_IMPUTATION' to safeguard against revenue skewness.",
                    "action_type": "SELECT_STRATEGY",
                },
                {
                    "step_number": 4,
                    "title": "Evaluate Post-Imputation Impact",
                    "description": "Inspect the transformed dataset and evaluate sample preservation metrics.",
                    "task_instructions": "Confirm the final imputation evaluation report.",
                    "action_type": "EVALUATE_IMPUTATION_IMPACT",
                },
            ],
        },
        "dataset_id": DATASET_MISSING_ID,
        "dataset_meta": {
            "title": "Annual Enterprise Survey Microdata Extract (Synthetic)",
            "description": "Synthetic manufacturing and services enterprise records containing realistic item non-response.",
            "scenario_type": "MISSING_DATA_ANALYSIS",
            "row_count": len(MISSING_DATASET_JSON),
            "schema_definition": {
                "enterprise_id": {"type": "string", "label": "Enterprise Registration ID", "key": True},
                "sector": {"type": "string", "label": "Economic Sector"},
                "annual_turnover_lakhs": {"type": "float", "label": "Annual Turnover (INR Lakhs)"},
                "full_time_workers": {"type": "integer", "label": "Full-Time Employees"},
                "gst_registered": {"type": "boolean", "label": "GST Registered Status"},
            },
            "records": MISSING_DATASET_JSON,
        },
    },
]


async def seed_virtual_labs(session) -> int:
    """
    Seeds the 4 canonical synthetic virtual lab scenarios and datasets idempotently.
    Returns the number of scenarios seeded or verified.
    """
    from sqlalchemy import select
    from app.core.logging import logger
    from app.modules.competencies.models import Competency
    from app.modules.labs.models import LabDataset, LabScenario

    logger.info("Seeding PRAGYA Statistical Virtual Lab (Stage 12 Synthetic Scenarios)...")
    seeded_count = 0

    for sc_info in SEED_SCENARIOS:
        ds_meta = sc_info["dataset_meta"]
        ds_id = sc_info["dataset_id"]

        # 1. Dataset idempotency
        ds_stmt = select(LabDataset).where(LabDataset.id == ds_id)
        ds_res = await session.execute(ds_stmt)
        dataset = ds_res.scalar_one_or_none()

        if not dataset:
            dataset = LabDataset(
                id=ds_id,
                title=ds_meta["title"],
                description=ds_meta["description"],
                scenario_type=ds_meta["scenario_type"],
                schema_definition=ds_meta["schema_definition"],
                dataset_json=ds_meta["records"],
                row_count=ds_meta["row_count"],
                is_synthetic=True,
            )
            session.add(dataset)
            await session.flush()
            logger.info(f"Created Synthetic Lab Dataset: {dataset.title}")
        else:
            dataset.dataset_json = ds_meta["records"]
            dataset.row_count = ds_meta["row_count"]
            dataset.is_synthetic = True

        # 2. Resolve target competency
        comp_code = sc_info["competency_code"]
        comp_stmt = select(Competency).where(Competency.code == comp_code)
        comp_res = await session.execute(comp_stmt)
        comp = comp_res.scalar_one_or_none()
        if not comp:
            # Fallback to any competency if code not yet seeded
            first_comp_res = await session.execute(select(Competency).limit(1))
            comp = first_comp_res.scalar_one()

        # 3. Scenario idempotency
        sc_id = sc_info["id"]
        sc_stmt = select(LabScenario).where(LabScenario.id == sc_id)
        sc_res = await session.execute(sc_stmt)
        scenario = sc_res.scalar_one_or_none()

        if not scenario:
            scenario = LabScenario(
                id=sc_id,
                title=sc_info["title"],
                description=sc_info["description"],
                scenario_type=sc_info["scenario_type"],
                competency_id=comp.id,
                difficulty=sc_info["difficulty"],
                estimated_minutes=sc_info["estimated_minutes"],
                learning_objectives=sc_info["learning_objectives"],
                instructions=sc_info["instructions"],
                dataset_id=dataset.id,
                status="READY",
            )
            session.add(scenario)
            await session.flush()
            logger.info(f"Created Virtual Lab Scenario: {scenario.title}")
        else:
            scenario.title = sc_info["title"]
            scenario.description = sc_info["description"]
            scenario.instructions = sc_info["instructions"]
            scenario.learning_objectives = sc_info["learning_objectives"]
            scenario.competency_id = comp.id
            scenario.dataset_id = dataset.id
            scenario.status = "READY"

        seeded_count += 1

    await session.commit()
    logger.info(f"Successfully seeded/verified {seeded_count} Stage 12 Virtual Lab scenarios.")
    return seeded_count

