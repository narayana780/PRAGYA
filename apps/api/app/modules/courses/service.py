"""PRAGYA Course Domain Service
Authoritative business logic for curriculum, progress, resource tracking,
knowledge checks, assignments, final assessment, completion validation,
and competency recalibration.
"""
import copy
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.core.exceptions import PragyaException
from app.modules.assessments.constants import EvidenceType
from app.modules.assessments.models import CompetencyEvidence
from app.modules.assessments.scoring_service import CompetencyScoringService
from app.modules.courses.curriculum import get_curriculum_for_item
from app.modules.courses.models import (
    CourseProgress,
    CourseResourceProgress,
    LearningItem,
    ModuleActivityAttempt,
)
from app.modules.courses.schemas import (
    AssignmentResultResponse,
    AssignmentSubmitRequest,
    CourseCompleteResponse,
    CourseProgressResponse,
    FinalAssessmentResultResponse,
    FinalAssessmentSubmitRequest,
    KnowledgeCheckResultResponse,
    KnowledgeCheckSubmitRequest,
    ProviderSyncResponse,
    QuestionEvaluationResult,
    RecalibrateCourseResponse,
    ResourceLaunchResponse,
    ResourceProgressResponse,
    ResourceProgressUpdateRequest,
)
from app.modules.employees.models import Employee
from app.modules.labs.models import LabSession
from app.modules.training_history.models import TrainingHistory


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_learning_item_or_404(self, course_id: uuid.UUID) -> LearningItem:
        stmt = (
            select(LearningItem)
            .options(selectinload(LearningItem.competency_mappings))
            .where(LearningItem.id == course_id)
        )
        res = await self.db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise PragyaException(
                message=f"Learning item '{course_id}' not found.",
                code="COURSE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return item

    async def get_curriculum(self, course_id: uuid.UUID) -> dict[str, Any]:
        """Returns curriculum for learning item without leaking answers."""
        item = await self.get_learning_item_or_404(course_id)
        curriculum = get_curriculum_for_item(str(item.id), item.provider_item_id, item.title)
        safe_curriculum = copy.deepcopy(curriculum)

        # Sanitize knowledge checks (remove correct_index from client payload)
        for module in safe_curriculum.get("modules", []):
            kc = module.get("knowledge_check")
            if kc:
                for q in kc.get("questions", []):
                    q.pop("correct_index", None)
                    q.pop("explanation", None)

        fa = safe_curriculum.get("final_assessment")
        if fa:
            for q in fa.get("questions", []):
                q.pop("correct_index", None)
                q.pop("explanation", None)

        safe_curriculum["learning_item_id"] = str(item.id)
        safe_curriculum["provider"] = item.provider
        safe_curriculum["provider_item_id"] = item.provider_item_id
        safe_curriculum["source_mode"] = item.source_mode
        safe_curriculum["is_demo_content"] = curriculum.get("is_demo_content", True)
        safe_curriculum["learning_path_mode"] = curriculum.get("learning_path_mode", "PRAGYA Demonstration Learning Path")
        safe_curriculum["provider_label"] = curriculum.get("provider_label", "iGOT & PRAGYA")
        return safe_curriculum

    async def get_course_progress(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> CourseProgressResponse:
        """Retrieves authoritative course progress, completed modules, resource status, and unlock states."""
        item = await self.get_learning_item_or_404(course_id)

        # Verify employee
        emp = await self.db.get(Employee, employee_id)
        if not emp:
            raise PragyaException(
                message=f"Employee '{employee_id}' not found.",
                code="EMPLOYEE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Retrieve or initialize course progress
        stmt = select(CourseProgress).where(
            CourseProgress.employee_id == employee_id,
            CourseProgress.learning_item_id == course_id,
        )
        res = await self.db.execute(stmt)
        progress = res.scalar_one_or_none()

        if not progress:
            progress = CourseProgress(
                id=uuid.uuid4(),
                employee_id=employee_id,
                learning_item_id=course_id,
                status="IN_PROGRESS",
                progress_percentage=0.0,
                completed_modules=[],
                final_assessment_passed=False,
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)

        # Look up curriculum resources to enrich provider info
        curriculum = get_curriculum_for_item(str(course_id), item.provider_item_id, item.title)
        res_info_map = {}
        for mod in curriculum.get("modules", []):
            for r_def in mod.get("resources", []):
                res_info_map[r_def["id"]] = r_def

        # Fetch all resource progress records
        stmt_res = select(CourseResourceProgress).where(
            CourseResourceProgress.employee_id == employee_id,
            CourseResourceProgress.learning_item_id == course_id,
        )
        res_list = (await self.db.execute(stmt_res)).scalars().all()
        res_map = {}
        for r in res_list:
            r_info = res_info_map.get(r.resource_id, {})
            r_provider = r_info.get("provider", "PRAGYA")
            has_url = bool(r_info.get("external_url") and r_info.get("external_url").strip())
            is_igot = r_provider.upper() == "IGOT"

            if r.is_completed:
                r_status = "VERIFIED_COMPLETED"
                r_verif = "VERIFIED"
            elif is_igot:
                # Rule: For iGOT external resources, if no URL exists, status is ALWAYS NOT_CONFIGURED.
                # If URL exists: LAUNCHED if launched/progress recorded, else NOT_STARTED.
                # IN_PROGRESS is never faked without legitimate provider progress.
                if not has_url:
                    r_status = "NOT_CONFIGURED"
                    r_verif = "NOT_VERIFIED"
                elif r.progress_seconds > 0.0:
                    r_status = "LAUNCHED"
                    r_verif = "NOT_VERIFIED"
                else:
                    r_status = "NOT_STARTED"
                    r_verif = "NOT_VERIFIED"
            else:
                # PRAGYA internal resources (readings, assignments, lab)
                if r.progress_percentage > 10.0 or r.progress_seconds > 60.0:
                    r_status = "IN_PROGRESS"
                    r_verif = "PENDING"
                elif r.progress_seconds > 0.0 or r.progress_percentage > 0.0:
                    r_status = "IN_PROGRESS"
                    r_verif = "PENDING"
                else:
                    r_status = "NOT_STARTED"
                    r_verif = "NOT_VERIFIED"

            res_map[r.resource_id] = {
                "module_id": r.module_id,
                "resource_type": r.resource_type,
                "is_completed": r.is_completed,
                "progress_percentage": r.progress_percentage,
                "progress_seconds": r.progress_seconds,
                "duration_seconds": r.duration_seconds,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "status": r_status,
                "verification_status": r_verif,
                "provider": r_provider,
                "external_resource_id": r_info.get("external_resource_id"),
                "external_url": r_info.get("external_url"),
            }

        # Pre-populate any unstarted curriculum resources into res_map
        for mod in curriculum.get("modules", []):
            for r_def in mod.get("resources", []):
                r_id = r_def["id"]
                if r_id not in res_map:
                    r_prov = r_def.get("provider", "PRAGYA")
                    has_url = bool(r_def.get("external_url") and r_def.get("external_url").strip())
                    is_igot = r_prov.upper() == "IGOT"
                    init_status = ("NOT_STARTED" if has_url else "NOT_CONFIGURED") if is_igot else "NOT_STARTED"
                    res_map[r_id] = {
                        "module_id": mod["id"],
                        "resource_type": r_def.get("type", "VIDEO"),
                        "is_completed": False,
                        "progress_percentage": 0.0,
                        "progress_seconds": 0.0,
                        "duration_seconds": float(r_def.get("duration_seconds") or 0),
                        "completed_at": None,
                        "status": init_status,
                        "verification_status": "NOT_VERIFIED",
                        "provider": r_prov,
                        "external_resource_id": r_def.get("external_resource_id"),
                        "external_url": r_def.get("external_url"),
                    }

        # Check virtual lab completion (passing score >= 60.0)
        stmt_lab = select(LabSession).where(
            LabSession.employee_id == employee_id,
            LabSession.status == "COMPLETED",
        )
        lab_sessions = (await self.db.execute(stmt_lab)).scalars().all()
        matching_lab = next((s for s in lab_sessions if (s.percentage or 0.0) >= 60.0), None)
        is_lab_verified = matching_lab is not None

        # Fetch activity attempts
        stmt_act = select(ModuleActivityAttempt).where(
            ModuleActivityAttempt.employee_id == employee_id,
            ModuleActivityAttempt.learning_item_id == course_id,
        ).order_by(ModuleActivityAttempt.created_at.desc())
        attempts = (await self.db.execute(stmt_act)).scalars().all()

        act_status = {
            "m1_kc_passed": any(a.module_id == 1 and a.activity_type == "KNOWLEDGE_CHECK" and a.passed for a in attempts),
            "m2_assignment_passed": any(a.module_id == 2 and a.activity_type == "ASSIGNMENT" and a.passed for a in attempts),
            "m2_kc_passed": any(a.module_id == 2 and a.activity_type == "KNOWLEDGE_CHECK" and a.passed for a in attempts),
            "m3_kc_passed": any(a.module_id == 3 and a.activity_type == "KNOWLEDGE_CHECK" and a.passed for a in attempts),
            "m4_lab_verified": is_lab_verified,
            "final_assessment_passed": progress.final_assessment_passed,
        }

        # Validate module completion rules dynamically
        completed_mods = list(progress.completed_modules)

        # Module 1 requirements: resources completed + knowledge check passed
        m1_res_complete = (
            res_map.get("mod1-video-1", {}).get("is_completed", False)
            and res_map.get("mod1-video-2", {}).get("is_completed", False)
            and res_map.get("mod1-read-1", {}).get("is_completed", False)
            and res_map.get("mod1-read-2", {}).get("is_completed", False)
        )
        if m1_res_complete and act_status["m1_kc_passed"] and 1 not in completed_mods:
            completed_mods.append(1)

        # Module 2 requirements: resources + assignment + knowledge check
        m2_res_complete = (
            res_map.get("mod2-video-1", {}).get("is_completed", False)
            and res_map.get("mod2-read-1", {}).get("is_completed", False)
        )
        if m2_res_complete and act_status["m2_assignment_passed"] and act_status["m2_kc_passed"] and 2 not in completed_mods:
            completed_mods.append(2)

        # Module 3 requirements: readings + knowledge check
        m3_res_complete = (
            res_map.get("mod3-read-1", {}).get("is_completed", False)
            and res_map.get("mod3-read-2", {}).get("is_completed", False)
        )
        if m3_res_complete and act_status["m3_kc_passed"] and 3 not in completed_mods:
            completed_mods.append(3)

        # Module 4 requirements: Virtual Lab verified passing AND Module 3 completed
        if is_lab_verified and 3 in completed_mods and 4 not in completed_mods:
            completed_mods.append(4)

        completed_set = set(completed_mods)
        current_set = set(progress.completed_modules or [])
        if completed_set != current_set:
            progress.completed_modules = sorted(list(completed_set))
            flag_modified(progress, "completed_modules")
            # Update percentage: 4 modules + final assessment (each 20%)
            pct = len(progress.completed_modules) * 20.0 + (20.0 if progress.final_assessment_passed else 0.0)
            progress.progress_percentage = min(100.0, pct)
            if progress.progress_percentage >= 100.0 and progress.status != "COMPLETED":
                progress.status = "COMPLETED"
                progress.completed_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(progress)

        # Compute sequential unlocked modules based on authoritative completed set
        resolved_completed = set(progress.completed_modules or [])
        unlocked = [1]
        if 1 in resolved_completed:
            unlocked.append(2)
        if 2 in resolved_completed:
            unlocked.append(3)
        if 3 in resolved_completed:
            unlocked.append(4)
        if 1 in resolved_completed and 2 in resolved_completed and 3 in resolved_completed:
            unlocked.append(5)  # 5 represents Final Assessment

        return CourseProgressResponse(
            learning_item_id=str(course_id),
            employee_id=str(employee_id),
            status=progress.status,
            progress_percentage=progress.progress_percentage,
            completed_modules=progress.completed_modules,
            unlocked_modules=unlocked,
            resource_progress=res_map,
            activities_status=act_status,
            is_lab_verified=is_lab_verified,
            final_assessment_passed=progress.final_assessment_passed,
            final_assessment_score=progress.final_assessment_score,
            course_completed=progress.status == "COMPLETED",
            enrolled_at=progress.enrolled_at,
            completed_at=progress.completed_at,
        )

    async def update_resource_progress(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        resource_id: str,
        req: ResourceProgressUpdateRequest,
    ) -> ResourceProgressResponse:
        """Updates video watch progress or reading completion. Auto-completes videos at >= 90%."""
        await self.get_learning_item_or_404(course_id)

        stmt = select(CourseResourceProgress).where(
            CourseResourceProgress.employee_id == employee_id,
            CourseResourceProgress.learning_item_id == course_id,
            CourseResourceProgress.module_id == req.module_id,
            CourseResourceProgress.resource_id == resource_id,
        )
        res = await self.db.execute(stmt)
        record = res.scalar_one_or_none()

        now = datetime.now(UTC)
        if not record:
            record = CourseResourceProgress(
                id=uuid.uuid4(),
                employee_id=employee_id,
                learning_item_id=course_id,
                module_id=req.module_id,
                resource_id=resource_id,
                resource_type=req.resource_type.upper(),
                progress_seconds=req.progress_seconds,
                duration_seconds=req.duration_seconds,
                progress_percentage=req.progress_percentage,
                is_completed=False,
            )
            self.db.add(record)
        else:
            record.progress_seconds = max(record.progress_seconds, req.progress_seconds)
            record.duration_seconds = max(record.duration_seconds, req.duration_seconds)
            record.progress_percentage = max(record.progress_percentage, req.progress_percentage)

        # Completion rule: strictly >= 90% watched for video, or explicit completed flag for reading
        if req.resource_type.upper() == "VIDEO":
            if record.duration_seconds and record.duration_seconds > 0:
                calc_pct = (record.progress_seconds / record.duration_seconds) * 100.0
                record.progress_percentage = min(100.0, max(record.progress_percentage, calc_pct))
            # Strict backend threshold validation: video cannot be marked complete without >=90% watch progress
            if record.progress_percentage >= 90.0:
                if not record.is_completed:
                    record.is_completed = True
                    record.completed_at = now
        elif req.resource_type.upper() == "READING":
            if req.is_completed or record.progress_percentage >= 90.0:
                if not record.is_completed:
                    record.is_completed = True
                    record.completed_at = now

        await self.db.commit()
        await self.db.refresh(record)

        # Trigger re-check of course progress
        await self.get_course_progress(employee_id, course_id)

        return ResourceProgressResponse(
            resource_id=record.resource_id,
            module_id=record.module_id,
            resource_type=record.resource_type,
            progress_seconds=record.progress_seconds,
            duration_seconds=record.duration_seconds,
            progress_percentage=record.progress_percentage,
            is_completed=record.is_completed,
            completed_at=record.completed_at,
            status="COMPLETED" if record.is_completed else ("IN_PROGRESS" if record.progress_percentage > 10.0 else "LAUNCHED"),
            verification_status="VERIFIED" if record.is_completed else "NOT_VERIFIED",
            provider="iGOT" if "video" in record.resource_id.lower() else "PRAGYA",
        )

    async def launch_resource(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        resource_id: str,
    ) -> ResourceLaunchResponse:
        """Records learning resource launch event on external provider without fake completion."""
        item = await self.get_learning_item_or_404(course_id)
        curriculum = get_curriculum_for_item(str(course_id), item.provider_item_id, item.title)

        target_res = None
        target_mod_id = 1
        for mod in curriculum.get("modules", []):
            for r in mod.get("resources", []):
                if r["id"] == resource_id:
                    target_res = r
                    target_mod_id = mod["id"]
                    break
            if target_res:
                break

        if not target_res:
            raise PragyaException(
                message=f"Resource '{resource_id}' not found in course curriculum.",
                code="RESOURCE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        stmt = select(CourseResourceProgress).where(
            CourseResourceProgress.employee_id == employee_id,
            CourseResourceProgress.learning_item_id == course_id,
            CourseResourceProgress.resource_id == resource_id,
        )
        record = (await self.db.execute(stmt)).scalar_one_or_none()

        if not record:
            record = CourseResourceProgress(
                id=uuid.uuid4(),
                employee_id=employee_id,
                learning_item_id=course_id,
                module_id=target_mod_id,
                resource_id=resource_id,
                resource_type=target_res.get("type", "VIDEO").upper(),
                progress_seconds=1.0,
                duration_seconds=float(target_res.get("duration_seconds") or 2700),
                progress_percentage=0.0,
                is_completed=False,
            )
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
        else:
            if not record.is_completed and record.progress_seconds <= 0:
                record.progress_seconds = 1.0
                await self.db.commit()
                await self.db.refresh(record)

        # Trigger progress recalculation
        await self.get_course_progress(employee_id, course_id)

        is_done = record.is_completed
        provider = target_res.get("provider", "iGOT")
        ext_url = target_res.get("external_url")
        has_url = bool(ext_url and ext_url.strip())
        is_cfg = has_url if provider.upper() == "IGOT" else True

        return ResourceLaunchResponse(
            resource_id=resource_id,
            status="VERIFIED_COMPLETED" if is_done else ("LAUNCHED" if is_cfg else "NOT_CONFIGURED"),
            verification_status="VERIFIED" if is_done else "NOT_VERIFIED",
            provider=provider,
            external_url=ext_url,
            message=(
                f"Resource launched on {provider}. Learning takes place on official {provider} platform."
                if (not is_done and is_cfg)
                else (
                    f"Resource '{resource_id}' link not configured. Learning resource requires official URL configuration."
                    if not is_done
                    else f"Resource already completed on {provider}."
                )
            ),
        )

    async def sync_provider_resource(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        resource_id: str,
    ) -> ProviderSyncResponse:
        """Verifies learning resource completion against external provider without faking status."""
        item = await self.get_learning_item_or_404(course_id)
        curriculum = get_curriculum_for_item(str(course_id), item.provider_item_id, item.title)

        target_res = None
        target_mod_id = 1
        for mod in curriculum.get("modules", []):
            for r in mod.get("resources", []):
                if r["id"] == resource_id:
                    target_res = r
                    target_mod_id = mod["id"]
                    break
            if target_res:
                break

        if not target_res:
            raise PragyaException(
                message=f"Resource '{resource_id}' not found in course curriculum.",
                code="RESOURCE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        provider = target_res.get("provider", "iGOT")
        ext_res_id = target_res.get("external_resource_id") or resource_id

        # Check existing progress record
        stmt = select(CourseResourceProgress).where(
            CourseResourceProgress.employee_id == employee_id,
            CourseResourceProgress.learning_item_id == course_id,
            CourseResourceProgress.resource_id == resource_id,
        )
        record = (await self.db.execute(stmt)).scalar_one_or_none()
        if record and record.is_completed:
            return ProviderSyncResponse(
                resource_id=resource_id,
                provider=provider,
                verified=True,
                reason="PROVIDER_VERIFIED",
                status="COMPLETED",
                completed_at=record.completed_at,
                message="Resource completion verified.",
            )

        # Internal PRAGYA resource sync
        if provider.upper() == "PRAGYA":
            is_done = bool(record and record.is_completed)
            return ProviderSyncResponse(
                resource_id=resource_id,
                provider="PRAGYA",
                verified=is_done,
                reason="INTERNAL_RESOURCE_STATUS",
                status="COMPLETED" if is_done else "NOT_VERIFIED",
                completed_at=record.completed_at if record else None,
                message="PRAGYA internal reading status checked.",
            )

        # External iGOT resource verification
        has_live_api = bool(settings.IGOT_API_BASE_URL and settings.IGOT_CLIENT_ID)
        if has_live_api:
            # Placeholder for future live government API calls
            pass

        # Check if TrainingHistory has an authoritative record (e.g. from provider sync/batch)
        stmt_th = select(TrainingHistory).where(
            TrainingHistory.employee_id == str(employee_id),
            TrainingHistory.status == "COMPLETED",
            (TrainingHistory.course_id == ext_res_id) | (TrainingHistory.title.ilike(f"%{ext_res_id}%")),
        )
        th_record = (await self.db.execute(stmt_th)).scalars().first()

        now = datetime.now(UTC)
        if th_record:
            if not record:
                record = CourseResourceProgress(
                    id=uuid.uuid4(),
                    employee_id=employee_id,
                    learning_item_id=course_id,
                    module_id=target_mod_id,
                    resource_id=resource_id,
                    resource_type=target_res.get("type", "VIDEO").upper(),
                    progress_seconds=float(target_res.get("duration_seconds") or 2700),
                    duration_seconds=float(target_res.get("duration_seconds") or 2700),
                    progress_percentage=100.0,
                    is_completed=True,
                    completed_at=th_record.completed_at or now,
                )
                self.db.add(record)
            else:
                record.is_completed = True
                record.progress_percentage = 100.0
                record.completed_at = th_record.completed_at or now

            await self.db.commit()
            await self.db.refresh(record)
            await self.get_course_progress(employee_id, course_id)

            return ProviderSyncResponse(
                resource_id=resource_id,
                provider="iGOT",
                verified=True,
                reason="PROVIDER_VERIFIED",
                status="COMPLETED",
                completed_at=record.completed_at,
                message="Resource completion verified via iGOT provider record.",
            )

        # When live credentials are not configured and no provider completion record exists:
        return ProviderSyncResponse(
            resource_id=resource_id,
            provider="iGOT",
            verified=False,
            reason="IGOT_INTEGRATION_NOT_CONFIGURED" if not has_live_api else "NOT_COMPLETED_ON_PROVIDER",
            status="NOT_VERIFIED",
            completed_at=None,
            message=(
                "iGOT completion verification is not configured for this prototype. Official iGOT completion verification requires provider API integration."
                if not has_live_api
                else "Resource is not marked as completed on iGOT."
            ),
        )

    async def sync_provider_course(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> list[ProviderSyncResponse]:
        """Syncs all external provider resources in this course."""
        item = await self.get_learning_item_or_404(course_id)
        curriculum = get_curriculum_for_item(str(course_id), item.provider_item_id, item.title)

        results = []
        for mod in curriculum.get("modules", []):
            for r in mod.get("resources", []):
                if r.get("provider", "").upper() == "IGOT":
                    res = await self.sync_provider_resource(employee_id, course_id, r["id"])
                    results.append(res)

        return results


    async def submit_knowledge_check(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        module_id: int,
        req: KnowledgeCheckSubmitRequest,
    ) -> KnowledgeCheckResultResponse:
        """Submits and evaluates module knowledge check. Persists attempt and contributes to module completion."""
        item = await self.get_learning_item_or_404(course_id)
        curriculum = get_curriculum_for_item(str(item.id), item.provider_item_id, item.title)

        mod = next((m for m in curriculum.get("modules", []) if m["id"] == module_id), None)
        if not mod or not mod.get("knowledge_check"):
            raise PragyaException(
                message=f"No knowledge check configured for module {module_id}.",
                code="KNOWLEDGE_CHECK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        kc = mod["knowledge_check"]
        questions = kc["questions"]
        threshold = kc.get("pass_threshold_percentage", 75.0)

        correct_count = 0
        evaluations = []
        for q in questions:
            qid = q["id"]
            selected = req.answers.get(qid, -1)
            correct = q["correct_index"]
            is_correct = (selected == correct)
            if is_correct:
                correct_count += 1
            evaluations.append(
                QuestionEvaluationResult(
                    question_id=qid,
                    selected_index=selected,
                    correct_index=correct,
                    is_correct=is_correct,
                    explanation=q.get("explanation", ""),
                )
            )

        total_q = len(questions)
        pct = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0
        passed = pct >= threshold

        # Record attempt
        attempt = ModuleActivityAttempt(
            id=uuid.uuid4(),
            employee_id=employee_id,
            learning_item_id=course_id,
            module_id=module_id,
            activity_type="KNOWLEDGE_CHECK",
            score=float(correct_count),
            max_score=float(total_q),
            percentage=pct,
            passed=passed,
            submission_payload=req.answers,
            feedback_payload={"correct_count": correct_count, "total": total_q, "evaluations": [e.model_dump() for e in evaluations]},
        )
        self.db.add(attempt)
        await self.db.commit()

        # Update course progress
        prog = await self.get_course_progress(employee_id, course_id)

        return KnowledgeCheckResultResponse(
            module_id=module_id,
            total_questions=total_q,
            correct_answers=correct_count,
            score=float(correct_count),
            percentage=pct,
            passed=passed,
            pass_threshold=threshold,
            question_results=evaluations,
            module_completed=module_id in prog.completed_modules,
        )

    async def submit_assignment(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        module_id: int,
        req: AssignmentSubmitRequest,
    ) -> AssignmentResultResponse:
        """Validates Module 2 practical scenario decision, calculates score, generates CompetencyEvidence."""
        item = await self.get_learning_item_or_404(course_id)
        if module_id != 2:
            raise PragyaException(
                message="Assignments are currently defined for Module 2.",
                code="ASSIGNMENT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Rubric evaluation: 4 components, each 25 points
        rubric = {
            "sampling_method": {
                "submitted": req.sampling_method,
                "correct": "STRATIFIED_TWO_STAGE",
                "is_correct": req.sampling_method == "STRATIFIED_TWO_STAGE",
                "points": 25.0 if req.sampling_method == "STRATIFIED_TWO_STAGE" else 0.0,
                "feedback": "Correct: Two-stage sampling is required for multi-district household surveys." if req.sampling_method == "STRATIFIED_TWO_STAGE" else "Incorrect: Simple or convenience sampling violates official NSSO standards.",
            },
            "allocation_strategy": {
                "submitted": req.allocation_strategy,
                "correct": "NEYMAN_OPTIMAL",
                "is_correct": req.allocation_strategy == "NEYMAN_OPTIMAL",
                "points": 25.0 if req.allocation_strategy == "NEYMAN_OPTIMAL" else 0.0,
                "feedback": "Correct: Neyman optimal allocation minimizes sampling variance when stratum standard deviations differ." if req.allocation_strategy == "NEYMAN_OPTIMAL" else "Incorrect: Proportional or equal allocation yields higher estimator variance under heterogeneous variances.",
            },
            "non_response_buffer": {
                "submitted": req.non_response_buffer,
                "correct": "12_PERCENT",
                "is_correct": req.non_response_buffer == "12_PERCENT",
                "points": 25.0 if req.non_response_buffer == "12_PERCENT" else 0.0,
                "feedback": "Correct: A 10%-15% buffer preserves statistical power against field non-contacts." if req.non_response_buffer == "12_PERCENT" else "Incorrect: 0% buffer leads to sample shortfall; 60% excessively inflates costs.",
            },
            "justification_code": {
                "submitted": req.justification_code,
                "correct": "VARIANCE_MINIMIZATION",
                "is_correct": req.justification_code == "VARIANCE_MINIMIZATION",
                "points": 25.0 if req.justification_code == "VARIANCE_MINIMIZATION" else 0.0,
                "feedback": "Correct: Standard deviation in Coastal Stratum (18.5k) vs Inland (9.2k) justifies Neyman allocation." if req.justification_code == "VARIANCE_MINIMIZATION" else "Incorrect: Administrative ease is not an official variance minimization justification.",
            },
        }

        total_score = sum(r["points"] for r in rubric.values())
        max_score = 100.0
        pct = round((total_score / max_score) * 100.0, 1)
        passed = pct >= 75.0

        evidence_id = None
        # Generate CompetencyEvidence if passed
        comp_id = None
        if item.competency_mappings:
            comp_id = item.competency_mappings[0].competency_id

        if passed and comp_id:
            evidence = CompetencyEvidence(
                id=uuid.uuid4(),
                employee_id=employee_id,
                competency_id=comp_id,
                evidence_type=EvidenceType.RECENT_ASSESSMENT.value,
                source_id=f"course-{course_id}-mod2-assignment",
                raw_value=pct,
                normalized_score=pct / 100.0,
                weight_used=0.25,
                contribution=round((pct / 100.0) * 0.85, 3),
                confidence=0.85,
                metadata_json={
                    "course_id": str(course_id),
                    "course_title": item.title,
                    "module_id": 2,
                    "activity": "District Sampling Allocation Assignment",
                    "score": total_score,
                    "passed": passed,
                },
            )
            self.db.add(evidence)
            await self.db.flush()
            evidence_id = str(evidence.id)

        attempt = ModuleActivityAttempt(
            id=uuid.uuid4(),
            employee_id=employee_id,
            learning_item_id=course_id,
            module_id=module_id,
            activity_type="ASSIGNMENT",
            score=total_score,
            max_score=max_score,
            percentage=pct,
            passed=passed,
            submission_payload=req.model_dump(),
            feedback_payload=rubric,
            evidence_id=uuid.UUID(evidence_id) if evidence_id else None,
        )
        self.db.add(attempt)
        await self.db.commit()

        prog = await self.get_course_progress(employee_id, course_id)

        feedback_msg = (
            "Outstanding! Your sampling design satisfies MoSPI NQAF precision guidelines and minimizes estimator variance."
            if passed
            else "Needs Review: Methodological decisions do not meet minimum survey variance standards. Review Module 2 Neyman allocation notes and retry."
        )

        return AssignmentResultResponse(
            module_id=module_id,
            score=total_score,
            max_score=max_score,
            percentage=pct,
            passed=passed,
            feedback=feedback_msg,
            rubric_breakdown=rubric,
            evidence_id=evidence_id,
            module_completed=module_id in prog.completed_modules,
        )

    async def submit_final_assessment(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
        req: FinalAssessmentSubmitRequest,
    ) -> FinalAssessmentResultResponse:
        """Evaluates final comprehensive course assessment. Requires Modules 1-3 to be completed first."""
        item = await self.get_learning_item_or_404(course_id)
        prog = await self.get_course_progress(employee_id, course_id)

        # Prerequisite check: Modules 1, 2, 3 must be completed before taking final assessment
        for m in [1, 2, 3]:
            if m not in prog.completed_modules:
                raise PragyaException(
                    message=f"Cannot attempt Final Assessment: Module {m} is not yet completed. Complete Modules 1-3 first.",
                    code="PREREQUISITE_NOT_MET",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        curriculum = get_curriculum_for_item(str(item.id), item.provider_item_id, item.title)
        fa = curriculum.get("final_assessment")
        if not fa:
            raise PragyaException(
                message="No final assessment configured for this course.",
                code="FINAL_ASSESSMENT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        questions = fa["questions"]
        threshold = fa.get("pass_threshold_percentage", 70.0)

        correct_count = 0
        evaluations = []
        for q in questions:
            qid = q["id"]
            selected = req.answers.get(qid, -1)
            correct = q["correct_index"]
            is_correct = (selected == correct)
            if is_correct:
                correct_count += 1
            evaluations.append(
                QuestionEvaluationResult(
                    question_id=qid,
                    selected_index=selected,
                    correct_index=correct,
                    is_correct=is_correct,
                    explanation=q.get("explanation", ""),
                )
            )

        total_q = len(questions)
        pct = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0
        passed = pct >= threshold

        evidence_id = None
        comp_id = item.competency_mappings[0].competency_id if item.competency_mappings else None

        if passed and comp_id:
            evidence = CompetencyEvidence(
                id=uuid.uuid4(),
                employee_id=employee_id,
                competency_id=comp_id,
                evidence_type=EvidenceType.RECENT_ASSESSMENT.value,
                source_id=f"course-{course_id}-final-assessment",
                raw_value=pct,
                normalized_score=pct / 100.0,
                weight_used=0.30,
                contribution=round((pct / 100.0) * 0.90, 3),
                confidence=0.90,
                metadata_json={
                    "course_id": str(course_id),
                    "course_title": item.title,
                    "activity": "Final Course Comprehensive Assessment",
                    "score": correct_count,
                    "max_score": total_q,
                    "percentage": pct,
                    "passed": passed,
                },
            )
            self.db.add(evidence)
            await self.db.flush()
            evidence_id = str(evidence.id)

        # Record attempt
        attempt = ModuleActivityAttempt(
            id=uuid.uuid4(),
            employee_id=employee_id,
            learning_item_id=course_id,
            module_id=0,  # 0 indicates final assessment
            activity_type="FINAL_ASSESSMENT",
            score=float(correct_count),
            max_score=float(total_q),
            percentage=pct,
            passed=passed,
            submission_payload=req.answers,
            feedback_payload={"correct_count": correct_count, "total": total_q, "evaluations": [e.model_dump() for e in evaluations]},
            evidence_id=uuid.UUID(evidence_id) if evidence_id else None,
        )
        self.db.add(attempt)

        # Update CourseProgress record
        stmt_p = select(CourseProgress).where(
            CourseProgress.employee_id == employee_id,
            CourseProgress.learning_item_id == course_id,
        )
        p_res = (await self.db.execute(stmt_p)).scalar_one()
        p_res.final_assessment_score = pct
        p_res.final_assessment_passed = passed
        await self.db.commit()

        # Re-evaluate course progress
        await self.get_course_progress(employee_id, course_id)

        return FinalAssessmentResultResponse(
            total_questions=total_q,
            correct_answers=correct_count,
            score=float(correct_count),
            percentage=pct,
            passed=passed,
            pass_threshold=threshold,
            question_results=evaluations,
            evidence_id=evidence_id,
        )

    async def complete_course(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> CourseCompleteResponse:
        """
        Authoritative course completion validator.
        Requires:
        1. Modules 1, 2, and 3 completed (resources + activities).
        2. Module 4 verified with a passing LabSession (>= 60%).
        3. Final assessment passed.
        No bypass allowed.
        """
        item = await self.get_learning_item_or_404(course_id)
        prog = await self.get_course_progress(employee_id, course_id)

        missing_requirements = []
        if 1 not in prog.completed_modules:
            missing_requirements.append("Module 1 (Foundations) learning resources and knowledge check")
        if 2 not in prog.completed_modules:
            missing_requirements.append("Module 2 (Methodology) learning resources, assignment, and knowledge check")
        if 3 not in prog.completed_modules:
            missing_requirements.append("Module 3 (Standards) learning resources and knowledge check")
        if not prog.is_lab_verified:
            missing_requirements.append("Module 4 (PRAGYA Virtual Lab) practical simulation demonstration (>= 60% passing score)")
        if not prog.final_assessment_passed:
            missing_requirements.append("Final Course Comprehensive Assessment (>= 70% passing score)")

        if missing_requirements:
            raise PragyaException(
                message=f"Cannot complete course. Missing mandatory requirements: {'; '.join(missing_requirements)}.",
                code="COURSE_COMPLETION_REQUIREMENTS_NOT_MET",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        now = datetime.now(UTC)
        stmt_p = select(CourseProgress).where(
            CourseProgress.employee_id == employee_id,
            CourseProgress.learning_item_id == course_id,
        )
        record = (await self.db.execute(stmt_p)).scalar_one()
        record.status = "COMPLETED"
        record.completed_modules = [1, 2, 3, 4]
        record.progress_percentage = 100.0
        record.completed_at = now

        # Create Course Completion CompetencyEvidence
        evidence_id = None
        if item.competency_mappings:
            for cm in item.competency_mappings:
                evidence = CompetencyEvidence(
                    id=uuid.uuid4(),
                    employee_id=employee_id,
                    competency_id=cm.competency_id,
                    evidence_type=EvidenceType.TRAINING.value,
                    source_id=f"course-complete-{course_id}",
                    raw_value=100.0,
                    normalized_score=1.0,
                    weight_used=0.30,
                    contribution=0.90,
                    confidence=0.90,
                    metadata_json={
                        "course_id": str(course_id),
                        "course_title": item.title,
                        "provider": item.provider,
                        "coverage_level": cm.coverage_level,
                        "completed_at": now.isoformat(),
                    },
                )
                self.db.add(evidence)
                await self.db.flush()
                evidence_id = str(evidence.id)

                # Trigger competency calculation
                try:
                    await CompetencyScoringService.calculate_competency(
                        employee_id=employee_id,
                        competency_id=cm.competency_id,
                        db=self.db,
                        change_reason=f"Course Completion: {item.title}",
                        trigger_evidence_id=evidence.id,
                    )
                except Exception:
                    pass

        await self.db.commit()

        return CourseCompleteResponse(
            success=True,
            message=f"Congratulations! You have completed '{item.title}', passed the Virtual Lab, and demonstrated certified competency.",
            progress_percentage=100.0,
            completed_at=now,
            evidence_id=evidence_id,
        )

    async def recalibrate_course_competencies(
        self,
        employee_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> RecalibrateCourseResponse:
        """Triggers closed-loop recalibration for all competencies targeted by this course."""
        item = await self.get_learning_item_or_404(course_id)
        results = []

        if not item.competency_mappings:
            return RecalibrateCourseResponse(
                recalibrated=False,
                recalibrated_competencies=[],
                message="No competencies mapped to this course.",
            )

        for cm in item.competency_mappings:
            try:
                emp_comp = await CompetencyScoringService.calculate_competency(
                    employee_id=employee_id,
                    competency_id=cm.competency_id,
                    db=self.db,
                    change_reason=f"Learning Path Recalibration: {item.title}",
                )
                results.append({
                    "competency_id": str(cm.competency_id),
                    "competency_code": cm.competency.code if cm.competency else None,
                    "competency_name": cm.competency.name if cm.competency else None,
                    "current_score": emp_comp.current_score if emp_comp else 0.0,
                    "confidence": emp_comp.confidence if emp_comp else 0.0,
                    "confidence_label": emp_comp.confidence_label if emp_comp else "LOW",
                })
            except Exception as e:
                results.append({
                    "competency_id": str(cm.competency_id),
                    "error": str(e),
                })

        return RecalibrateCourseResponse(
            recalibrated=True,
            recalibrated_competencies=results,
            message="Competencies recalibrated successfully based on verified learning and practical evidence.",
        )
