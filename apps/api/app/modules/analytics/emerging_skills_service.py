import uuid
from collections import defaultdict
from typing import Any

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.analytics.emerging_skills_schemas import (
    EmergingSkillItem,
    EmergingSkillsResponse,
)
from app.modules.competencies.models import (
    Competency,
    CompetencyDomain,
    CompetencyRequirement,
)
from app.modules.courses.models import (
    CourseProgress,
    LearningItem,
    LearningItemCompetency,
)
from app.modules.recommendations.models import LearningRecommendation
from app.modules.skill_gaps.models import SkillGap


class EmergingSkillsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_emerging_skills_signals(
        self, domain_id: uuid.UUID | None = None
    ) -> EmergingSkillsResponse:
        """
        Calculates explainable, deterministic emerging skill signals derived
        strictly from real internal MoSPI / PRAGYA workforce records.

        Methodology:
        - Gap Frequency (30%): Number of officers showing demonstrated capability deficits.
        - Recommendation Velocity (25%): AI recommendations issued prioritizing this competency.
        - Training Demand (25%): Active officers enrolled in mapped learning programmes.
        - Cadre Role Mandate (20%): Official statistical job roles specifying requirement.
        """
        # 1. Load active competencies with domains
        stmt_comp = (
            select(Competency)
            .options(selectinload(Competency.domain))
            .where(Competency.is_active.is_(True))
        )
        if domain_id is not None:
            stmt_comp = stmt_comp.where(Competency.domain_id == domain_id)

        stmt_comp = stmt_comp.order_by(Competency.name.asc())
        res_comp = await self.db.execute(stmt_comp)
        competencies = list(res_comp.scalars().all())

        if not competencies:
            return EmergingSkillsResponse(
                skills=[],
                total_analyzed=0,
                emerging_count=0,
                watch_count=0,
                established_count=0,
                insufficient_data_count=0,
                methodology=(
                    "Deterministic internal demand signal modeling based on workforce gaps (30%), "
                    "recommendations (25%), training demand (25%), and cadre role coverage (20%)."
                ),
            )

        # 2. Skill Gap Signals
        stmt_gaps = (
            select(
                SkillGap.competency_id,
                func.count(distinct(SkillGap.employee_id)).label("gap_count"),
                func.count(case((SkillGap.priority_level == "CRITICAL", 1))).label("crit_count"),
            )
            .where(SkillGap.gap_score > 0)
            .group_by(SkillGap.competency_id)
        )
        res_gaps = await self.db.execute(stmt_gaps)
        gap_map: dict[uuid.UUID, int] = {}
        crit_map: dict[uuid.UUID, int] = {}
        for row in res_gaps.all():
            gap_map[row.competency_id] = row.gap_count or 0
            crit_map[row.competency_id] = row.crit_count or 0

        # 3. Recommendation Signals
        stmt_recs = (
            select(
                LearningRecommendation.target_competency_id,
                func.count(LearningRecommendation.id).label("rec_count"),
            )
            .group_by(LearningRecommendation.target_competency_id)
        )
        res_recs = await self.db.execute(stmt_recs)
        rec_map: dict[uuid.UUID, int] = {
            row.target_competency_id: row.rec_count or 0 for row in res_recs.all()
        }

        # 4. Training Demand Signals (CourseProgress mapped to competency)
        stmt_demand = (
            select(
                LearningItemCompetency.competency_id,
                func.count(distinct(CourseProgress.employee_id)).label("demand_count"),
            )
            .join(
                CourseProgress,
                LearningItemCompetency.learning_item_id == CourseProgress.learning_item_id,
            )
            .group_by(LearningItemCompetency.competency_id)
        )
        res_demand = await self.db.execute(stmt_demand)
        demand_map: dict[uuid.UUID, int] = {
            row.competency_id: row.demand_count or 0 for row in res_demand.all()
        }

        # 5. Role Requirement Mandate Signals
        stmt_roles = (
            select(
                CompetencyRequirement.competency_id,
                func.count(distinct(CompetencyRequirement.job_role_id)).label("role_count"),
            )
            .group_by(CompetencyRequirement.competency_id)
        )
        res_roles = await self.db.execute(stmt_roles)
        role_map: dict[uuid.UUID, int] = {
            row.competency_id: row.role_count or 0 for row in res_roles.all()
        }

        # 6. Learning Catalogue Coverage
        stmt_cat = (
            select(
                LearningItemCompetency.competency_id,
                func.count(distinct(LearningItemCompetency.learning_item_id)).label("cat_count"),
            )
            .group_by(LearningItemCompetency.competency_id)
        )
        res_cat = await self.db.execute(stmt_cat)
        cat_map: dict[uuid.UUID, int] = {
            row.competency_id: row.cat_count or 0 for row in res_cat.all()
        }

        # Find maximum observed counts across all competencies for normalization
        max_gap = max(gap_map.values()) if gap_map else 0
        max_rec = max(rec_map.values()) if rec_map else 0
        max_demand = max(demand_map.values()) if demand_map else 0
        max_role = max(role_map.values()) if role_map else 0

        skills: list[EmergingSkillItem] = []
        emerging_cnt = 0
        watch_cnt = 0
        established_cnt = 0
        insufficient_cnt = 0

        for comp in competencies:
            gap_cnt = gap_map.get(comp.id, 0)
            crit_cnt = crit_map.get(comp.id, 0)
            rec_cnt = rec_map.get(comp.id, 0)
            train_cnt = demand_map.get(comp.id, 0)
            roles_cnt = role_map.get(comp.id, 0)
            cat_cnt = cat_map.get(comp.id, 0)

            total_raw_signals = gap_cnt + rec_cnt + train_cnt + roles_cnt

            if total_raw_signals == 0:
                score = 0.0
                status = "INSUFFICIENT_DATA"
                signals = ["Insufficient internal workforce signal data recorded"]
                insufficient_cnt += 1
            else:
                # Deterministic normalized component scores (0 to 100 scale)
                s_gap = (gap_cnt / max_gap * 100.0) if max_gap > 0 else 0.0
                s_rec = (rec_cnt / max_rec * 100.0) if max_rec > 0 else 0.0
                s_demand = (train_cnt / max_demand * 100.0) if max_demand > 0 else 0.0
                s_role = (roles_cnt / max_role * 100.0) if max_role > 0 else 0.0

                # Weighted sum: 30% Gap, 25% Rec, 25% Demand, 20% Role
                raw_score = (0.30 * s_gap) + (0.25 * s_rec) + (0.25 * s_demand) + (0.20 * s_role)
                score = round(min(100.0, max(0.0, raw_score)), 1)

                # Classification
                if s_role >= 50.0 and s_gap < 30.0:
                    status = "ESTABLISHED"
                    established_cnt += 1
                elif score >= 60.0:
                    status = "EMERGING"
                    emerging_cnt += 1
                elif score >= 35.0:
                    status = "WATCH"
                    watch_cnt += 1
                else:
                    if gap_cnt > 0 or train_cnt > 0:
                        status = "WATCH"
                        watch_cnt += 1
                    else:
                        status = "INSUFFICIENT_DATA"
                        insufficient_cnt += 1

                # Explainability rationale
                signals = []
                if gap_cnt > 0:
                    crit_str = f" ({crit_cnt} critical)" if crit_cnt > 0 else ""
                    signals.append(f"Workforce gap frequency: {gap_cnt} personnel deficient{crit_str}")
                if rec_cnt > 0:
                    signals.append(f"Active recommendation velocity: {rec_cnt} recommendations generated")
                if train_cnt > 0:
                    signals.append(f"Demonstrated training demand: {train_cnt} active course enrollments")
                if roles_cnt > 0:
                    signals.append(f"Cadre mandate: Required across {roles_cnt} official statistical roles")
                if cat_cnt == 0:
                    signals.append("Curriculum gap: 0 courses currently in catalogue for this competency")
                else:
                    signals.append(f"Catalogue support: {cat_cnt} active learning items available")

            skills.append(
                EmergingSkillItem(
                    competency_id=comp.id,
                    code=comp.code,
                    name=comp.name,
                    domain_id=comp.domain_id,
                    domain_name=comp.domain.name if comp.domain else "Statistical Framework",
                    signal_score=score,
                    affected_employees=gap_cnt,
                    gap_frequency=gap_cnt,
                    recommendation_frequency=rec_cnt,
                    training_demand=train_cnt,
                    role_coverage=roles_cnt,
                    catalogue_coverage=cat_cnt,
                    status=status,
                    signals=signals,
                )
            )

        # Deterministic sorting: signal_score desc, gap_frequency desc, name asc
        skills.sort(
            key=lambda x: (
                -x.signal_score,
                -x.gap_frequency,
                x.name,
            )
        )

        return EmergingSkillsResponse(
            skills=skills,
            total_analyzed=len(skills),
            emerging_count=emerging_cnt,
            watch_count=watch_cnt,
            established_count=established_cnt,
            insufficient_data_count=insufficient_cnt,
            methodology=(
                "Deterministic internal demand signal modeling based on workforce gaps (30%), "
                "recommendations (25%), training demand (25%), and cadre role coverage (20%)."
            ),
        )
