import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.competencies.models import Competency


class LearningItem(Base):
    __tablename__ = "learning_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # IGOT, NSSTA_TPAC, PRAGYA
    provider_item_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # COURSE, PROGRAMME, LAB, PATH
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)  # BEGINNER, INTERMEDIATE, ADVANCED
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 1 to 5
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="English")
    format: Mapped[str] = mapped_column(String(50), nullable=False)  # SELF_PACED, INSTRUCTOR_LED, BLENDED, INTERACTIVE_LAB
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prerequisites: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_mode: Mapped[str] = mapped_column(String(20), default="MOCK", nullable=False)  # MOCK or LIVE
    item_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    competency_mappings: Mapped[list["LearningItemCompetency"]] = relationship(
        "LearningItemCompetency",
        back_populates="learning_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LearningItemCompetency(Base):
    __tablename__ = "learning_item_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    learning_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    coverage_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="WORKING",
    )  # INTRODUCTORY, FOUNDATION, WORKING, ADVANCED
    learning_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    learning_item: Mapped["LearningItem"] = relationship(
        "LearningItem",
        back_populates="competency_mappings",
    )
    competency: Mapped["Competency"] = relationship(
        "Competency",
        lazy="selectin",
    )


class CourseProgress(Base):
    __tablename__ = "course_progress"
    __table_args__ = (
        UniqueConstraint("employee_id", "learning_item_id", name="uq_employee_course_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    learning_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="NOT_STARTED",
        nullable=False,
        index=True,
    )  # NOT_STARTED, IN_PROGRESS, COMPLETED
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    completed_modules: Mapped[list[int]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    final_assessment_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    final_assessment_passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee")
    learning_item: Mapped["LearningItem"] = relationship("LearningItem")


class CourseResourceProgress(Base):
    __tablename__ = "course_resource_progress"
    __table_args__ = (
        UniqueConstraint("employee_id", "learning_item_id", "module_id", "resource_id", name="uq_emp_course_module_res"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    learning_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    module_id: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # VIDEO, READING
    progress_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee")
    learning_item: Mapped["LearningItem"] = relationship("LearningItem")


class ModuleActivityAttempt(Base):
    __tablename__ = "module_activity_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    learning_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    module_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 for final assessment, 1-3 for modules
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # KNOWLEDGE_CHECK, ASSIGNMENT, FINAL_ASSESSMENT
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submission_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    feedback_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competency_evidence.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    employee = relationship("Employee")
    learning_item: Mapped["LearningItem"] = relationship("LearningItem")
    evidence = relationship("CompetencyEvidence")

