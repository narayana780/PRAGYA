"""
=============================================================================
PRAGYA SEED DATA SCRIPT — ORGANIZATIONAL & COMPETENCY DOMAIN
=============================================================================
NOTICE:
SYNTHETIC DEMONSTRATION DATA — NOT REAL GOVERNMENT DATA.
All officer names, cadre numbers, designations, and records contained herein
are completely fictional and generated strictly for system verification and
demonstration of the PRAGYA Competency Platform.
Taxonomy reference: SIH26101 (33 Competencies across 4 Canonical Domains).
=============================================================================
"""

import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.logging import logger
from app.db.session import AsyncSessionLocal

# Stage 5 Assessment & Evidence Models
from app.modules.assessments.evidence_service import EvidenceService
from app.modules.assessments.models import (
    Assessment,
    AssessmentCompetency,
    AssessmentQuestion,
    CompetencyEvidence,
)
from app.modules.assessments.scoring_service import CompetencyScoringService
from app.modules.assessments.seed_data import (
    DIAGNOSTIC_ASSESSMENT_DESC,
    DIAGNOSTIC_ASSESSMENT_TITLE,
    DIAGNOSTIC_COMPETENCY_CODES,
    DIAGNOSTIC_QUESTIONS,
)
from app.modules.competencies.constants import CANONICAL_DOMAINS, PROFICIENCY_LEVELS

# Stage 4 Competency Domain Models
from app.modules.competencies.models import (
    Competency,
    CompetencyDomain,
    CompetencyRelationship,
    CompetencyRequirement,
    Course,
    CourseCompetency,
    ProficiencyLevel,
    TrainingProgramme,
    TrainingProgrammeCompetency,
)

# Stage 7 Learning Items & Recommendation Engine Models & Services
from app.modules.courses.models import LearningItem, LearningItemCompetency

# Stage 3 Domain Models
from app.modules.departments.models import Department
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.recommendations.seed_catalogue import SYNTHETIC_LEARNING_ITEMS
from app.modules.recommendations.service import (
    LearningPathService,
    RecommendationService,
)
from app.modules.training_history.models import TrainingHistory


