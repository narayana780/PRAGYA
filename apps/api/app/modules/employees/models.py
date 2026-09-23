import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.departments.models import Department
    from app.modules.job_roles.models import JobRole
    from app.modules.training_history.models import TrainingHistory


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint(
            "experience_years >= 0 AND experience_years <= 50",
            name="chk_experience_years_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        index=True,
        nullable=False,
    )
    job_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_roles.id"),
        index=True,
        nullable=False,
    )
    current_assignment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    preferred_language: Mapped[str] = mapped_column(
        String(50),
        default="English",
        nullable=False,
    )
    target_role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_roles.id"),
        nullable=True,
    )
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="employees",
        lazy="selectin",
    )
    job_role: Mapped["JobRole"] = relationship(
        "JobRole",
        foreign_keys=[job_role_id],
        back_populates="employees",
        lazy="selectin",
    )
    target_role: Mapped[Optional["JobRole"]] = relationship(
        "JobRole",
        foreign_keys=[target_role_id],
        back_populates="target_employees",
        lazy="selectin",
    )
    training_history: Mapped[list["TrainingHistory"]] = relationship(
        "TrainingHistory",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="desc(TrainingHistory.completed_at)",
        lazy="selectin",
    )
