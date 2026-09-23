from enum import Enum


class AssessmentType(str, Enum):
    DIAGNOSTIC = "DIAGNOSTIC"
    QUIZ = "QUIZ"
    ADAPTIVE = "ADAPTIVE"
    PRACTICE = "PRACTICE"


class AssessmentStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class QuestionDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class AttemptStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class EvidenceType(str, Enum):
    DIAGNOSTIC = "DIAGNOSTIC"
    RECENT_ASSESSMENT = "RECENT_ASSESSMENT"
    TRAINING = "TRAINING"
    EXPERIENCE = "EXPERIENCE"
    SELF_ASSESSMENT = "SELF_ASSESSMENT"
    AI_GENERATED_QUIZ = "AI_GENERATED_QUIZ"
    ADAPTIVE_ASSESSMENT = "ADAPTIVE_ASSESSMENT"
    VIRTUAL_LAB = "VIRTUAL_LAB"


class ConfidenceLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


DEFAULT_EVIDENCE_WEIGHTS: dict[str, float] = {
    EvidenceType.DIAGNOSTIC.value: 0.50,
    EvidenceType.RECENT_ASSESSMENT.value: 0.20,
    EvidenceType.TRAINING.value: 0.15,
    EvidenceType.EXPERIENCE.value: 0.10,
    EvidenceType.SELF_ASSESSMENT.value: 0.05,
    EvidenceType.ADAPTIVE_ASSESSMENT.value: 0.20,
    EvidenceType.AI_GENERATED_QUIZ.value: 0.15,
    EvidenceType.VIRTUAL_LAB.value: 0.20,
}

SELF_ASSESSMENT_LEVEL_MAP: dict[int, float] = {
    1: 20.0,   # Beginner
    2: 40.0,   # Basic
    3: 60.0,   # Working
    4: 80.0,   # Proficient
    5: 100.0,  # Advanced
}


def normalize_experience(years: float) -> float:
    """Normalize years of experience into a 0-100 score.
    Prototype methodology:
    0 yr -> 0
    1 yr -> 20
    2 yrs -> 35
    3 yrs -> 45
    4 yrs -> 55
    5 yrs -> 65
    6 yrs -> 70
    7-10 yrs -> 75
    11-15 yrs -> 85
    16+ yrs -> 90
    """
    if years <= 0:
        return 0.0
    if years < 1.5:
        return 20.0
    if years < 2.5:
        return 35.0
    if years < 3.5:
        return 45.0
    if years < 4.5:
        return 55.0
    if years < 5.5:
        return 65.0
    if years < 6.5:
        return 70.0
    if years <= 10.0:
        return 75.0
    if years <= 15.0:
        return 85.0
    return 90.0


def normalize_self_assessment(level: int) -> float:
    """Map self-assessment level (1-5) to normalized score (20-100)."""
    if level not in SELF_ASSESSMENT_LEVEL_MAP:
        raise ValueError(f"Invalid self-assessment level '{level}'. Must be an integer between 1 and 5.")
    return SELF_ASSESSMENT_LEVEL_MAP[level]


def renormalize_weights(
    available_types: list[str],
    custom_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Given a list of available evidence types, renormalize weights so they sum to 1.0.
    Missing evidence sources are omitted rather than treated as zero.
    """
    weights = custom_weights or DEFAULT_EVIDENCE_WEIGHTS
    available_sum = sum(weights.get(t, 0.0) for t in available_types)
    if available_sum <= 0.0:
        return {}

    return {t: weights.get(t, 0.0) / available_sum for t in available_types}


def calculate_confidence_score(
    evidence_count: int,
    available_types: list[str],
    scores: list[float] | None = None,
) -> tuple[float, ConfidenceLabel]:
    """Calculate confidence score between 0.0 and 1.0 and its human-readable label.
    - Base confidence = (number of distinct available evidence types / 5.0)
    - Consistency modifier: slight boost if multiple sources agree closely
    Labels:
    0.00-0.39: LOW
    0.40-0.69: MEDIUM
    0.70-0.84: HIGH
    0.85-1.00: VERY_HIGH
    """
    if not available_types or evidence_count == 0:
        return 0.0, ConfidenceLabel.LOW

    # Base: proportion of evidence types present (up to 5 types)
    distinct_types = len(set(available_types))
    base = distinct_types / 5.0  # 1 type: 0.20, 2: 0.40, 3: 0.60, 4: 0.80, 5: 1.00

    # Consistency modifier
    modifier = 0.0
    if scores and len(scores) >= 2:
        variance = sum((s - (sum(scores) / len(scores))) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        if std_dev <= 10.0:
            modifier += 0.05  # high consistency bonus
        elif std_dev >= 30.0:
            modifier -= 0.05  # high disparity penalty

    # Diagnostic presence boost: objective test increases confidence
    if EvidenceType.DIAGNOSTIC.value in available_types:
        modifier += 0.05

    confidence = max(0.05, min(1.0, base + modifier))
    confidence = round(confidence, 2)

    if confidence < 0.40:
        label = ConfidenceLabel.LOW
    elif confidence < 0.70:
        label = ConfidenceLabel.MEDIUM
    elif confidence < 0.85:
        label = ConfidenceLabel.HIGH
    else:
        label = ConfidenceLabel.VERY_HIGH

    return confidence, label
