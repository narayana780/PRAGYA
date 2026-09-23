"""
Canonical definitions and conversion utilities for the PRAGYA Competency Framework.
"""

CANONICAL_DOMAINS = [
    {
        "code": "STATISTICAL",
        "name": "Statistical",
        "description": "Core statistical methodologies, survey sampling, economic indicators, and national quality frameworks.",
        "display_order": 1,
    },
    {
        "code": "TECHNICAL",
        "name": "Technical",
        "description": "Computational tools, statistical programming languages, database architectures, and data science platforms.",
        "display_order": 2,
    },
    {
        "code": "DIGITAL_GOVERNANCE",
        "name": "Digital Governance",
        "description": "Data privacy legislation, cybersecurity standards, digital public infrastructure, and government cloud security.",
        "display_order": 3,
    },
    {
        "code": "BEHAVIOURAL_MANAGERIAL",
        "name": "Behavioural / Managerial",
        "description": "Public leadership, stakeholder communication, project governance, ethics, and organisational transformation.",
        "display_order": 4,
    },
]

PROFICIENCY_LEVELS = [
    {
        "level_number": 1,
        "name": "Awareness",
        "description": "Understands basic terminology and fundamental concepts.",
        "minimum_score": 0,
        "maximum_score": 20,
        "display_order": 1,
    },
    {
        "level_number": 2,
        "name": "Foundation",
        "description": "Can understand and perform guided, foundational tasks.",
        "minimum_score": 21,
        "maximum_score": 40,
        "display_order": 2,
    },
    {
        "level_number": 3,
        "name": "Working",
        "description": "Can perform the competency independently in normal operational situations.",
        "minimum_score": 41,
        "maximum_score": 60,
        "display_order": 3,
    },
    {
        "level_number": 4,
        "name": "Proficient",
        "description": "Can apply the competency confidently to complex, non-routine tasks.",
        "minimum_score": 61,
        "maximum_score": 80,
        "display_order": 4,
    },
    {
        "level_number": 5,
        "name": "Advanced",
        "description": "Can resolve advanced problems, mentor others, and apply the competency strategically.",
        "minimum_score": 81,
        "maximum_score": 100,
        "display_order": 5,
    },
]


def score_to_proficiency_level(score: float) -> tuple[int, str]:
    """
    Converts a 0-100 numerical competency score into its canonical 1-5 level and level name.
    """
    normalized = max(0, min(100, round(score)))
    for lvl in PROFICIENCY_LEVELS:
        if lvl["minimum_score"] <= normalized <= lvl["maximum_score"]:
            return lvl["level_number"], lvl["name"]
    return 1, "Awareness"


def level_to_score_range(level: int) -> tuple[int, int]:
    """
    Converts a 1-5 proficiency level into its expected (min_score, max_score) tuple.
    """
    for lvl in PROFICIENCY_LEVELS:
        if lvl["level_number"] == level:
            return lvl["minimum_score"], lvl["maximum_score"]
    return 0, 20
