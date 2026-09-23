import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.job_roles.models import JobRole


class CompetencyDomain(Base):
    __tablename__ = "competency_domains"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    competencies: Mapped[list["Competency"]] = relationship(
        "Competency",
        back_populates="domain",
        cascade="all, delete-orphan",
        order_by="Competency.code",
    )


class ProficiencyLevel(Base):
    __tablename__ = "proficiency_levels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    level_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    minimum_score: Mapped[int] = mapped_column(Integer, nullable=False)
    maximum_score: Mapped[int] = mapped_column(Integer, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Competency(Base):
    __tablename__ = "competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competency_domains.id"),
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    measurement_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    source_reference: Mapped[str] = mapped_column(
        String(100),
        default="SIH26101",
        nullable=False,
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
    domain: Mapped["CompetencyDomain"] = relationship(
        "CompetencyDomain",
        back_populates="competencies",
        lazy="selectin",
    )
    requirements: Mapped[list["CompetencyRequirement"]] = relationship(
        "CompetencyRequirement",
        back_populates="competency",
        cascade="all, delete-orphan",
    )
    outgoing_relationships: Mapped[list["CompetencyRelationship"]] = relationship(
        "CompetencyRelationship",
        foreign_keys="[CompetencyRelationship.source_competency_id]",
        back_populates="source_competency",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    incoming_relationships: Mapped[list["CompetencyRelationship"]] = relationship(
        "CompetencyRelationship",
        foreign_keys="[CompetencyRelationship.target_competency_id]",
        back_populates="target_competency",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class CompetencyRequirement(Base):
    __tablename__ = "competency_requirements"
    __table_args__ = (
        UniqueConstraint("job_role_id", "competency_id", name="uq_role_competency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_roles.id"),
        index=True,
        nullable=False,
    )
    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id"),
        index=True,
        nullable=False,
    )
    required_level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("proficiency_levels.id"),
        index=True,
        nullable=False,
    )
    required_score: Mapped[int] = mapped_column(Integer, nullable=False)
    criticality: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # LOW, MEDIUM, HIGH, CRITICAL
    task_relevance: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # LOW, MEDIUM, HIGH
    mission_urgency: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )  # LOW, MEDIUM, HIGH (Prototype assumption)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_reference: Mapped[str] = mapped_column(
        String(100),
        default="MoSPI_Cadre_Prototype_2026",
        nullable=False,
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
    job_role: Mapped["JobRole"] = relationship(
        "JobRole",
        lazy="selectin",
    )
    competency: Mapped["Competency"] = relationship(
        "Competency",
        back_populates="requirements",
        lazy="selectin",
    )
    required_level: Mapped["ProficiencyLevel"] = relationship(
        "ProficiencyLevel",
        lazy="selectin",
    )


class CompetencyRelationship(Base):
    __tablename__ = "competency_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id"),
        index=True,
        nullable=False,
    )
    target_competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id"),
        index=True,
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # PREREQUISITE, RELATED, ADVANCED_FROM
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    source_competency: Mapped["Competency"] = relationship(
        "Competency",
        foreign_keys=[source_competency_id],
        back_populates="outgoing_relationships",
        lazy="selectin",
    )
    target_competency: Mapped["Competency"] = relationship(
        "Competency",
        foreign_keys=[target_competency_id],
        back_populates="incoming_relationships",
        lazy="selectin",
    )


# Minimum course abstraction required for course_competencies mapping
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class CourseCompetency(Base):
    __tablename__ = "course_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
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
    )  # INTRODUCTORY, FOUNDATION, WORKING, ADVANCED
    learning_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    course: Mapped["Course"] = relationship("Course", lazy="selectin")
    competency: Mapped["Competency"] = relationship("Competency", lazy="selectin")


# Minimum training programme abstraction required for training_programme_competencies mapping
class TrainingProgramme(Base):
    __tablename__ = "training_programmes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    programme_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class TrainingProgrammeCompetency(Base):
    __tablename__ = "training_programme_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    training_programme_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_programmes.id", ondelete="CASCADE"),
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
    )  # INTRODUCTORY, FOUNDATION, WORKING, ADVANCED
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
    programme: Mapped["TrainingProgramme"] = relationship(
        "TrainingProgramme", lazy="selectin"
    )
    competency: Mapped["Competency"] = relationship("Competency", lazy="selectin")
