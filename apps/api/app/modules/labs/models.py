import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.competencies.models import Competency
from app.modules.employees.models import Employee
from app.modules.assessments.models import CompetencyEvidence


class LabDataset(Base):
    """Synthetic dataset used within statistical virtual lab scenarios."""

    __tablename__ = "lab_datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    schema_definition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    dataset_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    scenarios: Mapped[list["LabScenario"]] = relationship(
        "LabScenario", back_populates="dataset"
    )


class LabScenario(Base):
    """Interactive statistical virtual lab scenario definition."""

    __tablename__ = "lab_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50), nullable=False, default="INTERMEDIATE"
    )  # BEGINNER, INTERMEDIATE, ADVANCED
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    learning_objectives: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    instructions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lab_datasets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), default="READY", nullable=False, index=True
    )  # DRAFT, READY, ARCHIVED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    competency = relationship("Competency")
    dataset: Mapped["LabDataset"] = relationship(
        "LabDataset", back_populates="scenarios"
    )
    sessions: Mapped[list["LabSession"]] = relationship(
        "LabSession", back_populates="scenario"
    )


class LabSession(Base):
    """Employee execution session for a virtual lab scenario."""

    __tablename__ = "lab_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lab_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="IN_PROGRESS", nullable=False, index=True
    )  # IN_PROGRESS, COMPLETED, ABANDONED
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee")
    scenario: Mapped["LabScenario"] = relationship(
        "LabScenario", back_populates="sessions"
    )
    actions: Mapped[list["LabAction"]] = relationship(
        "LabAction",
        back_populates="session",
        order_by="LabAction.step_number",
        cascade="all, delete-orphan",
    )
    result: Mapped["LabResult | None"] = relationship(
        "LabResult", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )


class LabAction(Base):
    """Discrete analytical action performed by an employee within a lab step."""

    __tablename__ = "lab_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lab_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score_awarded: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["LabSession"] = relationship("LabSession", back_populates="actions")


class LabResult(Base):
    """Permanent, verified completion record of a virtual lab simulation."""

    __tablename__ = "lab_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lab_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    competency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competency_evidence.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["LabSession"] = relationship("LabSession", back_populates="result")
    competency = relationship("Competency")
    evidence = relationship("CompetencyEvidence")
