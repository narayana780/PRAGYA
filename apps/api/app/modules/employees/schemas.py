import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

SUPPORTED_LANGUAGES = [
    "English",
    "Hindi",
    "Bengali",
    "Marathi",
    "Telugu",
    "Tamil",
    "Gujarati",
    "Urdu",
    "Kannada",
    "Odia",
    "Malayalam",
    "Punjabi",
    "Assamese",
]


class EmployeeUpdateRequest(BaseModel):
    current_assignment: str | None = Field(None, max_length=255)
    education: str | None = Field(None, max_length=255)
    experience_years: int | None = Field(None, ge=0, le=50)
    preferred_language: str | None = Field(None, max_length=50)
    target_role_id: uuid.UUID | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None and v not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        return v


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    employee_code: str
    user_id: uuid.UUID | None = None
    full_name: str
    designation: str
    department_id: uuid.UUID
    department_name: str | None = None
    department_code: str | None = None
    job_role_id: uuid.UUID
    job_role_name: str | None = None
    job_role_code: str | None = None
    current_assignment: str | None = None
    education: str | None = None
    experience_years: int
    preferred_language: str
    target_role_id: uuid.UUID | None = None
    target_role_name: str | None = None
    profile_image_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    training_count: int | None = 0

    model_config = ConfigDict(from_attributes=True)
