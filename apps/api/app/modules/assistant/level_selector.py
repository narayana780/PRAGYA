import enum


class ExplanationLevel(str, enum.Enum):
    FOUNDATION = "FOUNDATION"
    WORKING = "WORKING"
    ADVANCED = "ADVANCED"


class ExplanationLevelSelector:
    """
    Deterministic selector mapping assessed competency levels to pedagogical explanation depth.
    The LLM does NOT calculate competency level; Stage 5 assessment engine remains the ground truth.
    """

    @staticmethod
    def select(current_level: int | None) -> ExplanationLevel:
        """
        Map numerical competency level (1-5) to explanation depth:
        - <= 1 or None -> FOUNDATION (simple language, definitions, basic analogies, step-by-step)
        - 2 or 3       -> WORKING (practical examples, applied operational workflows, field scenarios)
        - >= 4         -> ADVANCED (complex edge cases, deeper theoretical & systemic trade-offs)
        """
        if current_level is None or current_level <= 1:
            return ExplanationLevel.FOUNDATION
        elif current_level in (2, 3):
            return ExplanationLevel.WORKING
        else:
            return ExplanationLevel.ADVANCED

    @staticmethod
    def get_instructions(level: ExplanationLevel) -> str:
        if level == ExplanationLevel.FOUNDATION:
            return (
                "PEDAGOGICAL LEVEL: FOUNDATION\n"
                "- Use clear, straightforward language without overwhelming statistical jargon.\n"
                "- Emphasize formal definitions and basic intuitive analogies.\n"
                "- Break down complex mechanisms into sequential, step-by-step explanations."
            )
        elif level == ExplanationLevel.WORKING:
            return (
                "PEDAGOGICAL LEVEL: WORKING\n"
                "- Focus on practical field application, operational procedures, and standard methodologies.\n"
                "- Provide applied workplace scenarios directly relevant to statistical surveying and reporting.\n"
                "- Balance procedural clarity with technical precision."
            )
        else:
            return (
                "PEDAGOGICAL LEVEL: ADVANCED\n"
                "- Dive into nuanced technical subtleties, theoretical foundations, and methodological trade-offs.\n"
                "- Address edge cases, variance properties, efficiency trade-offs, and systemic considerations.\n"
                "- Assume strong foundational literacy; deliver rigorous analytical depth."
            )
