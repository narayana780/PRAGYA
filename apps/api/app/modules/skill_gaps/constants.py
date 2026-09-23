from dataclasses import dataclass


@dataclass(frozen=True)
class GapPriorityConfig:
    """Configurable weights for the multi-factor gap priority scoring model.

    Methodology Disclaimer:
    Gap priority values and weights are a prototype methodology and are not official MoSPI policy.
    """

    gap_magnitude_weight: float = 0.40
    criticality_weight: float = 0.25
    task_relevance_weight: float = 0.15
    mission_urgency_weight: float = 0.10
    confidence_weight: float = 0.10


DEFAULT_GAP_PRIORITY_CONFIG = GapPriorityConfig()

CRITICALITY_MAP: dict[str, float] = {
    "CRITICAL": 100.0,
    "HIGH": 75.0,
    "MEDIUM": 50.0,
    "LOW": 25.0,
}

TASK_RELEVANCE_MAP: dict[str, float] = {
    "HIGH": 100.0,
    "MEDIUM": 60.0,
    "LOW": 30.0,
}

MISSION_URGENCY_MAP: dict[str, float] = {
    "HIGH": 100.0,
    "MEDIUM": 60.0,
    "LOW": 30.0,
}


def get_confidence_flag(confidence: float) -> str:
    if confidence < 0.40:
        return "LOW_CONFIDENCE"
    elif confidence < 0.70:
        return "MEDIUM_CONFIDENCE"
    elif confidence < 0.85:
        return "HIGH_CONFIDENCE"
    else:
        return "VERY_HIGH_CONFIDENCE"


def calculate_priority_score(
    gap_score: float,
    criticality: str,
    task_relevance: str,
    mission_urgency: str,
    confidence: float,
    config: GapPriorityConfig = DEFAULT_GAP_PRIORITY_CONFIG,
) -> tuple[float, str, dict[str, float]]:
    """Calculates the multi-factor priority score (0-100) and priority level.

    Returns (priority_score, priority_level, components_breakdown).
    """
    if gap_score <= 0.0:
        return (
            0.0,
            "NO_GAP",
            {
                "gap_component": 0.0,
                "criticality_component": 0.0,
                "task_relevance_component": 0.0,
                "mission_urgency_component": 0.0,
                "confidence_component": 0.0,
            },
        )

    # 1. Gap Magnitude (0-100) -> 40%
    gap_normalized = min(max(gap_score, 0.0), 100.0)
    gap_comp = gap_normalized * config.gap_magnitude_weight

    # 2. Role Criticality -> 25%
    crit_val = CRITICALITY_MAP.get(criticality.upper(), 50.0)
    crit_comp = crit_val * config.criticality_weight

    # 3. Task Relevance -> 15%
    task_val = TASK_RELEVANCE_MAP.get(task_relevance.upper(), 60.0)
    task_comp = task_val * config.task_relevance_weight

    # 4. Mission Urgency -> 10%
    urg_val = MISSION_URGENCY_MAP.get(mission_urgency.upper(), 60.0)
    urg_comp = urg_val * config.mission_urgency_weight

    # 5. Confidence (0.0-1.0 mapped to 0-100) -> 10%
    conf_val = min(max(confidence, 0.0), 1.0) * 100.0
    conf_comp = conf_val * config.confidence_weight

    raw_score = gap_comp + crit_comp + task_comp + urg_comp + conf_comp
    final_score = round(min(max(raw_score, 0.0), 100.0), 2)

    # Threshold classification
    if final_score < 25.0:
        level = "LOW"
    elif final_score < 50.0:
        level = "MEDIUM"
    elif final_score < 75.0:
        level = "HIGH"
    else:
        level = "CRITICAL"

    breakdown = {
        "gap_component": round(gap_comp, 2),
        "criticality_component": round(crit_comp, 2),
        "task_relevance_component": round(task_comp, 2),
        "mission_urgency_component": round(urg_comp, 2),
        "confidence_component": round(conf_comp, 2),
    }

    return final_score, level, breakdown


def generate_gap_explanation(
    competency_name: str,
    role_name: str,
    current_score: float,
    required_score: float,
    gap_score: float,
    priority_level: str,
    criticality: str,
    task_relevance: str,
    mission_urgency: str,
    confidence: float,
) -> str:
    """Generates a professional, constructive, deterministic explanation of the skill gap."""
    if gap_score <= 0.0:
        return (
            f"Demonstrated {competency_name} competency ({current_score:.1f}/100) satisfies or exceeds "
            f"the required level for {role_name} ({required_score:.1f}/100). No immediate skill gap identified."
        )

    if confidence < 0.40:
        return (
            f"{competency_name} shows a potential gap of {gap_score:.1f} pts below the required proficiency for {role_name}. "
            f"Role criticality is {criticality} with {task_relevance.lower()} task relevance. "
            f"Note: Current evidence confidence is low ({confidence * 100:.0f}%); more empirical evidence is recommended "
            f"before finalizing training commitments."
        )

    return (
        f"{competency_name} is currently demonstrated at {current_score:.1f}/100, which is {gap_score:.1f} pts below "
        f"the {required_score:.1f}/100 required for {role_name}. With {criticality.lower()} role criticality, "
        f"{task_relevance.lower()} task relevance, and {mission_urgency.lower()} mission urgency, this gap is "
        f"evaluated as {priority_level} priority for capacity building."
    )
