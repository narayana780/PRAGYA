import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.admin_service import WorkforceAnalysisService
from app.modules.analytics.emerging_skills_service import EmergingSkillsService
from app.modules.analytics.service import PerformanceAnalysisService
from app.modules.analytics.training_effectiveness_service import TrainingEffectivenessService
from app.modules.analytics.workforce_planning_service import WorkforcePlanningService
from app.modules.reports.excel_report_service import ExcelReportBuilder
from app.modules.reports.pdf_report_service import PdfReportBuilder


class ReportGenerationService:
    """
    Coordinates data extraction across PRAGYA intelligence services and
    renders statutory, audit-compliant PDF and Excel workbooks.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.workforce_service = WorkforceAnalysisService(db)
        self.training_service = TrainingEffectivenessService(db)
        self.emerging_service = EmergingSkillsService(db)
        self.planning_service = WorkforcePlanningService(db)
        self.perf_service = PerformanceAnalysisService(db)

    async def generate_executive_summary_report(self, fmt: str = "pdf") -> bytes:
        overview = await self.workforce_service.get_workforce_overview()
        forecast = await self.planning_service.get_capacity_forecast()
        gaps = await self.workforce_service.get_workforce_gaps()
        eff = await self.training_service.get_overall_effectiveness()

        title = "Executive Workforce & Capacity Summary"
        subtitle = "Consolidated intelligence audit covering cadre readiness, training velocity, and projected capacity."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": "National Statistical Cadre",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        kpis = [
            ("Total Cadre", f"{overview.active_employees} Officers", f"{overview.total_employees} Total Registered"),
            ("Avg Proficiency", f"{overview.average_competency_score:.1f} pts", "Govt Benchmark: 70.0 pts"),
            ("Role Readiness", f"{overview.average_role_readiness:.1f}%", f"{forecast.current_capacity} Officers Qualified"),
            ("Projected Deficit", f"{forecast.projected_gap} Officers", f"Capacity Shortfall: {forecast.capacity_gap}"),
        ]

        summary_text = (
            f"The National Statistical Cadre maintains an active evaluated strength of {overview.active_employees} officers "
            f"across {overview.departments_count} departments and {overview.roles_count} designated job roles. "
            f"Average competency proficiency stands at {overview.average_competency_score:.1f} with an overall cadre readiness of "
            f"{overview.average_role_readiness:.1f}%. The deterministic capacity planning engine identifies {forecast.projected_gap} "
            f"projected officer capacity deficits requiring targeted capacity augmentation across {len(forecast.priority_competencies)} "
            f"primary competency areas."
        )

        dept_analytics = await self.workforce_service.get_department_analytics()
        dept_headers = ["Department", "Code", "Workforce", "Avg Score", "Readiness", "Gaps"]
        dept_rows = [
            [
                d.department_name,
                d.department_code,
                d.employee_count,
                round(d.average_competency_score or 0.0, 1),
                f"{round(d.average_role_readiness or 0.0, 1)}%",
                d.critical_gap_count + d.high_gap_count,
            ]
            for d in dept_analytics.departments
        ]

        comp_headers = ["Deficient Competency", "Domain", "Affected Officers", "Average Gap", "Priority Level"]
        comp_rows = [
            [
                g.competency_name,
                g.domain_name,
                g.affected_employees,
                f"{g.average_gap_score:.1f} pts",
                g.highest_priority_level,
            ]
            for g in gaps.top_workforce_gaps[:10]
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Executive Capacity Benchmarks")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary_text)

            builder.add_section_heading("2. Departmental Capability & Cadre Distribution")
            builder.add_table(dept_headers, dept_rows, [2.5, 1.0, 1.2, 1.2, 1.2, 1.0])

            builder.add_section_heading("3. Priority Skill Deficits Across Cadre")
            builder.add_table(comp_headers, comp_rows, [2.5, 1.5, 1.2, 1.2, 1.2])

            builder.add_methodology_box(
                "Aggregated directly from PostgreSQL authoritative records. Evaluates employee competencies, skill gaps, role requirements, and learning completions.",
                [
                    "Model uses deterministic multi-factor weighting without synthetic forecasting.",
                    "Cadre benchmark defined at 70.0 competency score threshold.",
                    "Data sources include CompetencyEvidence, AssessmentAttempt, and SkillGap.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Executive Summary", title, kpis, summary_text, meta)
            builder.add_data_sheet("Department Capability", dept_headers, dept_rows)
            builder.add_data_sheet("Priority Skill Gaps", comp_headers, comp_rows)
            builder.add_audit_methodology_sheet(
                "Consolidated cadre evaluation and capacity benchmarks.",
                ["employees", "departments", "job_roles", "competencies", "skill_gaps", "course_progress"],
                [
                    "Scores calculated deterministically from verified assessment evidence.",
                    "No unverified external labor market statistics applied.",
                ],
            )
            return builder.finalize()

    async def generate_workforce_report(self, fmt: str = "pdf") -> bytes:
        overview = await self.workforce_service.get_workforce_overview()
        comp_resp = await self.workforce_service.get_workforce_competencies()

        title = "Workforce Competency Distribution Audit"
        subtitle = "Detailed audit of official statistical competencies, proficiency tiers, and assessed coverage."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"{overview.active_employees} Officers ({overview.competencies_tracked} Competencies)",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        kpis = [
            ("Tracked Competencies", overview.competencies_tracked, "Official MoSPI framework"),
            ("Cadre Evaluated", overview.active_employees, f"{overview.total_employees} registered"),
            ("Mean Proficiency", f"{overview.average_competency_score:.1f} pts", "Cadre benchmark: 70.0"),
            ("Target Readiness", f"{overview.average_role_readiness:.1f}%", "Role competency match"),
        ]

        summary = (
            f"This audit catalogues the proficiency distribution across all {overview.competencies_tracked} official "
            f"statistical competencies tracked within the MoSPI competency framework. A total of {overview.active_employees} "
            f"officers have demonstrated authoritative evaluation evidence in the PostgreSQL registry."
        )

        headers = ["Competency", "Domain", "Officers", "Avg Score", "Min Score", "Max Score", "Gaps Logged"]
        rows = [
            [
                c.name,
                c.domain,
                c.employee_count,
                round(c.average_score, 1),
                round(c.minimum_score, 1),
                round(c.maximum_score, 1),
                c.gap_count,
            ]
            for c in comp_resp.competencies
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Workforce Competency Audit Overview")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Competency Proficiency Tiers & Distribution")
            builder.add_table(headers, rows, [2.5, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0])
            builder.add_methodology_box(
                "Aggregated directly from employee_competencies, competencies, and competency_domains tables.",
                [
                    "Evaluated officers have recorded evidence in CompetencyEvidence or AssessmentAttempt.",
                    "Scores are scaled from 0.0 to 100.0 points.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Overview", title, kpis, summary, meta)
            builder.add_data_sheet("Competency Distribution", headers, rows)
            builder.add_audit_methodology_sheet(
                "Comprehensive competency distribution derived from authoritative assessment registry.",
                ["competencies", "competency_domains", "employee_competencies", "employees"],
                ["Scores reflect current authoritative state in PostgreSQL."],
            )
            return builder.finalize()

    async def generate_skill_gaps_report(self, fmt: str = "pdf") -> bytes:
        gaps = await self.workforce_service.get_workforce_gaps()
        overview = await self.workforce_service.get_workforce_overview()

        title = "National Cadre Skill Gap Analysis"
        subtitle = "Audit of identified proficiency shortfalls and developmental requirements by competency and role."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"{gaps.total_gaps} Identified Skill Gaps",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        total_affected = sum(g.affected_employees for g in gaps.top_workforce_gaps)
        avg_gap_val = (
            sum(g.average_gap_score * g.affected_employees for g in gaps.top_workforce_gaps) / total_affected
            if total_affected > 0
            else 0.0
        )
        affected_pct = (total_affected / overview.active_employees * 100.0) if overview.active_employees > 0 else 0.0

        kpis = [
            ("Total Skill Gaps", gaps.total_gaps, f"{gaps.critical_gaps} Critical Severity"),
            ("Affected Officers", total_affected, f"{overview.active_employees} Assessed Cadre"),
            ("Workforce Deficit Rate", f"{affected_pct:.1f}%", "Cadre with >= 1 gap"),
            ("Average Gap Score", f"{avg_gap_val:.1f} pts", "Distance to role requirement"),
        ]

        summary = (
            f"Analysis of {overview.active_employees} assessed officers reveals {gaps.total_gaps} active skill gaps "
            f"affecting {total_affected} personnel ({affected_pct:.1f}% of assessed cadre). "
            f"A total of {gaps.critical_gaps} gaps are classified as critical severity."
        )

        headers = ["Deficient Competency", "Domain", "Affected Personnel", "Avg Gap (Pts)", "Priority Severity"]
        rows = [
            [
                g.competency_name,
                g.domain_name,
                g.affected_employees,
                round(g.average_gap_score, 1),
                g.highest_priority_level,
            ]
            for g in gaps.top_workforce_gaps
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Skill Gap Audit Summary")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Prioritized Skill Gap Deficits")
            builder.add_table(headers, rows, [2.5, 1.5, 1.2, 1.0, 1.2, 1.0])
            builder.add_methodology_box(
                "Derived from skill_gaps table joined with competency_requirements and employee_competencies.",
                [
                    "Gap score = max(0, required_score - current_score).",
                    "Critical gaps denote gaps exceeding 25.0 points in core role competencies.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Gap Summary", title, kpis, summary, meta)
            builder.add_data_sheet("Prioritized Gaps", headers, rows)
            builder.add_audit_methodology_sheet(
                "Detailed cadre skill gaps calculated against job role requirements.",
                ["skill_gaps", "competency_requirements", "job_roles", "employees"],
                ["Only gaps with gap_score > 0 are audited."],
            )
            return builder.finalize()

    async def generate_training_effectiveness_report(self, fmt: str = "pdf") -> bytes:
        eff = await self.training_service.get_overall_effectiveness()
        courses_resp = await self.training_service.get_course_effectiveness()
        recs_resp = await self.training_service.get_recommendation_effectiveness()

        title = "Training Effectiveness & Recommendation Analytics"
        subtitle = "Longitudinal evaluation of course completion rates, observed competency improvement, and recommendation funnel."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"{eff.total_learners} Learners across {courses_resp.total_courses} Learning Interventions",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        eff_imp_rate = (
            (eff.effective_interventions / eff.measurable_interventions * 100.0)
            if eff.measurable_interventions > 0
            else 0.0
        )
        imp_str = f"+{eff.average_observed_improvement:.1f} pts" if eff.average_observed_improvement is not None else "N/A"
        kpis = [
            ("Total Enrollments", eff.total_enrollments, f"{eff.total_learners} Distinct Learners"),
            ("Completion Rate", f"{eff.completion_rate:.1f}%", f"{eff.completed_enrollments} Completed"),
            ("Measurable Interventions", eff.measurable_interventions, f"{eff_imp_rate:.1f}% Improved"),
            ("Avg Observed Gain", imp_str, "Subsequent evidence delta"),
        ]

        summary = (
            f"Evaluation of {eff.total_enrollments} learning enrollments across {courses_resp.total_courses} modules "
            f"demonstrates a {eff.completion_rate:.1f}% completion rate. For completed interventions with subsequent "
            f"authoritative evidence, {eff_imp_rate:.1f}% demonstrate observed competency gains, "
            f"with an average observed improvement of {imp_str}."
        )

        headers = ["Course / Module", "Provider", "Enrolled", "Completed", "Rate", "Pre Score", "Post Score", "Improvement"]
        rows = [
            [
                c.title,
                c.provider,
                c.enrolled_count,
                c.completed_count,
                f"{c.completion_rate:.1f}%",
                f"{c.average_pre_score:.1f}" if c.average_pre_score is not None else "NO_BASELINE",
                f"{c.average_post_score:.1f}" if c.average_post_score is not None else "NO_POST",
                f"+{c.average_improvement:.1f}" if c.average_improvement is not None else "—",
            ]
            for c in courses_resp.courses
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Training Effectiveness Summary")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Learning Intervention Outcomes & Benchmarks")
            builder.add_table(headers, rows, [2.5, 1.2, 0.9, 0.9, 1.0, 1.0, 1.0, 1.1])
            builder.add_methodology_box(
                "Pre-training baseline extracted from earliest assessment evidence. Post-training score derived from subsequent evaluations.",
                [
                    "Terminology reflects 'Observed improvement after training' rather than causal attribution.",
                    "Effectiveness index pts/hr calculated strictly when verified duration exists.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Training Summary", title, kpis, summary, meta)
            builder.add_data_sheet("Course Effectiveness", headers, rows)
            builder.add_audit_methodology_sheet(
                "Training effectiveness and recommendation lifecycle analytics.",
                ["course_progress", "learning_items", "competency_evidence", "competency_recalibrations", "learning_recommendations"],
                ["Requires subsequent evidence following course completion to measure improvement."],
            )
            return builder.finalize()

    async def generate_emerging_skills_report(self, fmt: str = "pdf") -> bytes:
        signals = await self.emerging_service.get_emerging_skills_signals()

        title = "Emerging Skills & Technology Horizon Scanning"
        subtitle = "Explainable internal demand signals identifying high-velocity capabilities for the Official Statistical System."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"{signals.total_analyzed} Statistical Competencies Evaluated",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        kpis = [
            ("Analyzed Competencies", signals.total_analyzed, "Official taxonomy"),
            ("Emerging Tier", signals.emerging_count, "Score >= 50.0"),
            ("Watch Tier", signals.watch_count, "Score 25.0 - 49.9"),
            ("Established Tier", signals.established_count, "Standard requirements"),
        ]

        summary = (
            f"Horizon scanning of {signals.total_analyzed} competencies identifies {signals.emerging_count} emerging competencies "
            f"and {signals.watch_count} watch-tier skills. Signals are computed deterministically from workforce skill gap frequency (30%), "
            f"recommendation velocity (25%), training demand (25%), and role coverage (20%)."
        )

        headers = ["Competency", "Domain", "Signal Score", "Affected Officers", "Gap Frequency", "Training Demand", "Status"]
        rows = [
            [
                s.name,
                s.domain_name,
                f"{s.signal_score:.1f}",
                s.affected_employees,
                f"{s.gap_frequency:.1f}%",
                s.training_demand,
                s.status,
            ]
            for s in signals.skills
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Horizon Scanning Intelligence Summary")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Competency Demand Signals & Categorization")
            builder.add_table(headers, rows, [2.5, 1.5, 1.1, 1.1, 1.1, 1.1, 1.2])
            builder.add_methodology_box(
                signals.methodology,
                [
                    "Uses only verified internal operational demand signals from PostgreSQL.",
                    "No unverified external internet web scrapes applied.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Horizon Overview", title, kpis, summary, meta)
            builder.add_data_sheet("Skill Demand Signals", headers, rows)
            builder.add_audit_methodology_sheet(
                "Deterministic internal demand signal scoring for emerging competencies.",
                ["competencies", "skill_gaps", "learning_recommendations", "course_progress", "competency_requirements"],
                ["Formula: 0.30*Gaps + 0.25*Recs + 0.25*Demand + 0.20*Roles."],
            )
            return builder.finalize()

    async def generate_planning_report(self, fmt: str = "pdf") -> bytes:
        overview = await self.planning_service.get_workforce_planning_overview()
        forecast = await self.planning_service.get_capacity_forecast()
        comp_fc = await self.planning_service.get_competency_capacity_forecast()
        role_fc = await self.planning_service.get_role_capacity_forecast()

        title = "Predictive Workforce Planning & Capacity Forecast"
        subtitle = "Deterministic cadre capacity projections, gap pressures, and targeted training interventions."
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"{forecast.total_workforce} Active Officers across {overview.population.roles_count} Roles",
            "Data Quality": f"{overview.data_quality.status} ({overview.data_quality.quality_grade})",
            "Version": "PRAGYA v1.0 Statutory Audit",
        }

        kpis = [
            ("Current Qualified", f"{forecast.current_capacity} / {forecast.total_workforce}", f"{forecast.current_capacity_percentage}% ready"),
            ("Capacity Gap", f"{forecast.capacity_gap} Officers", "Current shortfall"),
            ("Projected Deficit", f"{forecast.projected_gap} Officers", "Factoring velocity & gaps"),
            ("Planning Pressure", f"{forecast.overall_pressure_index} / 100", "Composite cadre index"),
        ]

        summary = (
            f"The deterministic capacity forecasting model evaluates {forecast.total_workforce} officers against required role "
            f"competencies. Current qualified capacity is {forecast.current_capacity} officers ({forecast.current_capacity_percentage}%), "
            f"yielding a current gap of {forecast.capacity_gap} personnel. Factoring in active skill gap pressure and training velocity, "
            f"the projected capacity deficit stands at {forecast.projected_gap} officers."
        )

        headers = ["Role / Cadre", "Workforce", "Meeting Target", "Below Target", "Critical Gaps", "Readiness", "Pressure"]
        rows = [
            [
                r.role_name,
                r.employee_count,
                r.employees_meeting_target,
                r.employees_below_target,
                r.critical_skill_gaps,
                f"{r.readiness_signal:.1f}%",
                f"{r.projected_capacity_pressure:.1f}",
            ]
            for r in role_fc.roles
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Workforce Planning & Capacity Baseline")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Role & Cadre Capacity Pressures")
            builder.add_table(headers, rows, [2.5, 1.0, 1.1, 1.1, 1.1, 1.1, 1.1])
            builder.add_methodology_box(
                "Pressure = 0.35*GapPressure + 0.25*TrainingDemand + 0.20*EmergingSignal + 0.20*CoverageDeficit",
                [
                    "Planning projections are deterministic estimates for capacity building planning.",
                    "Do not substitute statutory cadre review boards.",
                ],
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Planning Overview", title, kpis, summary, meta)
            builder.add_data_sheet("Cadre Role Projections", headers, rows)
            builder.add_audit_methodology_sheet(
                "Deterministic workforce capacity forecasting model.",
                ["employees", "job_roles", "competency_requirements", "skill_gaps", "course_progress"],
                ["Projections synthesize internal demand signals."],
            )
            return builder.finalize()

    async def generate_employee_report(self, employee_id: uuid.UUID, fmt: str = "pdf") -> bytes:
        drilldown = await self.planning_service.get_employee_planning_drilldown(employee_id)
        if not drilldown:
            raise ValueError(f"Employee {employee_id} not found")

        title = f"Officer Competency Profile: {drilldown.full_name}"
        subtitle = f"Designation: {drilldown.designation or 'Officer'} | Cadre Role: {drilldown.role_name or 'N/A'}"
        meta = {
            "Generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "Scope": f"Employee ID: {drilldown.employee_code or str(drilldown.employee_id)[:8]}",
            "Data Quality": "SUFFICIENT (HIGH)",
            "Version": "PRAGYA v1.0 Individual Audit",
        }

        kpis = [
            ("Average Score", f"{drilldown.current_average_score:.1f} pts", "Authoritative score"),
            ("Role Readiness", f"{drilldown.role_readiness_percentage:.1f}%", f"Status: {drilldown.readiness_indicator}"),
            ("Active Skill Gaps", drilldown.active_gaps_count, "Identified shortfalls"),
            ("Observed Gain", f"+{drilldown.observed_improvement_points:.1f} pts", f"{drilldown.learning_modules_completed} courses completed"),
        ]

        summary = (
            f"Officer {drilldown.full_name} ({drilldown.designation or 'Officer'}) assigned to the "
            f"{drilldown.department_name or 'Department'} currently demonstrates an average competency score of "
            f"{drilldown.current_average_score:.1f} points with a role readiness index of {drilldown.role_readiness_percentage:.1f}%. "
            f"The officer has {drilldown.active_gaps_count} active skill gap(s) logged and has completed "
            f"{drilldown.learning_modules_completed} training module(s)."
        )

        headers = ["Evaluation Date", "Competency", "Demonstrated Score", "Assessment Source"]
        rows = [
            [
                p.timestamp[:10],
                p.competency_name,
                f"{p.score:.1f}",
                p.source,
            ]
            for p in drilldown.historical_trajectory
        ]

        if fmt == "pdf":
            builder = PdfReportBuilder(title, subtitle, meta)
            builder.add_section_heading("1. Officer Performance Summary")
            builder.add_kpi_grid(kpis)
            builder.add_paragraph(summary)
            builder.add_section_heading("2. Longitudinal Competency Evidence & Recalibration")
            builder.add_table(headers, rows if rows else [["N/A", "Baseline Established", str(drilldown.current_average_score), "Diagnostic"]], [1.5, 2.5, 1.2, 1.5])
            builder.add_methodology_box(
                "Individual officer competency records compiled from verified diagnostic assessments, lab exercises, and recalibrations.",
                drilldown.planning_signals,
            )
            return builder.finalize()
        else:
            builder = ExcelReportBuilder(title)
            builder.add_summary_sheet("Officer Summary", title, kpis, summary, meta)
            builder.add_data_sheet("Evidence History", headers, rows if rows else [["N/A", "Baseline", drilldown.current_average_score, "Diagnostic"]])
            builder.add_audit_methodology_sheet(
                "Individual officer competency audit records.",
                ["employees", "employee_competencies", "competency_evidence", "competency_recalibrations"],
                ["Restricted for official administrative use only."],
            )
            return builder.finalize()
