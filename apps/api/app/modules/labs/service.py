"""
Virtual Lab Application Service
Coordinates lab lifecycle, evaluation, deterministic scoring, and evidence integration.
"""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import PragyaException
from app.modules.assessments.constants import DEFAULT_EVIDENCE_WEIGHTS, EvidenceType
from app.modules.assessments.models import CompetencyEvidence
from app.modules.assessments.scoring_service import CompetencyScoringService
from app.modules.competencies.models import Competency
from app.modules.labs.engine import LabEngine
from app.modules.labs.models import LabAction, LabDataset, LabResult, LabScenario, LabSession
from app.modules.labs.schemas import (
    LabActionEvaluationResult,
    LabActionResponse,
    LabActionSubmitRequest,
    LabCompleteResponse,
    LabDatasetDetail,
    LabHintResponse,
    LabResultDetail,
    LabScenarioDetail,
    LabScenarioSummary,
    LabSessionResponse,
)


class LabService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # Scenario Catalogue
    # -------------------------------------------------------------------------
    async def list_scenarios(
        self,
        competency_id: uuid.UUID | None = None,
        scenario_type: str | None = None,
        difficulty: str | None = None,
        status: str = "READY",
    ) -> list[LabScenarioSummary]:
        """Lists active virtual lab scenarios with optional filters."""
        stmt = (
            select(LabScenario)
            .options(selectinload(LabScenario.competency), selectinload(LabScenario.dataset))
            .where(LabScenario.status == status)
        )

        if competency_id:
            stmt = stmt.where(LabScenario.competency_id == competency_id)
        if scenario_type:
            stmt = stmt.where(LabScenario.scenario_type == scenario_type.upper())
        if difficulty:
            stmt = stmt.where(LabScenario.difficulty == difficulty.upper())

        stmt = stmt.order_by(LabScenario.created_at.desc())
        result = await self.db.execute(stmt)
        scenarios = result.scalars().all()

        summaries = []
        for s in scenarios:
            summaries.append(
                LabScenarioSummary(
                    id=s.id,
                    title=s.title,
                    description=s.description,
                    scenario_type=s.scenario_type,
                    competency_id=s.competency_id,
                    competency_name=s.competency.name if s.competency else None,
                    competency_code=s.competency.code if s.competency else None,
                    difficulty=s.difficulty,
                    estimated_minutes=s.estimated_minutes,
                    learning_objectives=s.learning_objectives,
                    status=s.status,
                    dataset_id=s.dataset_id,
                    dataset_row_count=s.dataset.row_count if s.dataset else 0,
                    is_synthetic=s.dataset.is_synthetic if s.dataset else True,
                    created_at=s.created_at,
                )
            )
        return summaries

    async def get_scenario_detail(self, scenario_id: uuid.UUID) -> LabScenarioDetail:
        """Retrieves full scenario details including instructions and synthetic dataset."""
        stmt = (
            select(LabScenario)
            .options(selectinload(LabScenario.competency), selectinload(LabScenario.dataset))
            .where(LabScenario.id == scenario_id)
        )
        result = await self.db.execute(stmt)
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise PragyaException(
                message=f"Lab scenario with ID {scenario_id} not found.",
                code="LAB_NOT_FOUND",
                status_code=404,
            )

        dataset = scenario.dataset
        dataset_detail = LabDatasetDetail(
            id=dataset.id,
            title=dataset.title,
            description=dataset.description,
            scenario_type=dataset.scenario_type,
            row_count=dataset.row_count,
            is_synthetic=dataset.is_synthetic,
            schema_definition=dataset.schema_definition,
            dataset_json=dataset.dataset_json,
        )

        return LabScenarioDetail(
            id=scenario.id,
            title=scenario.title,
            description=scenario.description,
            scenario_type=scenario.scenario_type,
            competency_id=scenario.competency_id,
            competency_name=scenario.competency.name if scenario.competency else None,
            competency_code=scenario.competency.code if scenario.competency else None,
            difficulty=scenario.difficulty,
            estimated_minutes=scenario.estimated_minutes,
            learning_objectives=scenario.learning_objectives,
            instructions=scenario.instructions,
            status=scenario.status,
            dataset_id=scenario.dataset_id,
            dataset_row_count=dataset.row_count,
            is_synthetic=dataset.is_synthetic,
            created_at=scenario.created_at,
            dataset=dataset_detail,
        )

    # -------------------------------------------------------------------------
    # Session Lifecycle
    # -------------------------------------------------------------------------
    async def start_session(
        self,
        employee_id: uuid.UUID,
        scenario_id: uuid.UUID,
    ) -> LabSessionResponse:
        """Creates a new isolated lab session for an employee."""
        # Verify scenario exists and is READY
        scenario = await self.db.get(LabScenario, scenario_id)
        if not scenario or scenario.status != "READY":
            raise PragyaException(
                message="Cannot start session. Scenario is not active or does not exist.",
                code="SCENARIO_INACTIVE",
                status_code=400,
            )

        session = LabSession(
            id=uuid.uuid4(),
            employee_id=employee_id,
            scenario_id=scenario_id,
            status="IN_PROGRESS",
            score=0.0,
            percentage=0.0,
            confidence=0.30,
        )
        self.db.add(session)
        await self.db.commit()

        return await self.get_session(employee_id, session.id)

    async def get_session(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LabSessionResponse:
        """Fetches employee session details ensuring employee isolation."""
        stmt = (
            select(LabSession)
            .options(
                selectinload(LabSession.scenario).selectinload(LabScenario.competency),
                selectinload(LabSession.actions),
            )
            .where(LabSession.id == session_id)
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise PragyaException(
                message="Lab session not found.",
                code="SESSION_NOT_FOUND",
                status_code=404,
            )

        # Enforce Employee Isolation
        if session.employee_id != employee_id:
            raise PragyaException(
                message="Unauthorized access to another employee's lab session.",
                code="ACCESS_DENIED",
                status_code=403,
            )

        total_steps = session.scenario.instructions.get("total_steps", 4)
        completed_steps = len(session.actions)
        current_step = min(total_steps, completed_steps + 1)

        actions_dto = [
            LabActionResponse(
                id=a.id,
                session_id=a.session_id,
                step_number=a.step_number,
                action_type=a.action_type,
                action_payload=a.action_payload,
                is_correct=a.is_correct,
                score_awarded=a.score_awarded,
                feedback=a.feedback,
                created_at=a.created_at,
            )
            for a in session.actions
        ]

        return LabSessionResponse(
            id=session.id,
            employee_id=session.employee_id,
            scenario_id=session.scenario_id,
            scenario_title=session.scenario.title,
            scenario_type=session.scenario.scenario_type,
            difficulty=session.scenario.difficulty,
            competency_id=session.scenario.competency_id,
            competency_name=session.scenario.competency.name if session.scenario.competency else None,
            status=session.status,
            current_step=current_step,
            total_steps=total_steps,
            score=session.score,
            percentage=session.percentage,
            confidence=session.confidence,
            started_at=session.started_at,
            completed_at=session.completed_at,
            actions=actions_dto,
        )

    async def get_employee_sessions(self, employee_id: uuid.UUID) -> list[LabSessionResponse]:
        """Returns all virtual lab sessions initiated or completed by the employee."""
        stmt = (
            select(LabSession)
            .options(
                selectinload(LabSession.scenario).selectinload(LabScenario.competency),
                selectinload(LabSession.actions),
            )
            .where(LabSession.employee_id == employee_id)
            .order_by(LabSession.created_at.desc())
        )
        res = await self.db.execute(stmt)
        sessions = res.scalars().all()
        result = []
        for session in sessions:
            total_steps = session.scenario.instructions.get("total_steps", 4) if session.scenario and session.scenario.instructions else 4
            completed_steps = len(session.actions)
            current_step = min(total_steps, completed_steps + 1)
            actions_dto = [
                LabActionResponse(
                    id=a.id,
                    session_id=a.session_id,
                    step_number=a.step_number,
                    action_type=a.action_type,
                    action_payload=a.action_payload,
                    is_correct=a.is_correct,
                    score_awarded=a.score_awarded,
                    feedback=a.feedback,
                    created_at=a.created_at,
                )
                for a in session.actions
            ]
            result.append(
                LabSessionResponse(
                    id=session.id,
                    employee_id=session.employee_id,
                    scenario_id=session.scenario_id,
                    scenario_title=session.scenario.title if session.scenario else "Virtual Lab Scenario",
                    scenario_type=session.scenario.scenario_type if session.scenario else "SIMULATION",
                    difficulty=session.scenario.difficulty if session.scenario else "BEGINNER",
                    competency_id=session.scenario.competency_id if session.scenario else None,
                    competency_name=session.scenario.competency.name if session.scenario and session.scenario.competency else None,
                    status=session.status,
                    current_step=current_step,
                    total_steps=total_steps,
                    score=session.score,
                    percentage=session.percentage,
                    confidence=session.confidence,
                    started_at=session.started_at,
                    completed_at=session.completed_at,
                    actions=actions_dto,
                )
            )
        return result

    # -------------------------------------------------------------------------
    # Action Execution & Deterministic Evaluation
    # -------------------------------------------------------------------------
    async def submit_action(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
        req: LabActionSubmitRequest,
    ) -> LabActionEvaluationResult:
        """
        Submits and evaluates an analytical action within a lab step.
        Guarantees idempotency: resubmitting an already completed step returns the existing record.
        """
        stmt = (
            select(LabSession)
            .options(
                selectinload(LabSession.scenario).selectinload(LabScenario.dataset),
                selectinload(LabSession.actions),
            )
            .where(LabSession.id == session_id)
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise PragyaException(message="Lab session not found.", code="SESSION_NOT_FOUND", status_code=404)

        if session.employee_id != employee_id:
            raise PragyaException(message="Unauthorized access to lab session.", code="ACCESS_DENIED", status_code=403)

        if session.status != "IN_PROGRESS":
            raise PragyaException(
                message=f"Cannot submit action. Session is already {session.status}.",
                code="SESSION_NOT_IN_PROGRESS",
                status_code=400,
            )

        scenario = session.scenario
        dataset = scenario.dataset
        dataset_records = dataset.dataset_json

        # Check for existing action on this step
        existing_action = next((a for a in session.actions if a.step_number == req.step_number), None)
        total_steps = session.scenario.instructions.get("total_steps", 4)

        if existing_action:
            # If payload is identical and step was already correct, return idempotent response
            if existing_action.is_correct and existing_action.action_payload == req.action_payload:
                return LabActionEvaluationResult(
                    action_id=existing_action.id,
                    session_id=session.id,
                    step_number=existing_action.step_number,
                    action_type=existing_action.action_type,
                    is_correct=existing_action.is_correct,
                    score_awarded=existing_action.score_awarded,
                    feedback=f"(Idempotent Resubmission) {existing_action.feedback}",
                    current_score=session.score or 0.0,
                    next_step=min(total_steps, req.step_number + 1),
                    is_completed=(len(session.actions) >= total_steps),
                )

            # Re-evaluate revised or re-submitted action
            try:
                is_correct, score_awarded, feedback, metrics, preview = LabEngine.evaluate_action(
                    scenario_type=scenario.scenario_type,
                    difficulty=scenario.difficulty,
                    step_number=req.step_number,
                    action_type=req.action_type,
                    payload=req.action_payload,
                    dataset_records=dataset_records,
                )
            except ValueError as val_err:
                raise PragyaException(
                    message=str(val_err),
                    code="SECURITY_SANDBOX_VIOLATION",
                    status_code=400,
                )

            # Update existing action fields
            existing_action.action_type = req.action_type
            existing_action.action_payload = req.action_payload
            existing_action.is_correct = is_correct
            existing_action.score_awarded = score_awarded
            existing_action.feedback = feedback

            # Recalculate overall session score
            session.score = round(sum(a.score_awarded for a in session.actions), 2)
            await self.db.commit()

            return LabActionEvaluationResult(
                action_id=existing_action.id,
                session_id=session.id,
                step_number=existing_action.step_number,
                action_type=existing_action.action_type,
                is_correct=existing_action.is_correct,
                score_awarded=existing_action.score_awarded,
                feedback=existing_action.feedback,
                current_score=session.score or 0.0,
                next_step=min(total_steps, req.step_number + 1),
                is_completed=(len(session.actions) >= total_steps),
                data_preview=preview,
                metrics=metrics,
            )

        # Enforce step sequence (step_number must not exceed next expected step)
        expected_step = len(session.actions) + 1
        if req.step_number > expected_step:
            raise PragyaException(
                message=f"Out of order step. Please complete step {expected_step} before step {req.step_number}.",
                code="INVALID_STEP_SEQUENCE",
                status_code=400,
            )

        # Step 4 remains locked until Steps 1–3 are completed
        if req.step_number == 4:
            completed_prior = {a.step_number for a in session.actions if a.step_number < 4}
            if len(completed_prior) < 3:
                raise PragyaException(
                    message="Step 4 is locked. Steps 1, 2, and 3 must be completed first.",
                    code="STEP_LOCKED",
                    status_code=400,
                )

        # Evaluate through deterministic LabEngine
        try:
            is_correct, score_awarded, feedback, metrics, preview = LabEngine.evaluate_action(
                scenario_type=scenario.scenario_type,
                difficulty=scenario.difficulty,
                step_number=req.step_number,
                action_type=req.action_type,
                payload=req.action_payload,
                dataset_records=dataset_records,
            )
        except ValueError as val_err:
            raise PragyaException(
                message=str(val_err),
                code="SECURITY_SANDBOX_VIOLATION",
                status_code=400,
            )

        # Persist action
        action = LabAction(
            id=uuid.uuid4(),
            session_id=session.id,
            step_number=req.step_number,
            action_type=req.action_type,
            action_payload=req.action_payload,
            is_correct=is_correct,
            score_awarded=score_awarded,
            feedback=feedback,
        )
        self.db.add(action)

        # Update session running score
        current_score = (session.score or 0.0) + score_awarded
        session.score = round(current_score, 2)
        total_steps = scenario.instructions.get("total_steps", 4)
        session.actions.append(action)

        await self.db.commit()

        is_completed = len(session.actions) >= total_steps
        next_step = min(total_steps, req.step_number + 1)

        return LabActionEvaluationResult(
            action_id=action.id,
            session_id=session.id,
            step_number=action.step_number,
            action_type=action.action_type,
            is_correct=action.is_correct,
            score_awarded=action.score_awarded,
            feedback=action.feedback,
            current_score=current_score,
            next_step=next_step,
            is_completed=is_completed,
            data_preview=preview,
            metrics=metrics,
        )

    # -------------------------------------------------------------------------
    # Session Completion & Competency Evidence Generation
    # -------------------------------------------------------------------------
    async def complete_session(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LabCompleteResponse:
        """
        Finalizes lab session, generates authoritative score, creates CompetencyEvidence,
        and triggers competency recalculation. Idempotent.
        """
        stmt = (
            select(LabSession)
            .options(
                selectinload(LabSession.scenario).selectinload(LabScenario.competency),
                selectinload(LabSession.actions),
                selectinload(LabSession.result),
            )
            .where(LabSession.id == session_id)
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise PragyaException(message="Lab session not found.", code="SESSION_NOT_FOUND", status_code=404)

        if session.employee_id != employee_id:
            raise PragyaException(message="Unauthorized access to lab session.", code="ACCESS_DENIED", status_code=403)

        # Idempotency Check: if already completed or result exists, return existing result
        res_stmt = select(LabResult).where(LabResult.session_id == session_id)
        existing_res = (await self.db.execute(res_stmt)).scalar_one_or_none()

        if session.status == "COMPLETED" or existing_res:
            res_obj = existing_res or session.result
            correct_count = sum(1 for a in session.actions if a.is_correct)
            incorrect_count = len(session.actions) - correct_count
            actions_dto = [
                LabActionResponse(
                    id=a.id,
                    session_id=a.session_id,
                    step_number=a.step_number,
                    action_type=a.action_type,
                    action_payload=a.action_payload,
                    is_correct=a.is_correct,
                    score_awarded=a.score_awarded,
                    feedback=a.feedback,
                    created_at=a.created_at,
                )
                for a in session.actions
            ]
            learning_feedback = [a.feedback for a in session.actions]
            summary_metrics = {
                "total_steps": len(session.actions),
                "correct_actions": correct_count,
                "incorrect_actions": incorrect_count,
                "passing_threshold_percentage": 60.0,
            }
            return LabCompleteResponse(
                session_id=session.id,
                scenario_id=session.scenario_id,
                scenario_title=session.scenario.title,
                scenario_type=session.scenario.scenario_type,
                difficulty=session.scenario.difficulty,
                total_score=res_obj.total_score if res_obj else (session.score or 0.0),
                percentage=res_obj.percentage if res_obj else (session.percentage or 0.0),
                passed=res_obj.passed if res_obj else ((session.percentage or 0.0) >= 60.0),
                confidence=session.confidence or 0.85,
                competency_id=res_obj.competency_id if res_obj else session.scenario.competency_id,
                competency_name=session.scenario.competency.name if session.scenario.competency else None,
                evidence_id=res_obj.evidence_id if res_obj else None,
                actions_completed=len(session.actions),
                correct_actions=correct_count,
                incorrect_actions=incorrect_count,
                actions_history=actions_dto,
                learning_feedback=learning_feedback,
                summary_metrics=summary_metrics,
                completed_at=session.completed_at or (res_obj.created_at if res_obj else datetime.now(UTC)),
                message="Lab session previously completed. Existing competency evidence returned.",
            )

        if session.status == "ABANDONED":
            raise PragyaException(
                message="Cannot complete an abandoned lab session.",
                code="SESSION_ABANDONED",
                status_code=400,
            )

        total_steps = session.scenario.instructions.get("total_steps", 4)
        if len(session.actions) < total_steps:
            raise PragyaException(
                message=f"All {total_steps} experiment steps must be completed before submitting the lab (currently completed {len(session.actions)} of {total_steps}).",
                code="INCOMPLETE_LAB_STEPS",
                status_code=400,
            )

        step4_action = next((a for a in session.actions if a.step_number == 4 and a.is_correct), None)
        if not step4_action:
            raise PragyaException(
                message="Lab completion requires Step 4 (Simulation Execution) to be successfully completed.",
                code="STEP_4_NOT_COMPLETED",
                status_code=400,
            )

        # Calculate authoritative totals
        total_score = sum(a.score_awarded for a in session.actions)
        # Maximum possible score is steps * 25.0 (or 100.0)
        max_possible = 100.0
        percentage = round(min(100.0, max(0.0, (total_score / max_possible) * 100.0)), 1)
        passed = percentage >= 60.0

        correct_count = sum(1 for a in session.actions if a.is_correct)
        confidence = LabEngine.calculate_confidence(
            completed_steps=len(session.actions),
            total_steps=total_steps,
            correct_actions=correct_count,
            total_actions=len(session.actions),
            difficulty=session.scenario.difficulty,
        )

        now = datetime.now(UTC)
        session.status = "COMPLETED"
        session.completed_at = now
        session.score = total_score
        session.percentage = percentage
        session.confidence = confidence

        evidence_id = None
        comp_id = session.scenario.competency_id

        # Generate CompetencyEvidence if passed or attempted meaningfully
        if passed and comp_id:
            normalized_score = percentage / 100.0
            evidence_weight = DEFAULT_EVIDENCE_WEIGHTS.get(EvidenceType.VIRTUAL_LAB.value, 0.20)
            evidence = CompetencyEvidence(
                id=uuid.uuid4(),
                employee_id=session.employee_id,
                competency_id=comp_id,
                evidence_type=EvidenceType.VIRTUAL_LAB.value,
                source_id=str(session.id),
                raw_value=percentage,
                normalized_score=normalized_score,
                weight_used=evidence_weight,
                contribution=round(normalized_score * confidence, 3),
                confidence=confidence,
                metadata_json={
                    "scenario_id": str(session.scenario_id),
                    "scenario_title": session.scenario.title,
                    "scenario_type": session.scenario.scenario_type,
                    "difficulty": session.scenario.difficulty,
                    "total_score": total_score,
                    "percentage": percentage,
                    "passed": passed,
                    "actions_completed": len(session.actions),
                    "methodology": "PRAGYA prototype methodology",
                },
            )
            self.db.add(evidence)
            await self.db.flush()
            evidence_id = evidence.id

            # Trigger closed-loop recalibration through existing CompetencyScoringService
            try:
                await CompetencyScoringService.calculate_competency(
                    employee_id=session.employee_id,
                    competency_id=comp_id,
                    db=self.db,
                    change_reason="Virtual Lab completion",
                    trigger_evidence_id=evidence_id,
                )
            except Exception:
                pass  # Gracefully proceed if scoring recalculation has no prior base

        # Persist LabResult record
        lab_result = LabResult(
            id=uuid.uuid4(),
            session_id=session.id,
            total_score=total_score,
            percentage=percentage,
            passed=passed,
            competency_id=comp_id,
            evidence_id=evidence_id,
        )
        self.db.add(lab_result)
        session.result = lab_result
        await self.db.commit()

        actions_dto = [
            LabActionResponse(
                id=a.id,
                session_id=a.session_id,
                step_number=a.step_number,
                action_type=a.action_type,
                action_payload=a.action_payload,
                is_correct=a.is_correct,
                score_awarded=a.score_awarded,
                feedback=a.feedback,
                created_at=a.created_at,
            )
            for a in session.actions
        ]
        incorrect_count = len(session.actions) - correct_count
        learning_feedback = [a.feedback for a in session.actions]
        summary_metrics = {
            "total_steps": len(session.actions),
            "correct_actions": correct_count,
            "incorrect_actions": incorrect_count,
            "passing_threshold_percentage": 60.0,
        }

        return LabCompleteResponse(
            session_id=session.id,
            scenario_id=session.scenario_id,
            scenario_title=session.scenario.title,
            scenario_type=session.scenario.scenario_type,
            difficulty=session.scenario.difficulty,
            total_score=total_score,
            percentage=percentage,
            passed=passed,
            confidence=confidence,
            competency_id=comp_id,
            competency_name=session.scenario.competency.name if session.scenario.competency else None,
            evidence_id=evidence_id,
            actions_completed=len(session.actions),
            correct_actions=correct_count,
            incorrect_actions=incorrect_count,
            actions_history=actions_dto,
            learning_feedback=learning_feedback,
            summary_metrics=summary_metrics,
            completed_at=now,
            message="Virtual Lab completed successfully. Verified competency evidence recorded.",
        )

    # -------------------------------------------------------------------------
    # Results & Educational Feedback
    # -------------------------------------------------------------------------
    async def get_result(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LabResultDetail:
        """Retrieves comprehensive result report with actions breakdown and educational summary."""
        stmt = (
            select(LabResult)
            .options(
                selectinload(LabResult.session).selectinload(LabSession.actions),
                selectinload(LabResult.session).selectinload(LabSession.scenario).selectinload(LabScenario.competency),
            )
            .where(LabResult.session_id == session_id)
        )
        result = await self.db.execute(stmt)
        lab_res = result.scalar_one_or_none()

        if not lab_res:
            raise PragyaException(
                message="Lab result not found. Make sure the session has been completed.",
                code="RESULT_NOT_FOUND",
                status_code=404,
            )

        session = lab_res.session
        if session.employee_id != employee_id:
            raise PragyaException(message="Unauthorized access to result report.", code="ACCESS_DENIED", status_code=403)

        scenario = session.scenario
        actions = session.actions
        correct_count = sum(1 for a in actions if a.is_correct)
        incorrect_count = len(actions) - correct_count

        actions_dto = [
            LabActionResponse(
                id=a.id,
                session_id=a.session_id,
                step_number=a.step_number,
                action_type=a.action_type,
                action_payload=a.action_payload,
                is_correct=a.is_correct,
                score_awarded=a.score_awarded,
                feedback=a.feedback,
                created_at=a.created_at,
            )
            for a in actions
        ]

        # Educational feedback highlights
        learning_feedback = [a.feedback for a in actions]
        summary_metrics = {
            "total_steps": len(actions),
            "correct_actions": correct_count,
            "incorrect_actions": incorrect_count,
            "passing_threshold_percentage": 60.0,
        }

        return LabResultDetail(
            id=lab_res.id,
            session_id=session.id,
            scenario_id=scenario.id,
            scenario_title=scenario.title,
            scenario_type=scenario.scenario_type,
            difficulty=scenario.difficulty,
            total_score=lab_res.total_score,
            percentage=lab_res.percentage,
            passed=lab_res.passed,
            confidence=session.confidence or 0.85,
            competency_id=lab_res.competency_id,
            competency_name=scenario.competency.name if scenario.competency else None,
            evidence_id=lab_res.evidence_id,
            actions_completed=len(actions),
            correct_actions=correct_count,
            incorrect_actions=incorrect_count,
            actions_history=actions_dto,
            learning_feedback=learning_feedback,
            summary_metrics=summary_metrics,
            created_at=lab_res.created_at,
        )

    # -------------------------------------------------------------------------
    # Hints & Abandonment
    # -------------------------------------------------------------------------
    async def get_hint(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
        step_number: int,
    ) -> LabHintResponse:
        """Provides deterministic educational hints for the specified step."""
        session = await self.db.get(LabSession, session_id)
        if not session:
            raise PragyaException(message="Lab session not found.", code="SESSION_NOT_FOUND", status_code=404)
        if session.employee_id != employee_id:
            raise PragyaException(message="Unauthorized access to lab session.", code="ACCESS_DENIED", status_code=403)

        scenario = await self.db.get(LabScenario, session.scenario_id)
        hint_text, guidance = LabEngine.get_hint(scenario.scenario_type, step_number)
        return LabHintResponse(
            step_number=step_number,
            hint=hint_text,
            guidance=guidance,
        )

    async def abandon_session(
        self,
        employee_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LabSessionResponse:
        """Marks a session as ABANDONED so no further actions or evidence are accepted."""
        session = await self.db.get(LabSession, session_id)
        if not session:
            raise PragyaException(message="Lab session not found.", code="SESSION_NOT_FOUND", status_code=404)
        if session.employee_id != employee_id:
            raise PragyaException(message="Unauthorized access to lab session.", code="ACCESS_DENIED", status_code=403)

        session.status = "ABANDONED"
        await self.db.commit()
        return await self.get_session(employee_id, session_id)
