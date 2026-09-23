import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainingHistoryBase(BaseModel):
    title: str
    provider: str
    provider_type: str
    course_id: str | None = None
    programme_id: str | None = None
    completed_at: datetime | None = None
    status: str = "COMPLETED"
    score: float | None = None
    duration_hours: float | None = None
    certificate_reference: str | None = None


class TrainingHistoryResponse(TrainingHistoryBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
