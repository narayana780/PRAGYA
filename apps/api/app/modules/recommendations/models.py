import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.competencies.models import Competency
from app.modules.courses.models import LearningItem
from app.modules.employees.models import Employee
from app.modules.job_roles.models import JobRole
from app.modules.skill_gaps.models import SkillGap


class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"

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
    target_competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    gap_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_gaps.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    matched_competencies: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, STARTED, COMPLETED, DISMISSED
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recommendation_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
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
    employee: Mapped["Employee"] = relationship("Employee", lazy="selectin")
    learning_item: Mapped["LearningItem"] = relationship(
        "app.modules.courses.models.LearningItem",
        lazy="selectin",
    )
    target_competency: Mapped["Competency"] = relationship("Competency", lazy="selectin")
    gap: Mapped["SkillGap"] = relationship("SkillGap", lazy="selectin")


class LearningPath(Base):
    __tablename__ = "learning_paths"

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
    target_role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", nullable=False)  # IN_PROGRESS, COMPLETED, ARCHIVED
    generated_at: Mapped[datetime] = mapped_column(
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
    employee: Mapped["Employee"] = relationship("Employee", lazy="selectin")
    target_role: Mapped["JobRole"] = relationship("JobRole", lazy="selectin")
    items: Mapped[list["LearningPathItem"]] = relationship(
        "LearningPathItem",
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="LearningPathItem.sequence_order",
        lazy="selectin",
    )


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    learning_path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    learning_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    target_competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )
    estimated_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=60)  # minutes
    status: Mapped[str] = mapped_column(String(20), default="NOT_STARTED", nullable=False)  # NOT_STARTED, IN_PROGRESS, COMPLETED, SKIPPED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    learning_path: Mapped["LearningPath"] = relationship(
        "LearningPath",
        back_populates="items",
    )
    learning_item: Mapped["LearningItem"] = relationship(
        "app.modules.courses.models.LearningItem",
        lazy="selectin",
    )
    target_competency: Mapped["Competency"] = relationship("Competency", lazy="selectin")
