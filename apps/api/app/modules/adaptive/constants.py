"""
Constants, deterministic progression rules, stopping conditions, and confidence formulas
for the PRAGYA Adaptive Assessment & Closed-Loop Recalibration Engine.

NOTE: All formulas and weights represent the PRAGYA prototype methodology.
"""

from enum import Enum

MIN_ADAPTIVE_QUESTIONS = 5
MAX_ADAPTIVE_QUESTIONS = 15
TARGET_CONFIDENCE = 0.85
MAX_RECALIBRATION_DELTA = 20.0


class AdaptiveSessionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class AdaptiveDifficulty(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


DIFFICULTY_ORDER = [
    AdaptiveDifficulty.BEGINNER.value,
    AdaptiveDifficulty.INTERMEDIATE.value,
    AdaptiveDifficulty.ADVANCED.value,
]


def score_to_initial_level(score: float | None) -> str:
    """
    Deterministic rule for selecting starting difficulty from previous demonstrated score:
    - Score < 30: BEGINNER
    - 30 <= Score < 60: INTERMEDIATE
    - Score >= 60: ADVANCED
    Defaults to BEGINNER if no previous score exists.
    """
    if score is None or score < 30.0:
        return AdaptiveDifficulty.BEGINNER.value
    if score < 60.0:
        return AdaptiveDifficulty.INTERMEDIATE.value
    return AdaptiveDifficulty.ADVANCED.value


def next_difficulty(current: str, is_correct: bool) -> str:
    """
    Deterministic single-step difficulty adaptation rule:
    - Correct: increase one step, maximum ADVANCED.
    - Incorrect: decrease one step, minimum BEGINNER.
    Does NOT jump more than one level at a time.
    """
    current_norm = current.upper()
    if is_correct:
        if current_norm == AdaptiveDifficulty.BEGINNER.value:
            return AdaptiveDifficulty.INTERMEDIATE.value
        return AdaptiveDifficulty.ADVANCED.value
    else:
        if current_norm == AdaptiveDifficulty.ADVANCED.value:
            return AdaptiveDifficulty.INTERMEDIATE.value
        return AdaptiveDifficulty.BEGINNER.value


def calculate_adaptive_confidence(
    question_count: int,
    difficulties_seen: set[str],
    is_correct_history: list[bool],
) -> float:
    """
    PRAGYA Prototype Adaptive Confidence Formula.
    Deterministic, transparent, explainable:
    
    1. Base depth factor (up to 0.50):
       min(question_count / 10.0, 1.0) * 0.50
    2. Difficulty coverage bonus (up to 0.25):
       - 1 level tested: 0.10
       - 2 levels tested: 0.20
       - 3 levels tested: 0.25
    3. Consistency factor (up to 0.25):
       - For question_count < 3: 0.05
       - For question_count >= 3:
         Measures outcome stability based on performance convergence.
         Calculated as 0.25 - (0.5 * normalized flips / (question_count - 1))
         clamped to [0.05, 0.25].
         
    Final confidence is bounded in [0.20, 1.00] rounded to 2 decimal places.
    """
    if question_count == 0:
        return 0.0

    # 1. Depth factor
    depth_factor = min(question_count / 10.0, 1.0) * 0.50

    # 2. Coverage bonus
    num_diffs = len(difficulties_seen)
    if num_diffs >= 3:
        coverage_bonus = 0.25
    elif num_diffs == 2:
        coverage_bonus = 0.20
    else:
        coverage_bonus = 0.10

    # 3. Consistency factor
    if question_count < 3 or len(is_correct_history) < 3:
        consistency_factor = 0.05
    else:
        flips = sum(
            1 for i in range(len(is_correct_history) - 1)
            if is_correct_history[i] != is_correct_history[i + 1]
        )
        max_possible_flips = len(is_correct_history) - 1
        flip_ratio = flips / max_possible_flips if max_possible_flips > 0 else 0.0
        consistency_factor = max(0.05, min(0.25, 0.25 - (flip_ratio * 0.15)))

    combined = depth_factor + coverage_bonus + consistency_factor
    return round(max(0.20, min(1.00, combined)), 2)


def calculate_adaptive_score(
    responses: list[tuple[str, bool]],
) -> float:
    """
    Calculate normalized assessment score (0-100) based on questions and difficulties answered.
    Prototype methodology:
    Each question has a difficulty weight:
    - BEGINNER: 1.0 point base
    - INTERMEDIATE: 2.0 points base
    - ADVANCED: 3.0 points base
    Earned points = sum of difficulty weight for correct answers.
    Max points = sum of difficulty weight for all attempted questions.
    Returns (earned / max) * 100.0, rounded to 1 decimal place.
    """
    if not responses:
        return 0.0

    weights = {
        AdaptiveDifficulty.BEGINNER.value: 1.0,
        AdaptiveDifficulty.INTERMEDIATE.value: 2.0,
        AdaptiveDifficulty.ADVANCED.value: 3.0,
    }

    earned = 0.0
    total = 0.0
    for diff, is_corr in responses:
        w = weights.get(diff.upper(), 1.0)
        total += w
        if is_corr:
            earned += w

    if total == 0.0:
        return 0.0

    return round((earned / total) * 100.0, 1)
