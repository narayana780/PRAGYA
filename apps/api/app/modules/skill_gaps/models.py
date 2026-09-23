import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.competencies.models import Competency, ProficiencyLevel
    from app.modules.employees.models import Employee


class SkillGap(Base):
    __tablename__ = "skill_gaps"
    __table_args__ = (
        UniqueConstraint("employee_id", "competency_id", name="uq_skill_gaps_employee_competency"),
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
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    current_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    required_score: Mapped[float] = mapped_column(Float, nullable=False)
    gap_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("proficiency_levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    required_level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("proficiency_levels.id", ondelete="RESTRICT"),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_flag: Mapped[str] = mapped_column(
        String(30),
        default="LOW_CONFIDENCE",
        nullable=False,
    )  # LOW_CONFIDENCE, MEDIUM_CONFIDENCE, HIGH_CONFIDENCE, VERY_HIGH_CONFIDENCE
    criticality: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # CRITICAL, HIGH, MEDIUM, LOW
    task_relevance: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # HIGH, MEDIUM, LOW
    mission_urgency: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # HIGH, MEDIUM, LOW
    priority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    priority_level: Mapped[str] = mapped_column(
        String(20),
        default="NO_GAP",
        nullable=False,
    )  # NO_GAP, LOW, MEDIUM, HIGH, CRITICAL
    role_relevance: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
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
    employee: Mapped["Employee"] = relationship(
        "Employee",
        lazy="selectin",
    )
    competency: Mapped["Competency"] = relationship(
        "Competency",
        lazy="selectin",
    )
    current_level: Mapped["ProficiencyLevel | None"] = relationship(
        "ProficiencyLevel",
        foreign_keys=[current_level_id],
        lazy="selectin",
    )
    required_level: Mapped["ProficiencyLevel"] = relationship(
        "ProficiencyLevel",
        foreign_keys=[required_level_id],
        lazy="selectin",
    )
