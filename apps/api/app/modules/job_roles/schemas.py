import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobRoleBase(BaseModel):
    name: str
    code: str
    description: str | None = None
    career_level: str
    is_active: bool = True


class JobRoleResponse(JobRoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