async def seed_database():
    """Seeds organizational reference data, competencies, and demo employee records idempotently."""
    logger.info("Initiating PRAGYA database seeding (SYNTHETIC DEMONSTRATION DATA)...")

    async with AsyncSessionLocal() as session:
        # =========================================================================
        # 1. DEPARTMENTS (Stage 3 - 5 Departments)
        # =========================================================================
        departments_data = [
            {
                "code": "DES",
                "name": "Department of Economics and Statistics",
                "description": "Nodal division responsible for economic indicators, surveys, and state-level statistical aggregation.",
            },
            {
                "code": "NAD",
                "name": "National Accounts Division",
                "description": "Prepares National Accounts aggregates including Gross Domestic Product (GDP) and Input-Output Tables.",
            },
            {
                "code": "NSSO",
                "name": "National Sample Survey Office",
                "description": "Conducts large-scale socio-economic sample surveys across India for policy planning.",
            },
            {
                "code": "PCLD",
                "name": "Price & Cost of Living Division",
                "description": "Compiles and publishes Consumer Price Index (CPI) and related indices.",
            },
            {
                "code": "CPD",
                "name": "Coordination & Publication Division",
                "description": "Coordinates official statistical publications, statistical standards, and inter-agency coordination.",
            },
        ]

        department_map = {}
        for dep_info in departments_data:
            stmt = select(Department).where(Department.code == dep_info["code"])
            result = await session.execute(stmt)
            dept = result.scalar_one_or_none()
            if not dept:
                dept = Department(
                    id=uuid.uuid4(),
                    code=dep_info["code"],
                    name=dep_info["name"],
                    description=dep_info["description"],
                    is_active=True,
                )
                session.add(dept)
                await session.flush()
                logger.info(f"Created Department: {dept.name} ({dept.code})")
            department_map[dep_info["code"]] = dept

        # =========================================================================
        # 2. JOB ROLES (Stage 3 - 5 Official Cadre Levels)
        # =========================================================================
        job_roles_data = [
            {
                "code": "SO",
                "name": "Statistical Officer",
                "career_level": "Level 8",
                "description": "Primary officer managing survey fieldwork, data validation, and preliminary tabular compilation.",
            },
            {
                "code": "SSO",
                "name": "Senior Statistical Officer",
                "career_level": "Level 10",
                "description": "Supervises statistical investigations, complex estimation methodologies, and sub-divisional analytics.",
            },
            {
                "code": "AD",
                "name": "Assistant Director",
                "career_level": "Level 11",
                "description": "Division unit head overseeing survey methodology, quality assurance, and econometric modeling.",
            },
            {
                "code": "DD",
                "name": "Deputy Director",
                "career_level": "Level 12",
                "description": "Directs core statistical programmes, inter-ministerial data sharing, and official releases.",
            },
            {
                "code": "JD",
                "name": "Joint Director",
                "career_level": "Level 13",
                "description": "Senior executive leading policy evaluation, national statistical frameworks, and modernization.",
            },
        ]

        role_map = {}
        for role_info in job_roles_data:
            stmt = select(JobRole).where(JobRole.code == role_info["code"])
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                role = JobRole(
                    id=uuid.uuid4(),
                    code=role_info["code"],
                    name=role_info["name"],
                    career_level=role_info["career_level"],
                    description=role_info["description"],
                    is_active=True,
                )
                session.add(role)
                await session.flush()
                logger.info(f"Created Job Role: {role.name} ({role.code})")
            role_map[role_info["code"]] = role

        # =========================================================================
        # 3. EMPLOYEES (Stage 3 - 4 Cadre Officers)
        # =========================================================================
        employees_data = [
            {
                "employee_code": "EMP-0001",
                "full_name": "Ananya Sharma",
                "designation": "Statistical Officer",
                "department_code": "DES",
                "job_role_code": "SO",
                "target_role_code": "SSO",
                "experience_years": 5,
                "education": "M.Sc. Statistics",
                "preferred_language": "English",
                "current_assignment": "Survey Data Analysis",
                "profile_image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80",
            },
            {
                "employee_code": "EMP-0002",
                "full_name": "Rajesh Verma",
                "designation": "Senior Statistical Officer",
                "department_code": "NAD",
                "job_role_code": "SSO",
                "target_role_code": "AD",
                "experience_years": 9,
                "education": "Ph.D. Economics",
                "preferred_language": "English",
                "current_assignment": "GDP Estimation Framework",
                "profile_image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
            },
            {
                "employee_code": "EMP-0003",
                "full_name": "Priya Patel",
                "designation": "Assistant Director",
                "department_code": "NSSO",
                "job_role_code": "AD",
                "target_role_code": "DD",
                "experience_years": 12,
                "education": "M.Stat. (ISI Kolkata)",
                "preferred_language": "Hindi",
                "current_assignment": "Field Survey Sampling Design",
                "profile_image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&q=80",
            },
            {
                "employee_code": "EMP-0004",
                "full_name": "Vikram Malhotra",
                "designation": "Statistical Officer",
                "department_code": "PCLD",
                "job_role_code": "SO",
                "target_role_code": "SSO",
                "experience_years": 3,
                "education": "M.Sc. Applied Statistics",
                "preferred_language": "English",
                "current_assignment": "CPI Basket Weight Revision",
                "profile_image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80",
            },
        ]

        employee_map = {}
        for emp_info in employees_data:
            stmt = select(Employee).where(Employee.employee_code == emp_info["employee_code"])
            result = await session.execute(stmt)
            emp = result.scalar_one_or_none()
            if not emp:
                emp = Employee(
                    id=uuid.uuid4(),
                    employee_code=emp_info["employee_code"],
                    full_name=emp_info["full_name"],
                    designation=emp_info["designation"],
                    department_id=department_map[emp_info["department_code"]].id,
                    job_role_id=role_map[emp_info["job_role_code"]].id,
                    target_role_id=role_map[emp_info["target_role_code"]].id if emp_info["target_role_code"] else None,
                    experience_years=emp_info["experience_years"],
                    education=emp_info["education"],
                    preferred_language=emp_info["preferred_language"],
                    current_assignment=emp_info["current_assignment"],
                    profile_image_url=emp_info["profile_image_url"],
                    is_active=True,
                )
                session.add(emp)
                await session.flush()
                logger.info(f"Created Employee: {emp.full_name} ({emp.employee_code})")
            employee_map[emp_info["employee_code"]] = emp

        # =========================================================================
        # 4. TRAINING HISTORY (Stage 3 - 12 Synthetic Records)
        # =========================================================================
        training_records = [
            {"employee_code": "EMP-0001", "title": "Advanced Survey Sampling & Weight Calibration", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-STAT-401", "completed_at": datetime(2026, 3, 15, tzinfo=UTC), "status": "COMPLETED", "score": 92.5, "duration_hours": 36.0, "certificate_reference": "CERT-IGOT-2026-8821"},
            {"employee_code": "EMP-0001", "title": "National Accounts Statistics & SUT Framework", "provider": "NSSTA (National Statistical Systems Training Academy)", "provider_type": "NSSTA_TPAC", "programme_id": "NSSTA-TPAC-2025-08", "completed_at": datetime(2025, 11, 20, tzinfo=UTC), "status": "COMPLETED", "score": 88.0, "duration_hours": 45.0, "certificate_reference": "CERT-NSSTA-2025-4109"},
            {"employee_code": "EMP-0001", "title": "Official Statistical Quality Standards (NQAF)", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-GOV-108", "completed_at": datetime(2025, 8, 10, tzinfo=UTC), "status": "COMPLETED", "score": 95.0, "duration_hours": 20.0, "certificate_reference": "CERT-IGOT-2025-1923"},
            {"employee_code": "EMP-0001", "title": "Python & R for Large-Scale Data Analytics", "provider": "NSSTA (National Statistical Systems Training Academy)", "provider_type": "NSSTA_TPAC", "programme_id": "NSSTA-TECH-2025-02", "completed_at": datetime(2025, 5, 18, tzinfo=UTC), "status": "COMPLETED", "score": 91.0, "duration_hours": 60.0, "certificate_reference": "CERT-NSSTA-2025-2831"},
            {"employee_code": "EMP-0002", "title": "Macroeconomic Indicators & Quarterly GDP Modeling", "provider": "NSSTA (National Statistical Systems Training Academy)", "provider_type": "NSSTA_TPAC", "programme_id": "NSSTA-MACRO-2025-01", "completed_at": datetime(2025, 9, 12, tzinfo=UTC), "status": "COMPLETED", "score": 94.0, "duration_hours": 50.0, "certificate_reference": "CERT-NSSTA-2025-5012"},
            {"employee_code": "EMP-0002", "title": "Digital Governance & Data Protection Act 2023", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-LAW-204", "completed_at": datetime(2025, 4, 10, tzinfo=UTC), "status": "COMPLETED", "score": 89.0, "duration_hours": 15.0, "certificate_reference": "CERT-IGOT-2025-3310"},
            {"employee_code": "EMP-0002", "title": "Time Series Econometrics with Seasonal Adjustment", "provider": "Reserve Bank Staff College", "provider_type": "OTHER", "programme_id": "RBSC-ECON-2024", "completed_at": datetime(2024, 12, 5, tzinfo=UTC), "status": "COMPLETED", "score": 87.5, "duration_hours": 30.0, "certificate_reference": "CERT-RBSC-2024-1029"},
            {"employee_code": "EMP-0003", "title": "Multistage Stratified Sampling & Non-response Imputation", "provider": "NSSTA (National Statistical Systems Training Academy)", "provider_type": "NSSTA_TPAC", "programme_id": "NSSTA-SAMP-2025-04", "completed_at": datetime(2025, 10, 1, tzinfo=UTC), "status": "COMPLETED", "score": 96.0, "duration_hours": 40.0, "certificate_reference": "CERT-NSSTA-2025-7819"},
            {"employee_code": "EMP-0003", "title": "Leadership & Change Management for Senior Officers", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-LEAD-301", "completed_at": datetime(2025, 6, 25, tzinfo=UTC), "status": "COMPLETED", "score": 90.0, "duration_hours": 24.0, "certificate_reference": "CERT-IGOT-2025-9921"},
            {"employee_code": "EMP-0004", "title": "Consumer Price Index Compilation Methodologies", "provider": "NSSTA (National Statistical Systems Training Academy)", "provider_type": "NSSTA_TPAC", "programme_id": "NSSTA-CPI-2026-01", "completed_at": datetime(2026, 1, 20, tzinfo=UTC), "status": "COMPLETED", "score": 85.0, "duration_hours": 35.0, "certificate_reference": "CERT-NSSTA-2026-1102"},
            {"employee_code": "EMP-0004", "title": "Foundational Statistics & Ethics in Public Data", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-STAT-101", "completed_at": datetime(2025, 7, 14, tzinfo=UTC), "status": "COMPLETED", "score": 93.0, "duration_hours": 18.0, "certificate_reference": "CERT-IGOT-2025-7734"},
            {"employee_code": "EMP-0004", "title": "Data Visualization & Dashboard Design for Policy", "provider": "iGOT Karmayogi", "provider_type": "IGOT", "course_id": "IGOT-TECH-205", "completed_at": datetime(2025, 3, 30, tzinfo=UTC), "status": "COMPLETED", "score": 88.5, "duration_hours": 25.0, "certificate_reference": "CERT-IGOT-2025-6612"},
        ]

        for tr_info in training_records:
            emp = employee_map[tr_info["employee_code"]]
            stmt = select(TrainingHistory).where(
                TrainingHistory.employee_id == emp.id,
                TrainingHistory.title == tr_info["title"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                record = TrainingHistory(
                    id=uuid.uuid4(),
                    employee_id=emp.id,
                    title=tr_info["title"],
                    provider=tr_info["provider"],
                    provider_type=tr_info["provider_type"],
                    course_id=tr_info.get("course_id"),
                    programme_id=tr_info.get("programme_id"),
                    completed_at=tr_info["completed_at"],
                    status=tr_info["status"],
                    score=tr_info["score"],
                    duration_hours=tr_info["duration_hours"],
                    certificate_reference=tr_info["certificate_reference"],
                )
                session.add(record)
                logger.info(f"Added Training Record: '{record.title}' for {emp.full_name}")

        # =========================================================================
        # 5. COMPETENCY DOMAINS (Stage 4 - 4 Canonical Domains)
        # =========================================================================
        domain_map = {}
        for d_info in CANONICAL_DOMAINS:
            stmt = select(CompetencyDomain).where(CompetencyDomain.code == d_info["code"])
            result = await session.execute(stmt)
            domain = result.scalar_one_or_none()
            if not domain:
                domain = CompetencyDomain(
                    id=uuid.uuid4(),
                    code=d_info["code"],
                    name=d_info["name"],
                    description=d_info["description"],
                    display_order=d_info["display_order"],
                    is_active=True,
                )
                session.add(domain)
                await session.flush()
                logger.info(f"Created Competency Domain: {domain.name} ({domain.code})")
            domain_map[d_info["code"]] = domain

        # =========================================================================
        # 6. PROFICIENCY LEVELS (Stage 4 - 5 Levels)
        # =========================================================================
        level_map = {}
        for p_info in PROFICIENCY_LEVELS:
            stmt = select(ProficiencyLevel).where(ProficiencyLevel.level_number == p_info["level_number"])
            result = await session.execute(stmt)
            level = result.scalar_one_or_none()
            if not level:
                level = ProficiencyLevel(
                    id=uuid.uuid4(),
                    level_number=p_info["level_number"],
                    name=p_info["name"],
                    description=p_info["description"],
                    minimum_score=p_info["minimum_score"],
                    maximum_score=p_info["maximum_score"],
                    display_order=p_info["display_order"],
                    is_active=True,
                )
                session.add(level)
                await session.flush()
                logger.info(f"Created Proficiency Level: Level {level.level_number} - {level.name}")
            level_map[p_info["level_number"]] = level

        # =========================================================================
        # 7. EXACTLY 33 CANONICAL COMPETENCIES (SIH26101 Taxonomy)
        # =========================================================================
        competencies_data = [
            # DOMAIN 1: STATISTICAL (10 Competencies)
            {
                "code": "STAT_SURVEY_DESIGN",
                "name": "Survey Design",
                "domain_code": "STATISTICAL",
                "short_description": "Methodology, questionnaire structuring, pilot testing, and schedule design for official socioeconomic surveys.",
                "description": "Comprehensive design and operationalization of large-scale statistical survey instruments, including defining target populations, conceptualizing inquiry schedules, testing response consistency, and pre-testing survey instruments.",
                "learning_objectives": "Formulate valid survey questions; design standardized enumerator schedules; implement cognitive pre-testing; mitigate survey non-sampling bias.",
                "measurement_guidance": "Assessed via questionnaire evaluation, instrument review, and field schedule pilot exercises.",
                "aliases": "Questionnaire Design, Schedule Formulation, Survey Methodology",
            },
            {
                "code": "STAT_SAMPLING",
                "name": "Sampling",
                "domain_code": "STATISTICAL",
                "short_description": "Probability sampling techniques, stratification, multistage cluster design, and sampling weight calibration.",
                "description": "Theory and practical application of probability sampling in official statistical systems, covering simple random sampling, systematic sampling, probability proportional to size (PPS), multistage stratification, and calculation of design weights and non-response adjustments.",
                "learning_objectives": "Compute sample size required for target confidence limits; construct sampling frames; calculate multipliers and post-stratification weights.",
                "measurement_guidance": "Evaluated via mathematical frame construction exercises and survey weight derivation tests.",
                "aliases": "Sampling Theory, Stratification, Weight Calibration, Multistage Sampling",
            },
            {
                "code": "STAT_NATIONAL_ACCOUNTS",
                "name": "National Accounts",
                "domain_code": "STATISTICAL",
                "short_description": "System of National Accounts (SNA), GDP estimation, Gross Value Added (GVA), and Supply-Use Tables.",
                "description": "Methodologies and standards for national accounting under UN SNA 2008 guidelines, measuring production, income, and expenditure accounts, compiling supply and use tables (SUT), and reconciling economic aggregates across agricultural, industrial, and service sectors.",
                "learning_objectives": "Explain production, income, and expenditure approaches to GDP; compile supply-use matrices; identify deflators for constant price estimates.",
                "measurement_guidance": "Evaluated through sectoral GVA compilation problems and macroeconomic aggregation case studies.",
                "aliases": "GDP Compilation, SNA 2008, GVA Estimation, Supply-Use Tables",
            },
            {
                "code": "STAT_PRICE_STATISTICS",
                "name": "Price Statistics",
                "domain_code": "STATISTICAL",
                "short_description": "Consumer Price Index (CPI), Wholesale Price Index (WPI), and index formula construction.",
                "description": "Compilation, index aggregation, item basket selection, and price collection methodologies for Consumer Price Indices (CPI-Rural, CPI-Urban, CPI-Combined) and Wholesale Price Indices (WPI) using Laspeyres and geometric mean formulations.",
                "learning_objectives": "Construct price relatives; update consumption weighting baskets; manage quality adjustments and seasonal price imputations.",
                "measurement_guidance": "Tested via basket weighting calculations and index aggregation exercises.",
                "aliases": "CPI, WPI, Inflation Measurement, Index Number Theory",
            },
            {
                "code": "STAT_LABOUR_STATISTICS",
                "name": "Labour Statistics",
                "domain_code": "STATISTICAL",
                "short_description": "Periodic Labour Force Survey (PLFS), labour force participation, and employment classification.",
                "description": "Frameworks for measuring workforce dynamics, Labour Force Participation Rate (LFPR), Worker Population Ratio (WPR), Unemployment Rate (UR), and principal vs. subsidiary activity status following ILO recommendations and Indian statistical norms.",
                "learning_objectives": "Classify employment status under Usual Status and Current Weekly Status (CWS); compute standard labour indicators; interpret industrial sector classifications.",
                "measurement_guidance": "Assessed through activity classification drills and labour rate computations from PLFS unit data.",
                "aliases": "PLFS, Employment Statistics, LFPR, Activity Classification",
            },
            {
                "code": "STAT_AGRICULTURAL_STATISTICS",
                "name": "Agricultural Statistics",
                "domain_code": "STATISTICAL",
                "short_description": "Crop estimation, yield assessment, land utilization statistics, and livestock census.",
                "description": "Techniques for estimating area, yield, and production of major agricultural crops, including crop cutting experiments (CCE), agricultural census compilation, and rainfall/seasonal index adjustments.",
                "learning_objectives": "Conduct supervised crop-cutting experiment analytics; evaluate agricultural census tables; calculate harvest yield indices.",
                "measurement_guidance": "Assessed via CCE simulation data analysis and land-use category verification exercises.",
                "aliases": "Crop Cutting Experiments, Agricultural Census, Harvest Yield Analytics",
            },
            {
                "code": "STAT_INDUSTRIAL_STATISTICS",
                "name": "Industrial Statistics",
                "domain_code": "STATISTICAL",
                "short_description": "Annual Survey of Industries (ASI), Index of Industrial Production (IIP), and NIC classification.",
                "description": "Methods for monitoring the organized and unorganized manufacturing sectors, including conducting the Annual Survey of Industries, constructing the Index of Industrial Production (IIP), and applying National Industrial Classification (NIC).",
                "learning_objectives": "Apply NIC codes to manufacturing units; aggregate ASI input/output data; compute IIP item weights and growth indicators.",
                "measurement_guidance": "Evaluated via industrial classification drills and monthly IIP compilation tests.",
                "aliases": "ASI, IIP, Manufacturing Statistics, Industrial Classification",
            },
            {
                "code": "STAT_SDG_INDICATORS",
                "name": "SDG Indicators",
                "domain_code": "STATISTICAL",
                "short_description": "Sustainable Development Goals (SDG) National Indicator Framework (NIF) tracking and reporting.",
                "description": "Alignment, computation, and reporting of national and sub-national progress against the UN 2030 Agenda for Sustainable Development, utilizing MoSPI's National Indicator Framework across all 17 Goals.",
                "learning_objectives": "Map official datasets to SDG target indicators; compute baseline vs target trajectories; identify data gaps in disaggregated reporting.",
                "measurement_guidance": "Assessed through NIF indicator derivation and dashboard reporting audits.",
                "aliases": "NIF, UN SDG 2030, Global Indicator Framework, Target Tracking",
            },
            {
                "code": "STAT_METADATA_STANDARDS",
                "name": "Metadata Standards",
                "domain_code": "STATISTICAL",
                "short_description": "SDMX (Statistical Data and Metadata eXchange), DDI, and statistical classification repositories.",
                "description": "Design and implementation of international metadata architectures, concepts, code-lists, and data structure definitions (DSDs) under SDMX and Data Documentation Initiative (DDI) standards.",
                "learning_objectives": "Draft SDMX structural artifacts; document survey data dictionaries; construct standardized code-lists.",
                "measurement_guidance": "Evaluated via SDMX artifact design and statistical dictionary audits.",
                "aliases": "SDMX, DDI, Data Documentation, Statistical Taxonomy",
            },
            {
                "code": "STAT_DATA_QUALITY_FRAMEWORKS",
                "name": "Data Quality Frameworks",
                "domain_code": "STATISTICAL",
                "short_description": "National Quality Assurance Framework (NQAF), data integrity verification, and validation rules.",
                "description": "Application of principles of official statistics, compliance audits, and quality dimensions (relevance, accuracy, timeliness, accessibility, interpretability, and coherence) derived from UN NQAF standards.",
                "learning_objectives": "Perform data quality audits; implement logical consistency checks; construct quality reports for official releases.",
                "measurement_guidance": "Evaluated through dataset validation challenges and quality audit report production.",
                "aliases": "NQAF, Data Validation, Quality Auditing, Statistical Integrity",
            },

            # DOMAIN 2: TECHNICAL (12 Competencies)
            {
                "code": "TECH_PYTHON",
                "name": "Python",
                "domain_code": "TECHNICAL",
                "short_description": "Data processing, statistical analysis, and scripting with pandas, numpy, and scipy.",
                "description": "Core Python programming for official statistics, including data cleansing, frame manipulation, vectorization, algorithmic validation, and automated batch reporting.",
                "learning_objectives": "Manipulate large survey tabular data using pandas; perform statistical testing with scipy; automate recurring ETL pipelines.",
                "measurement_guidance": "Evaluated via coding assessments and data processing scripting tests.",
                "aliases": "Python Programming, pandas, numpy, Python Data Analytics",
            },
            {
                "code": "TECH_R",
                "name": "R",
                "domain_code": "TECHNICAL",
                "short_description": "Statistical modeling, survey analysis packages (survey, srvyr), and tidyverse in R.",
                "description": "Using R and the Comprehensive R Archive Network (CRAN) ecosystem for specialized statistical modeling, survey sampling calculations with complex survey designs, and markdown reporting.",
                "learning_objectives": "Analyze complex survey designs with the survey package; conduct regression modeling; produce reproducible RMarkdown reports.",
                "measurement_guidance": "Assessed via R scripting assignments and complex sampling estimation scripts.",
                "aliases": "R Programming, RStats, tidyverse, Survey Package",
            },
            {
                "code": "TECH_SQL",
                "name": "SQL",
                "domain_code": "TECHNICAL",
                "short_description": "Relational queries, analytical window functions, indexing, and survey data aggregation.",
                "description": "Relational database querying and structured data manipulation using SQL, including joins, window functions, CTEs, aggregation pipelines, and database optimization.",
                "learning_objectives": "Write complex analytical SQL queries; design normalized schemas; perform multi-table aggregation on census/survey tables.",
                "measurement_guidance": "Tested through query optimization drills and practical SQL problem sets.",
                "aliases": "SQL Queries, PostgreSQL, Database Querying, Relational Queries",
            },
            {
                "code": "TECH_STATA",
                "name": "Stata",
                "domain_code": "TECHNICAL",
                "short_description": "Econometric modeling, microdata analysis, do-file automation, and survey regression.",
                "description": "Using Stata for econometric analysis, cross-sectional and panel data regressions, survey weighting estimation (svyset), and automated do-file research workflows.",
                "learning_objectives": "Configure svyset for complex survey designs; run instrumental variable and panel models; manage reproducible do-file pipelines.",
                "measurement_guidance": "Assessed via do-file construction and regression output interpretation.",
                "aliases": "Stata Software, Do-files, Microdata Econometrics",
            },
            {
                "code": "TECH_SPSS",
                "name": "SPSS",
                "domain_code": "TECHNICAL",
                "short_description": "Survey tabulation, cross-tabulations, descriptive statistics, and SPSS syntax.",
                "description": "Statistical Package for the Social Sciences (SPSS) operationalization for survey microdata extraction, weight application, contingency table generation, and syntax scripting.",
                "learning_objectives": "Generate official statistical tables; apply variable and value labels; write repeatable SPSS syntax routines.",
                "measurement_guidance": "Evaluated via cross-tabulation accuracy and syntax file automation.",
                "aliases": "IBM SPSS, SPSS Syntax, Cross-Tabulation",
            },
            {
                "code": "TECH_SAS",
                "name": "SAS",
                "domain_code": "TECHNICAL",
                "short_description": "Enterprise SAS programming, macro facility, PROC procedures, and large-scale data manipulation.",
                "description": "Base SAS and advanced SAS procedures (PROC SQL, PROC SURVEYSELECT, PROC SURVEYMEANS) for managing enterprise administrative records and legacy statistical databases.",
                "learning_objectives": "Write SAS DATA steps and macros; execute PROC SURVEY procedures; validate large-scale data extracts.",
                "measurement_guidance": "Assessed through SAS code debugging and proc procedure outputs.",
                "aliases": "SAS Programming, Base SAS, SAS Macros",
            },
            {
                "code": "TECH_GIS",
                "name": "GIS",
                "domain_code": "TECHNICAL",
                "short_description": "Geographic Information Systems, spatial data analysis, choropleth mapping, and QGIS.",
                "description": "Spatial analysis, thematic mapping, geocoding, boundary shapefile integration, and geospatial visualization of district and state-level statistical indicators using QGIS and geospatial libraries.",
                "learning_objectives": "Overlay statistical survey data with administrative shapefiles; generate publication-grade choropleth maps; detect spatial clustering.",
                "measurement_guidance": "Evaluated through spatial data integration challenges and map cartography reviews.",
                "aliases": "Geographic Information Systems, QGIS, Spatial Analytics, Thematic Mapping",
            },
            {
                "code": "TECH_DATA_VISUALIZATION",
                "name": "Data Visualization",
                "domain_code": "TECHNICAL",
                "short_description": "Interactive charting, dashboard storytelling, visual hierarchy, and policy dashboards.",
                "description": "Visual representation of statistical findings using principles of graphic design, cognitive perception, chart selection (scatter, violin, Sankey, heatmaps), and interactive dashboard frameworks.",
                "learning_objectives": "Select appropriate visual forms for statistical distributions; design high-density dashboards; communicate uncertainty visually.",
                "measurement_guidance": "Assessed via dashboard design reviews and chart communication exercises.",
                "aliases": "Data Storytelling, Dashboard Design, Information Graphics",
            },
            {
                "code": "TECH_AI_ML",
                "name": "AI/ML",
                "domain_code": "TECHNICAL",
                "short_description": "Machine learning, statistical learning, automated classification, and predictive modeling.",
                "description": "Application of supervised and unsupervised machine learning algorithms, text classification for economic activity descriptions, anomaly detection in microdata, and predictive imputation.",
                "learning_objectives": "Train and evaluate predictive models; implement automated text categorization for NIC codes; detect statistical outliers with unsupervised learning.",
                "measurement_guidance": "Evaluated through model validation pipelines and classification accuracy benchmarks.",
                "aliases": "Machine Learning, Artificial Intelligence, Predictive Modeling",
            },
            {
                "code": "TECH_CLOUD_COMPUTING",
                "name": "Cloud Computing",
                "domain_code": "TECHNICAL",
                "short_description": "Cloud infrastructure, scalable data storage, containerization, and virtual servers.",
                "description": "Understanding cloud architectures, virtual machines, cloud object storage, secure network perimeters, and elastic computation for hosting national statistical data platforms.",
                "learning_objectives": "Deploy containerized applications; configure secure bucket storage; optimize cloud compute resource allocation.",
                "measurement_guidance": "Assessed via cloud architecture design reviews and deployment simulations.",
                "aliases": "Cloud Infrastructure, Cloud Storage, Virtualization",
            },
            {
                "code": "TECH_APIS",
                "name": "APIs",
                "domain_code": "TECHNICAL",
                "short_description": "RESTful API design, data dissemination endpoints, JSON/XML schemas, and API security.",
                "description": "Design, consumption, and governance of Application Programming Interfaces for modern statistical data exchange, inter-ministerial data pipelines, and public dissemination portals.",
                "learning_objectives": "Design OpenAPI-compliant REST endpoints; implement API rate limiting and token authentication; consume external administrative APIs.",
                "measurement_guidance": "Evaluated through API endpoint implementation and contract compliance tests.",
                "aliases": "REST APIs, Web Services, Data Exchange Endpoints",
            },
            {
                "code": "TECH_OPEN_DATA",
                "name": "Open Data",
                "domain_code": "TECHNICAL",
                "short_description": "Open Data Policy (NDSAP), machine-readable data publishing, and anonymization protocols.",
                "description": "Implementation of the National Data Sharing and Accessibility Policy (NDSAP), licensing, machine-readable format compliance (CSV, JSON), statistical disclosure control, and data portal publishing.",
                "learning_objectives": "Apply Statistical Disclosure Control (SDC) to microdata; format datasets for open government portals; establish data licensing documentation.",
                "measurement_guidance": "Assessed through anonymization testing and open data packaging exercises.",
                "aliases": "NDSAP, Machine Readable Data, Open Government Data",
            },

            # DOMAIN 3: DIGITAL GOVERNANCE (5 Competencies)
            {
                "code": "DIGITAL_CYBERSECURITY",
                "name": "Cybersecurity",
                "domain_code": "DIGITAL_GOVERNANCE",
                "short_description": "Information security protocols, CERT-In compliance, access controls, and cyber hygiene.",
                "description": "Principles and practices of securing government IT systems, compliance with Indian Computer Emergency Response Team (CERT-In) guidelines, zero-trust access management, and vulnerability management.",
                "learning_objectives": "Implement least-privilege role-based access; recognize phishing and threat vectors; comply with government cyber incident reporting.",
                "measurement_guidance": "Tested via cybersecurity scenario analysis and security compliance audits.",
                "aliases": "InfoSec, Cyber Hygiene, CERT-In Compliance, Access Control",
            },
            {
                "code": "DIGITAL_DATA_PRIVACY",
                "name": "Data Privacy",
                "domain_code": "DIGITAL_GOVERNANCE",
                "short_description": "Digital Personal Data Protection (DPDP) Act 2023, confidentiality, and consent management.",
                "description": "Legal, ethical, and operational compliance with the DPDP Act 2023, respondent privacy guarantees under the Collection of Statistics Act, purpose limitation, and data fiduciary obligations.",
                "learning_objectives": "Identify personal vs non-personal identifiers; implement data anonymization and pseudonimization; enforce respondent confidentiality safeguards.",
                "measurement_guidance": "Assessed through privacy impact assessment case studies and regulatory compliance reviews.",
                "aliases": "DPDP Act, Personal Data Protection, Statistical Confidentiality",
            },
            {
                "code": "DIGITAL_DIGITAL_SIGNATURES",
                "name": "Digital Signatures",
                "domain_code": "DIGITAL_GOVERNANCE",
                "short_description": "e-Sign, PKI infrastructure, DSC integration, and legal validity under the IT Act.",
                "description": "Public Key Infrastructure (PKI) concepts, Digital Signature Certificates (DSC), Aadhaar-based e-Sign integration, and non-repudiation in official government workflows under the Information Technology Act.",
                "learning_objectives": "Explain asymmetric cryptography and certificate authorities; integrate digital signing into electronic document workflows; verify signature validity.",
                "measurement_guidance": "Evaluated via cryptographic verification drills and e-office workflow integration scenarios.",
                "aliases": "DSC, e-Sign, PKI, Electronic Verification",
            },
            {
                "code": "DIGITAL_GOVERNMENT_CLOUD",
                "name": "Government Cloud",
                "domain_code": "DIGITAL_GOVERNANCE",
                "short_description": "MeitY empanelled cloud (GI Cloud / MeghRaj), data residency, and procurement standards.",
                "description": "Architecture, operational governance, and regulatory requirements of the Government of India GI Cloud (MeghRaj) initiative, data localization rules, and security certification standards.",
                "learning_objectives": "Evaluate cloud service provider compliance against MeitY guidelines; ensure data sovereignty and residency; plan disaster recovery architectures.",
                "measurement_guidance": "Assessed through cloud compliance reviews and government cloud architecture evaluations.",
                "aliases": "MeghRaj, GI Cloud, MeitY Cloud Guidelines, Data Sovereignty",
            },
            {
                "code": "DIGITAL_DIGITAL_PUBLIC_INFRASTRUCTURE",
                "name": "Digital Public Infrastructure",
                "domain_code": "DIGITAL_GOVERNANCE",
                "short_description": "India Stack, Aadhaar, UPI, DigiLocker, and interoperability protocols in governance.",
                "description": "Architecture and integration opportunities with India's foundational Digital Public Infrastructure (DPI), including identity (Aadhaar), payments (UPI), verifiable credentials (DigiLocker), and Open Network protocols.",
                "learning_objectives": "Describe the multi-layered India Stack architecture; leverage DigiLocker for document verification; integrate interoperable DPI primitives.",
                "measurement_guidance": "Assessed via DPI architecture mapping and case studies on digital public goods.",
                "aliases": "India Stack, DPI, DigiLocker, Digital Public Goods",
            },

            # DOMAIN 4: BEHAVIOURAL / MANAGERIAL (6 Competencies)
            {
                "code": "BEHAVIOR_LEADERSHIP",
                "name": "Leadership",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "Public leadership, team empowerment, strategic direction, and public value creation.",
                "description": "Inspiring, guiding, and directing multi-disciplinary statistical teams, setting organizational direction, fostering collaborative public sector culture, and achieving strategic modernization goals.",
                "learning_objectives": "Articulate clear vision for survey divisions; resolve team operational bottlenecks; mentor junior statistical cadres.",
                "measurement_guidance": "Evaluated through situational judgment tests, leadership simulations, and peer assessments.",
                "aliases": "Public Leadership, Team Direction, Visionary Management",
            },
            {
                "code": "BEHAVIOR_COMMUNICATION",
                "name": "Communication",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "Statistical communication, policy briefing, executive writing, and public dissemination.",
                "description": "Translating complex statistical findings, methodologies, and macroeconomic models into plain, clear, and actionable insights for policymakers, media, and citizens.",
                "learning_objectives": "Draft concise policy briefs from complex survey reports; deliver effective statistical presentations; communicate data limitations transparently.",
                "measurement_guidance": "Assessed via policy brief writing exercises and oral presentation reviews.",
                "aliases": "Statistical Storytelling, Policy Writing, Executive Communication",
            },
            {
                "code": "BEHAVIOR_PROJECT_MANAGEMENT",
                "name": "Project Management",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "Survey operational planning, milestone tracking, budget governance, and risk mitigation.",
                "description": "Managing the end-to-end lifecycle of national survey programmes, resource allocation, field team coordination, timeline tracking, and risk management.",
                "learning_objectives": "Construct survey operational work breakdown structures (WBS); monitor critical path milestones; manage budget variances.",
                "measurement_guidance": "Evaluated through project plan simulations and risk mitigation exercises.",
                "aliases": "Survey Administration, Operational Planning, Milestone Management",
            },
            {
                "code": "BEHAVIOR_ETHICS",
                "name": "Ethics",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "UN Fundamental Principles of Official Statistics, integrity, impartiality, and objectivity.",
                "description": "Upholding high standards of ethical conduct, professional independence, statistical transparency, prevention of data manipulation, and strict adherence to the UN Fundamental Principles of Official Statistics.",
                "learning_objectives": "Apply UN Fundamental Principles in practical situations; ensure impartial statistical dissemination; safeguard data integrity against undue influence.",
                "measurement_guidance": "Tested via ethical dilemma simulations and professional integrity case studies.",
                "aliases": "Statistical Ethics, Professional Independence, Integrity, Impartiality",
            },
            {
                "code": "BEHAVIOR_DECISION_MAKING",
                "name": "Decision Making",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "Evidence-based decisions, risk evaluation, trade-off analysis, and crisis management.",
                "description": "Systematic assessment of analytical alternatives, weighing methodology trade-offs (e.g. speed vs. precision), and formulating sound administrative and statistical decisions.",
                "learning_objectives": "Evaluate competing statistical methodologies; analyze trade-offs under uncertainty; defend methodological decisions rationally.",
                "measurement_guidance": "Evaluated through scenario-based decision challenges and risk analysis reviews.",
                "aliases": "Evidence-Based Decision Making, Risk Appraisal, Trade-Off Analysis",
            },
            {
                "code": "BEHAVIOR_CHANGE_MANAGEMENT",
                "name": "Change Management",
                "domain_code": "BEHAVIOURAL_MANAGERIAL",
                "short_description": "Digital modernization, stakeholder adoption, organizational readiness, and continuous learning.",
                "description": "Guiding statistical divisions through digital transformation, adoption of modern tools (e.g., Computer Assisted Personal Interviewing - CAPI), overcoming operational resistance, and building capacity.",
                "learning_objectives": "Develop change communication strategies for technological transitions; manage field resistance to new survey tools; build learning agility.",
                "measurement_guidance": "Assessed via change impact assessments and transformation strategy proposals.",
                "aliases": "Organizational Transformation, Capacity Building, Modernization",
            },
        ]

        competency_map = {}
        for c_info in competencies_data:
            stmt = select(Competency).where(Competency.code == c_info["code"])
            result = await session.execute(stmt)
            comp = result.scalar_one_or_none()
            if not comp:
                comp = Competency(
                    id=uuid.uuid4(),
                    code=c_info["code"],
                    name=c_info["name"],
                    domain_id=domain_map[c_info["domain_code"]].id,
                    short_description=c_info["short_description"],
                    description=c_info["description"],
                    learning_objectives=c_info["learning_objectives"],
                    measurement_guidance=c_info["measurement_guidance"],
                    aliases=c_info["aliases"],
                    is_active=True,
                    version="1.0",
                    source_reference="SIH26101",
                )
                session.add(comp)
                await session.flush()
                logger.info(f"Created Competency: {comp.name} ({comp.code})")
            competency_map[c_info["code"]] = comp

        # =========================================================================
        # 8. COMPETENCY RELATIONSHIPS (Prerequisites and Related Capabilities)
        # =========================================================================
        relationships_data = [
            {"source": "TECH_PYTHON", "target": "TECH_DATA_VISUALIZATION", "type": "PREREQUISITE", "strength": 0.9},
            {"source": "TECH_PYTHON", "target": "TECH_AI_ML", "type": "PREREQUISITE", "strength": 1.0},
            {"source": "STAT_SURVEY_DESIGN", "target": "STAT_SAMPLING", "type": "PREREQUISITE", "strength": 1.0},
            {"source": "STAT_SAMPLING", "target": "STAT_DATA_QUALITY_FRAMEWORKS", "type": "RELATED", "strength": 0.8},
            {"source": "STAT_NATIONAL_ACCOUNTS", "target": "STAT_PRICE_STATISTICS", "type": "RELATED", "strength": 0.85},
            {"source": "DIGITAL_CYBERSECURITY", "target": "DIGITAL_DATA_PRIVACY", "type": "RELATED", "strength": 0.9},
            {"source": "BEHAVIOR_LEADERSHIP", "target": "BEHAVIOR_CHANGE_MANAGEMENT", "type": "PREREQUISITE", "strength": 0.85},
            {"source": "TECH_SQL", "target": "TECH_PYTHON", "type": "RELATED", "strength": 0.75},
        ]

        for rel_info in relationships_data:
            src = competency_map[rel_info["source"]]
            tgt = competency_map[rel_info["target"]]
            stmt = select(CompetencyRelationship).where(
                CompetencyRelationship.source_competency_id == src.id,
                CompetencyRelationship.target_competency_id == tgt.id,
            )
            result = await session.execute(stmt)
            rel = result.scalar_one_or_none()
            if not rel:
                rel = CompetencyRelationship(
                    id=uuid.uuid4(),
                    source_competency_id=src.id,
                    target_competency_id=tgt.id,
                    relationship_type=rel_info["type"],
                    strength=rel_info["strength"],
                )
                session.add(rel)
                logger.info(f"Created Relationship: {src.code} -> {tgt.code} ({rel_info['type']})")

        # =========================================================================
        # 9. JOB ROLE COMPETENCY REQUIREMENTS (Distinct Profiles for all 5 Cadre Roles)
        # =========================================================================
        role_requirements_data = {
            # 1. Statistical Officer (Level 8) - Operational fieldwork & survey analysis
            "SO": [
                {"comp": "STAT_SURVEY_DESIGN", "lvl": 4, "score": 75, "crit": "CRITICAL", "rel": "HIGH", "urgency": "HIGH", "prio": 1, "rationale": "Directly conducts field inquiry schedule verification and enumerator oversight."},
                {"comp": "STAT_SAMPLING", "lvl": 4, "score": 70, "crit": "HIGH", "rel": "HIGH", "urgency": "HIGH", "prio": 2, "rationale": "Applies sampling weights and verifies primary sampling unit selection integrity."},
                {"comp": "STAT_DATA_QUALITY_FRAMEWORKS", "lvl": 3, "score": 55, "crit": "HIGH", "rel": "HIGH", "urgency": "HIGH", "prio": 3, "rationale": "Executes data quality audits and logical consistency checks on field microdata."},
                {"comp": "TECH_PYTHON", "lvl": 3, "score": 50, "crit": "MEDIUM", "rel": "HIGH", "urgency": "HIGH", "prio": 4, "rationale": "Scripts automated validation checks and preliminary data manipulation."},
                {"comp": "TECH_DATA_VISUALIZATION", "lvl": 3, "score": 50, "crit": "MEDIUM", "rel": "MEDIUM", "urgency": "MEDIUM", "prio": 5, "rationale": "Creates graphical representations of survey tabular findings."},
                {"comp": "TECH_SQL", "lvl": 2, "score": 35, "crit": "MEDIUM", "rel": "MEDIUM", "urgency": "MEDIUM", "prio": 6, "rationale": "Queries regional statistical relational databases."},
                {"comp": "TECH_GIS", "lvl": 2, "score": 30, "crit": "LOW", "rel": "MEDIUM", "urgency": "HIGH", "prio": 7, "rationale": "Assists with spatial boundary mapping for primary sampling units."},
                {"comp": "BEHAVIOR_ETHICS", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "urgency": "HIGH", "prio": 8, "rationale": "Safeguards respondent confidentiality and impartial observation in field investigations."},
                {"comp": "BEHAVIOR_COMMUNICATION", "lvl": 3, "score": 50, "crit": "MEDIUM", "rel": "MEDIUM", "urgency": "MEDIUM", "prio": 9, "rationale": "Instructs field teams and communicates survey guidelines clearly."},
            ],
            # 2. Senior Statistical Officer (Level 10) - Advanced estimation & divisional analytics
            "SSO": [
                {"comp": "STAT_SURVEY_DESIGN", "lvl": 4, "score": 80, "crit": "CRITICAL", "rel": "HIGH", "prio": 1, "rationale": "Leads sub-divisional survey instrument customization and pre-testing."},
                {"comp": "STAT_SAMPLING", "lvl": 4, "score": 80, "crit": "CRITICAL", "rel": "HIGH", "prio": 2, "rationale": "Calculates complex multipliers and non-response adjustments."},
                {"comp": "STAT_NATIONAL_ACCOUNTS", "lvl": 3, "score": 55, "crit": "HIGH", "rel": "MEDIUM", "prio": 3, "rationale": "Reconciles survey aggregates into macroeconomic National Accounts inputs."},
                {"comp": "STAT_DATA_QUALITY_FRAMEWORKS", "lvl": 4, "score": 70, "crit": "HIGH", "rel": "HIGH", "prio": 4, "rationale": "Oversees NQAF compliance reviews across state data submissions."},
                {"comp": "TECH_PYTHON", "lvl": 3, "score": 60, "crit": "HIGH", "rel": "HIGH", "prio": 5, "rationale": "Develops production analytics pipelines for official statistical publications."},
                {"comp": "TECH_R", "lvl": 3, "score": 55, "crit": "MEDIUM", "rel": "HIGH", "prio": 6, "rationale": "Runs complex sampling variance estimates and econometric regressions."},
                {"comp": "TECH_SQL", "lvl": 3, "score": 55, "crit": "MEDIUM", "rel": "HIGH", "prio": 7, "rationale": "Extracts and aggregates multi-year longitudinal microdata."},
                {"comp": "TECH_DATA_VISUALIZATION", "lvl": 4, "score": 65, "crit": "HIGH", "rel": "HIGH", "prio": 8, "rationale": "Designs executive visual summaries for ministry briefings."},
                {"comp": "BEHAVIOR_PROJECT_MANAGEMENT", "lvl": 3, "score": 55, "crit": "HIGH", "rel": "HIGH", "prio": 9, "rationale": "Coordinates divisional survey timelines and enumerator milestones."},
                {"comp": "BEHAVIOR_LEADERSHIP", "lvl": 3, "score": 50, "crit": "MEDIUM", "rel": "MEDIUM", "prio": 10, "rationale": "Mentors statistical officers and junior technical cadres."},
                {"comp": "BEHAVIOR_ETHICS", "lvl": 4, "score": 80, "crit": "HIGH", "rel": "HIGH", "prio": 11, "rationale": "Upholds strict adherence to the Collection of Statistics Act."},
            ],
            # 3. Assistant Director (Level 11) - Unit head & methodology oversight
            "AD": [
                {"comp": "STAT_NATIONAL_ACCOUNTS", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 1, "rationale": "Directs sectoral GVA estimation and input-output table modeling."},
                {"comp": "STAT_SDG_INDICATORS", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 2, "rationale": "Coordinates national SDG indicator tracking across line ministries."},
                {"comp": "STAT_METADATA_STANDARDS", "lvl": 4, "score": 70, "crit": "HIGH", "rel": "HIGH", "prio": 3, "rationale": "Enforces SDMX data structure definitions and national metadata compliance."},
                {"comp": "TECH_PYTHON", "lvl": 3, "score": 50, "crit": "MEDIUM", "rel": "MEDIUM", "prio": 4, "rationale": "Reviews analytical scripts and reproducible pipelines."},
                {"comp": "TECH_APIS", "lvl": 3, "score": 45, "crit": "MEDIUM", "rel": "MEDIUM", "prio": 5, "rationale": "Oversees automated data exchange interfaces with state portals."},
                {"comp": "DIGITAL_DATA_PRIVACY", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 6, "rationale": "Ensures DPDP Act 2023 compliance across all departmental microdata releases."},
                {"comp": "BEHAVIOR_LEADERSHIP", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 7, "rationale": "Directs statistical teams and fosters culture of technical innovation."},
                {"comp": "BEHAVIOR_PROJECT_MANAGEMENT", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 8, "rationale": "Controls budget allocation and contract deliverables for major survey rounds."},
                {"comp": "BEHAVIOR_COMMUNICATION", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 9, "rationale": "Authors high-level policy briefs and represents department in inter-agency forums."},
            ],
            # 4. Deputy Director (Level 12) - Programme director & policy evaluation
            "DD": [
                {"comp": "STAT_SDG_INDICATORS", "lvl": 5, "score": 85, "crit": "CRITICAL", "rel": "HIGH", "prio": 1, "rationale": "Represents India in international UN statistical forums and multi-agency reporting."},
                {"comp": "STAT_DATA_QUALITY_FRAMEWORKS", "lvl": 5, "score": 85, "crit": "CRITICAL", "rel": "HIGH", "prio": 2, "rationale": "Formulates national quality assurance policies and audit frameworks."},
                {"comp": "TECH_OPEN_DATA", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 3, "rationale": "Governs NDSAP compliance and public microdata dissemination."},
                {"comp": "DIGITAL_DIGITAL_PUBLIC_INFRASTRUCTURE", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 4, "rationale": "Integrates national statistical datasets into India Stack and DigiLocker ecosystems."},
                {"comp": "DIGITAL_CYBERSECURITY", "lvl": 3, "score": 55, "crit": "HIGH", "rel": "HIGH", "prio": 5, "rationale": "Ensures critical statistical infrastructure complies with CERT-In mandates."},
                {"comp": "BEHAVIOR_LEADERSHIP", "lvl": 5, "score": 85, "crit": "CRITICAL", "rel": "HIGH", "prio": 6, "rationale": "Guides strategic modernisation and talent development across divisions."},
                {"comp": "BEHAVIOR_DECISION_MAKING", "lvl": 5, "score": 85, "crit": "CRITICAL", "rel": "HIGH", "prio": 7, "rationale": "Makes definitive judgements on statistical methodology controversies and trade-offs."},
                {"comp": "BEHAVIOR_CHANGE_MANAGEMENT", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 8, "rationale": "Steers institutional transitions from legacy methods to cloud-native analytics."},
            ],
            # 5. Joint Director (Level 13) - Executive leadership & modernization
            "JD": [
                {"comp": "STAT_SDG_INDICATORS", "lvl": 5, "score": 90, "crit": "CRITICAL", "rel": "HIGH", "prio": 1, "rationale": "Sets national statistical goals and advises ministry on economic indicator veracity."},
                {"comp": "STAT_METADATA_STANDARDS", "lvl": 5, "score": 85, "crit": "HIGH", "rel": "HIGH", "prio": 2, "rationale": "Champions nationwide adoption of SDMX across federal and state statistical bodies."},
                {"comp": "DIGITAL_GOVERNMENT_CLOUD", "lvl": 4, "score": 75, "crit": "HIGH", "rel": "HIGH", "prio": 3, "rationale": "Oversees long-term data repository strategy on MeghRaj cloud."},
                {"comp": "BEHAVIOR_LEADERSHIP", "lvl": 5, "score": 95, "crit": "CRITICAL", "rel": "HIGH", "prio": 4, "rationale": "Executive steward of official statistical integrity and administrative cadre excellence."},
                {"comp": "BEHAVIOR_CHANGE_MANAGEMENT", "lvl": 5, "score": 90, "crit": "CRITICAL", "rel": "HIGH", "prio": 5, "rationale": "Leads organizational transformation toward AI-augmented statistical workflows."},
                {"comp": "BEHAVIOR_DECISION_MAKING", "lvl": 5, "score": 95, "crit": "CRITICAL", "rel": "HIGH", "prio": 6, "rationale": "Advises Cabinet Secretariat and NITI Aayog on official economic releases."},
                {"comp": "BEHAVIOR_COMMUNICATION", "lvl": 5, "score": 90, "crit": "HIGH", "rel": "HIGH", "prio": 7, "rationale": "Chief spokesperson for official statistical methodology and releases."},
            ],
        }

        for role_code, req_list in role_requirements_data.items():
            job_role = role_map[role_code]
            for r_item in req_list:
                comp = competency_map[r_item["comp"]]
                lvl = level_map[r_item["lvl"]]
                stmt = select(CompetencyRequirement).where(
                    CompetencyRequirement.job_role_id == job_role.id,
                    CompetencyRequirement.competency_id == comp.id,
                )
                result = await session.execute(stmt)
                req = result.scalar_one_or_none()
                if not req:
                    req = CompetencyRequirement(
                        id=uuid.uuid4(),
                        job_role_id=job_role.id,
                        competency_id=comp.id,
                        required_level_id=lvl.id,
                        required_score=r_item["score"],
                        criticality=r_item["crit"],
                        task_relevance=r_item["rel"],
                        mission_urgency=r_item.get("urgency", "MEDIUM"),
                        priority=r_item["prio"],
                        rationale=r_item["rationale"],
                        source_reference="MoSPI_Cadre_Prototype_2026",
                    )
                    session.add(req)
                    logger.info(f"Added Requirement: {job_role.name} requires {comp.name} at Level {lvl.level_number}")
                else:
                    req.mission_urgency = r_item.get("urgency", "MEDIUM")

        # =========================================================================
        # 10. MINIMAL COURSE & TRAINING PROGRAMME MAPPINGS (Abstractions)
        # =========================================================================
        courses_data = [
            {
                "code": "IGOT-STAT-401",
                "title": "Advanced Survey Sampling & Weight Calibration",
                "provider": "iGOT Karmayogi",
                "competency_code": "STAT_SAMPLING",
                "coverage_level": "ADVANCED",
                "outcome": "Comprehensive mastery of probability sampling and survey weight derivation.",
            },
            {
                "code": "IGOT-TECH-205",
                "title": "Python for Official Data Analytics",
                "provider": "iGOT Karmayogi",
                "competency_code": "TECH_PYTHON",
                "coverage_level": "WORKING",
                "outcome": "Automate data validation and tabular cleaning pipelines using pandas and numpy.",
            },
            {
                "code": "IGOT-GOV-108",
                "title": "Official Statistical Quality Standards (NQAF)",
                "provider": "iGOT Karmayogi",
                "competency_code": "STAT_DATA_QUALITY_FRAMEWORKS",
                "coverage_level": "WORKING",
                "outcome": "Implement NQAF assurance protocols across survey releases.",
            },
        ]

        for c_data in courses_data:
            stmt = select(Course).where(Course.course_code == c_data["code"])
            result = await session.execute(stmt)
            course = result.scalar_one_or_none()
            if not course:
                course = Course(
                    id=uuid.uuid4(),
                    course_code=c_data["code"],
                    title=c_data["title"],
                    provider=c_data["provider"],
                    is_active=True,
                )
                session.add(course)
                await session.flush()
                logger.info(f"Created Minimal Course: {course.title} ({course.course_code})")

            # Map to competency
            comp = competency_map[c_data["competency_code"]]
            stmt_map = select(CourseCompetency).where(
                CourseCompetency.course_id == course.id,
                CourseCompetency.competency_id == comp.id,
            )
            res_map = await session.execute(stmt_map)
            existing_map = res_map.scalar_one_or_none()
            if not existing_map:
                c_comp = CourseCompetency(
                    id=uuid.uuid4(),
                    course_id=course.id,
                    competency_id=comp.id,
                    coverage_level=c_data["coverage_level"],
                    learning_outcome=c_data["outcome"],
                )
                session.add(c_comp)
                logger.info(f"Mapped Course {course.course_code} -> Competency {comp.code}")

        programmes_data = [
            {
                "code": "NSSTA-TPAC-2025-08",
                "title": "National Accounts & SUT Framework",
                "provider": "NSSTA",
                "competency_code": "STAT_NATIONAL_ACCOUNTS",
                "coverage_level": "WORKING",
            },
            {
                "code": "NSSTA-TECH-2025-02",
                "title": "Python & R for Large-Scale Data Analytics",
                "provider": "NSSTA",
                "competency_code": "TECH_PYTHON",
                "coverage_level": "ADVANCED",
            },
        ]

        for p_data in programmes_data:
            stmt = select(TrainingProgramme).where(TrainingProgramme.programme_code == p_data["code"])
            result = await session.execute(stmt)
            prog = result.scalar_one_or_none()
            if not prog:
                prog = TrainingProgramme(
                    id=uuid.uuid4(),
                    programme_code=p_data["code"],
                    title=p_data["title"],
                    provider=p_data["provider"],
                    is_active=True,
                )
                session.add(prog)
                await session.flush()
                logger.info(f"Created Minimal Programme: {prog.title} ({prog.programme_code})")

            comp = competency_map[p_data["competency_code"]]
            stmt_map = select(TrainingProgrammeCompetency).where(
                TrainingProgrammeCompetency.training_programme_id == prog.id,
                TrainingProgrammeCompetency.competency_id == comp.id,
            )
            res_map = await session.execute(stmt_map)
            existing_map = res_map.scalar_one_or_none()
            if not existing_map:
                p_comp = TrainingProgrammeCompetency(
                    id=uuid.uuid4(),
                    training_programme_id=prog.id,
                    competency_id=comp.id,
                    coverage_level=p_data["coverage_level"],
                )
                session.add(p_comp)
                logger.info(f"Mapped Programme {prog.programme_code} -> Competency {comp.code}")

        # =========================================================================
        # 11. STAGE 5: DIAGNOSTIC ASSESSMENT & PSYCHOMETRIC QUESTIONS
        # =========================================================================
        logger.info("Seeding Stage 5: PRAGYA Core Competency Diagnostic & Questions...")
        stmt_diag = select(Assessment).where(Assessment.title == DIAGNOSTIC_ASSESSMENT_TITLE)
        diag_res = await session.execute(stmt_diag)
        diag_assessment = diag_res.scalar_one_or_none()

        if not diag_assessment:
            diag_assessment = Assessment(
                id=uuid.uuid4(),
                title=DIAGNOSTIC_ASSESSMENT_TITLE,
                description=DIAGNOSTIC_ASSESSMENT_DESC,
                assessment_type="DIAGNOSTIC",
                status="PUBLISHED",
                duration_minutes=30,
                question_count=len(DIAGNOSTIC_QUESTIONS),
            )
            session.add(diag_assessment)
            await session.flush()
            logger.info(f"Created Assessment: {diag_assessment.title} (ID: {diag_assessment.id})")

        # Map Assessment to 8 Competencies
        for code in DIAGNOSTIC_COMPETENCY_CODES:
            comp = competency_map.get(code)
            if comp:
                stmt_ac = select(AssessmentCompetency).where(
                    AssessmentCompetency.assessment_id == diag_assessment.id,
                    AssessmentCompetency.competency_id == comp.id,
                )
                ac_exists = (await session.execute(stmt_ac)).scalar_one_or_none()
                if not ac_exists:
                    session.add(
                        AssessmentCompetency(
                            id=uuid.uuid4(),
                            assessment_id=diag_assessment.id,
                            competency_id=comp.id,
                        )
                    )

        # Seed 24 Questions
        for idx, q_data in enumerate(DIAGNOSTIC_QUESTIONS):
            comp = competency_map.get(q_data["competency_code"])
            if not comp:
                continue

            stmt_q = select(AssessmentQuestion).where(
                AssessmentQuestion.assessment_id == diag_assessment.id,
                AssessmentQuestion.order_index == idx,
            )
            q_exists = (await session.execute(stmt_q)).scalar_one_or_none()
            if not q_exists:
                question = AssessmentQuestion(
                    id=uuid.uuid4(),
                    assessment_id=diag_assessment.id,
                    competency_id=comp.id,
                    question_text=q_data["question_text"],
                    options=q_data["options"],
                    correct_option=q_data["correct_option"],
                    explanation=q_data["explanation"],
                    difficulty=q_data["difficulty"],
                    points=q_data["points"],
                    order_index=idx,
                )
                session.add(question)

        await session.flush()
        logger.info(f"Seeded {len(DIAGNOSTIC_QUESTIONS)} diagnostic questions across 8 competencies.")

        # =========================================================================
        # 12. STAGE 5: TRAINING HISTORY COMPETENCY ASSOCIATIONS
        # =========================================================================
        # Associate Ananya Sharma's training history records with competencies
        ananya_emp = employee_map.get("EMP-0001")
        if ananya_emp:
            stmt_th = select(TrainingHistory).where(TrainingHistory.employee_id == ananya_emp.id)
            th_records = (await session.execute(stmt_th)).scalars().all()

            for th in th_records:
                if "Python" in th.title and "TECH_PYTHON" in competency_map:
                    th.competency_id = competency_map["TECH_PYTHON"].id
                elif ("Sampling" in th.title or "Survey" in th.title) and "STAT_SAMPLING" in competency_map:
                    th.competency_id = competency_map["STAT_SAMPLING"].id

            await session.flush()

            # =====================================================================
            # 13. STAGE 5: INITIAL EVIDENCE & ESTIMATED COMPETENCY FOR DEMO EMPLOYEE
            # =====================================================================
            # Experience evidence for 4 core statistical/technical competencies (5 years)
            exp_comp_codes = ["STAT_SURVEY_DESIGN", "STAT_SAMPLING", "TECH_PYTHON", "STAT_DATA_QUALITY_FRAMEWORKS"]
            for c_code in exp_comp_codes:
                comp = competency_map.get(c_code)
                if not comp:
                    continue
                # Check if evidence exists
                stmt_ev = select(CompetencyEvidence).where(
                    CompetencyEvidence.employee_id == ananya_emp.id,
                    CompetencyEvidence.competency_id == comp.id,
                    CompetencyEvidence.evidence_type == "EXPERIENCE",
                )
                if not (await session.execute(stmt_ev)).scalar_one_or_none():
                    await EvidenceService.record_experience_evidence(
                        employee_id=ananya_emp.id,
                        competency_id=comp.id,
                        experience_years=ananya_emp.experience_years,
                        db=session,
                    )

            # Training evidence for Python (score: 88.0) and Sampling (score: 92.0)
            if "TECH_PYTHON" in competency_map:
                py_comp = competency_map["TECH_PYTHON"]
                stmt_tev = select(CompetencyEvidence).where(
                    CompetencyEvidence.employee_id == ananya_emp.id,
                    CompetencyEvidence.competency_id == py_comp.id,
                    CompetencyEvidence.evidence_type == "TRAINING",
                )
                if not (await session.execute(stmt_tev)).scalar_one_or_none():
                    await EvidenceService.record_training_evidence(
                        employee_id=ananya_emp.id,
                        competency_id=py_comp.id,
                        training_title="Python for Statistical Analysis & Visualization",
                        score=88.0,
                        provider="iGOT Karmayogi",
                        db=session,
                    )

            if "STAT_SAMPLING" in competency_map:
                samp_comp = competency_map["STAT_SAMPLING"]
                stmt_sev = select(CompetencyEvidence).where(
                    CompetencyEvidence.employee_id == ananya_emp.id,
                    CompetencyEvidence.competency_id == samp_comp.id,
                    CompetencyEvidence.evidence_type == "TRAINING",
                )
                if not (await session.execute(stmt_sev)).scalar_one_or_none():
                    await EvidenceService.record_training_evidence(
                        employee_id=ananya_emp.id,
                        competency_id=samp_comp.id,
                        training_title="Advanced Sampling & Survey Methodology",
                        score=92.0,
                        provider="NSSTA",
                        db=session,
                    )

            # Compute initial employee competencies for Ananya Sharma
            await CompetencyScoringService.calculate_all_employee_competencies(ananya_emp.id, session)
            logger.info("Calculated initial multi-source employee competencies for Ananya Sharma (EMP-0001).")

            # =========================================================================
            # 13. STAGE 6: INITIAL SKILL GAP ENGINE CALCULATION
            # =========================================================================
            from app.modules.skill_gaps.service import SkillGapService

            gap_service = SkillGapService(session)
            initial_gaps = await gap_service.recalculate_employee_gaps(ananya_emp.id)
            logger.info(f"Calculated {len(initial_gaps)} initial skill gaps for Ananya Sharma (EMP-0001).")

            # =========================================================================
            # 14. STAGE 7: SYNTHETIC LEARNING CATALOGUE & RECOMMENDATIONS
            # =========================================================================
            logger.info("Seeding Stage 7 synthetic learning catalogue (iGOT, NSSTA, PRAGYA)...")
            seeded_items_count = 0
            for item_data in SYNTHETIC_LEARNING_ITEMS:
                stmt_item = select(LearningItem).where(
                    LearningItem.provider == item_data["provider"],
                    LearningItem.provider_item_id == item_data["provider_item_id"],
                )
                existing_item = (await session.execute(stmt_item)).scalar_one_or_none()
                if not existing_item:
                    existing_item = LearningItem(
                        id=uuid.uuid4(),
                        provider=item_data["provider"],
                        provider_item_id=item_data["provider_item_id"],
                        title=item_data["title"],
                        description=item_data["description"],
                        type=item_data["type"],
                        difficulty=item_data["difficulty"],
                        level=item_data["level"],
                        duration_minutes=item_data["duration_minutes"],
                        language=item_data["language"],
                        format=item_data["format"],
                        url=item_data.get("url"),
                        prerequisites=item_data.get("prerequisites", []),
                        is_active=True,
                        source_mode="MOCK",
                        item_metadata=item_data.get("metadata", {}),
                    )
                    session.add(existing_item)
                    await session.flush()
                else:
                    existing_item.title = item_data["title"]
                    existing_item.description = item_data["description"]
                    existing_item.type = item_data["type"]
                    existing_item.difficulty = item_data["difficulty"]
                    existing_item.level = item_data["level"]
                    existing_item.duration_minutes = item_data["duration_minutes"]
                    existing_item.language = item_data["language"]
                    existing_item.format = item_data["format"]
                    existing_item.url = item_data.get("url")
                    existing_item.prerequisites = item_data.get("prerequisites", [])
                    existing_item.source_mode = "MOCK"
                    existing_item.item_metadata = item_data.get("metadata", {})
                    await session.flush()

                # Competency mappings
                stmt_del = select(LearningItemCompetency).where(
                    LearningItemCompetency.learning_item_id == existing_item.id
                )
                existing_maps = (await session.execute(stmt_del)).scalars().all()
                for em in existing_maps:
                    await session.delete(em)
                await session.flush()

                for comp_map in item_data.get("competencies", []):
                    code = comp_map["competency_code"]
                    if code in competency_map:
                        lic = LearningItemCompetency(
                            id=uuid.uuid4(),
                            learning_item_id=existing_item.id,
                            competency_id=competency_map[code].id,
                            coverage_level=comp_map.get("coverage_level", "WORKING"),
                            learning_outcome=comp_map.get("learning_outcome", ""),
                        )
                        session.add(lic)
                seeded_items_count += 1

            await session.flush()
            logger.info(f"Seeded/verified {seeded_items_count} Stage 7 synthetic learning items.")

            # Generate initial personalized recommendations and learning path for Ananya Sharma
            rec_service = RecommendationService(session)
            ananya_recs = await rec_service.generate_recommendations(ananya_emp.id)
            logger.info(f"Generated {len(ananya_recs)} personalized learning recommendations for Ananya Sharma (EMP-0001).")

            # Seed Stage 12 Statistical Virtual Lab Scenarios
            from app.modules.labs.seed_scenarios import seed_virtual_labs
            await seed_virtual_labs(session)

        await session.commit()
        logger.info("PRAGYA database seeding (including Stage 12 Statistical Virtual Lab) completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
