import uuid
from pydantic import BaseModel, ConfigDict, Field


class EmergingSkillItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competency_id: uuid.UUID
    code: str
    name: str
    domain_id: uuid.UUID
    domain_name: str
    signal_score: float = Field(..., description="Deterministic weighted internal signal score 0.0 - 100.0")
    affected_employees: int = 0
    gap_frequency: int = 0
    recommendation_frequency: int = 0
    training_demand: int = 0
    role_coverage: int = 0
    catalogue_coverage: int = 0
    status: str = Field(
        ..., description="Classification: EMERGING, WATCH, ESTABLISHED, INSUFFICIENT_DATA"
    )
    signals: list[str] = Field(default_factory=list, description="Explainability rationale for this competency")


class EmergingSkillsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skills: list[EmergingSkillItem]
    total_analyzed: int
    emerging_count: int
    watch_count: int
    established_count: int
    insufficient_data_count: int
    methodology: str
