from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecommendationConfig:
    WEIGHT_GAP_PRIORITY: float = 0.35
    WEIGHT_SEMANTIC_MATCH: float = 0.25
    WEIGHT_LEVEL_FIT: float = 0.15
    WEIGHT_OUTCOME_COVERAGE: float = 0.10
    WEIGHT_PREREQUISITE_FIT: float = 0.05
    WEIGHT_DURATION_FIT: float = 0.05
    WEIGHT_NOVELTY: float = 0.05

    # Thresholds for eligible gaps
    ELIGIBLE_PRIORITY_LEVELS: tuple[str, ...] = ("CRITICAL", "HIGH", "MEDIUM")


DEFAULT_RECOMMENDATION_CONFIG = RecommendationConfig()


def calculate_level_fit(
    item_level: int,
    emp_level: int,
    required_level: int,
) -> float:
    """Calculates how well a learning item's proficiency level matches employee progression.
    Returns score from 0.0 to 100.0.
    """
    # If employee is completely unassessed (level 0), level 1 or 2 is optimal
    if emp_level <= 0:
        if item_level == 1:
            return 100.0
        elif item_level == 2:
            return 85.0
        elif item_level == 3:
            return 60.0
        else:
            return 30.0

    diff = item_level - emp_level

    # Optimal progression: course is exactly 1 level higher than demonstrated
    if diff == 1:
        return 100.0
    # Consolidating current level
    elif diff == 0:
        return 85.0
    # Reaching required level in 2 steps
    elif diff == 2 and item_level <= required_level:
        return 75.0
    # Too advanced
    elif diff > 2:
        return max(20.0, 100.0 - (diff * 25.0))
    # Below current demonstrated level (too basic)
    else:
        abs_diff = abs(diff)
        return max(25.0, 100.0 - (abs_diff * 35.0))


def calculate_outcome_coverage(coverage_level: str | None) -> float:
    """Evaluates the depth of competency coverage provided by the learning item."""
    norm = (coverage_level or "").upper()
    if norm == "ADVANCED":
        return 100.0
    elif norm == "WORKING":
        return 90.0
    elif norm == "FOUNDATION":
        return 75.0
    elif norm == "INTRODUCTORY":
        return 60.0
    return 70.0


def calculate_prerequisite_fit(
    prerequisites: list[dict[str, Any]] | None,
    emp_competency_scores: dict[str, float],
) -> float:
    """Checks whether the employee meets stated prerequisites.
    Returns score from 0.0 to 100.0.
    """
    if not prerequisites:
        return 100.0

    met_count = 0
    total_count = len(prerequisites)

    for prereq in prerequisites:
        comp_code = prereq.get("competency_code")
        min_score = prereq.get("min_score", 40.0)
        current_score = emp_competency_scores.get(comp_code, 0.0) if comp_code else 0.0

        if current_score >= min_score:
            met_count += 1

    if total_count == 0:
        return 100.0

    ratio = met_count / total_count
    if ratio == 1.0:
        return 100.0
    elif ratio >= 0.5:
        return 60.0
    else:
        return 25.0


def calculate_duration_fit(duration_minutes: int) -> float:
    """Scores suitability of course length for continuing education.
    Returns score from 0.0 to 100.0.
    """
    # 30 min to 3 hours: optimal micro-learning / short modular format
    if 30 <= duration_minutes <= 180:
        return 100.0
    # 3 to 8 hours: standard full-day or self-paced course
    elif 180 < duration_minutes <= 480:
        return 90.0
    # 8 to 24 hours: multi-day intensive programme
    elif 480 < duration_minutes <= 1440:
        return 80.0
    # Quick module under 30 mins
    elif duration_minutes < 30:
        return 85.0
    # Extended programme > 24 hours
    else:
        return 65.0


def calculate_novelty_score(
    is_completed: bool,
    is_in_progress: bool = False,
) -> float:
    """Scores content novelty: completed content receives strong negative signal."""
    if is_completed:
        return 0.0
    if is_in_progress:
        return 40.0
    return 100.0


def calculate_recommendation_score(
    gap_priority_score: float,
    semantic_match_score: float,
    level_fit_score: float,
    outcome_coverage_score: float,
    prerequisite_fit_score: float,
    duration_fit_score: float,
    novelty_score: float,
    config: RecommendationConfig = DEFAULT_RECOMMENDATION_CONFIG,
) -> tuple[float, dict[str, float]]:
    """Computes total deterministic recommendation score (0.0 to 100.0) and factor breakdown."""
    gap_comp = round(gap_priority_score * config.WEIGHT_GAP_PRIORITY, 2)
    semantic_comp = round(semantic_match_score * config.WEIGHT_SEMANTIC_MATCH, 2)
    level_comp = round(level_fit_score * config.WEIGHT_LEVEL_FIT, 2)
    outcome_comp = round(outcome_coverage_score * config.WEIGHT_OUTCOME_COVERAGE, 2)
    prereq_comp = round(prerequisite_fit_score * config.WEIGHT_PREREQUISITE_FIT, 2)
    duration_comp = round(duration_fit_score * config.WEIGHT_DURATION_FIT, 2)
    novelty_comp = round(novelty_score * config.WEIGHT_NOVELTY, 2)

    total_score = min(
        round(
            gap_comp
            + semantic_comp
            + level_comp
            + outcome_comp
            + prereq_comp
            + duration_comp
            + novelty_comp,
            2,
        ),
        100.0,
    )

    breakdown = {
        "gap_priority_component": gap_comp,
        "semantic_match_component": semantic_comp,
        "level_fit_component": level_comp,
        "outcome_coverage_component": outcome_comp,
        "prerequisite_fit_component": prereq_comp,
        "duration_fit_component": duration_comp,
        "novelty_component": novelty_comp,
    }

    return total_score, breakdown


def generate_recommendation_reason(
    competency_name: str,
    priority_level: str,
    gap_score: float,
    current_score: float,
    required_score: float,
    role_name: str,
    item_title: str,
    item_provider: str,
    coverage_level: str,
    level_fit_score: float,
    is_completed: bool,
) -> dict[str, str]:
    """Generates deterministic structured explanation model for why this course is recommended."""
    gap_reason = (
        f"{competency_name} is an active {priority_level}-priority skill gap "
        f"with a deficit of {gap_score:.1f} pts (current: {current_score:.1f}/100, required: {required_score:.1f}/100)."
    )

    role_reason = f"Required competency for your current cadre role as {role_name}."

    competency_reason = f"'{item_title}' provides dedicated {coverage_level.lower()} coverage for {competency_name}."

    if level_fit_score >= 90.0:
        level_reason = "The curriculum difficulty is an optimal next-step progression from your demonstrated proficiency."
    elif level_fit_score >= 70.0:
        level_reason = "Appropriate difficulty level to consolidate and advance your competency."
    else:
        level_reason = "Provides introductory or prerequisite grounding."

    if not is_completed:
        novelty_reason = f"Fresh content from {item_provider} that has not been completed previously."
    else:
        novelty_reason = "Previously recorded in training history; recommended for refresher revision."

    summary = (
        f"Recommended because {competency_name} is a {priority_level} role requirement with a {gap_score:.1f}-pt deficit. "
        f"This {item_provider} course directly targets the competency at an appropriate learning level."
    )

    return {
        "summary": summary,
        "gap_reason": gap_reason,
        "role_reason": role_reason,
        "competency_reason": competency_reason,
        "level_reason": level_reason,
        "novelty_reason": novelty_reason,
    }
