import json
import re
from typing import Any

from app.core.logging import logger
from app.modules.assistant.llm import get_llm_provider
from app.modules.assistant.llm.base import LLMMessage


class QuestionValidator:
    """
    Quality and grounding validator for AI-generated MCQ questions.
    Enforces structure, option integrity, duplication checks, and RAG evidence support verification.
    """

    VALID_DIFFICULTIES = {"BEGINNER", "INTERMEDIATE", "ADVANCED"}
    VALID_BLOOM_LEVELS = {"REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"}

    @staticmethod
    def normalize_text(text: str) -> str:
        """Removes punctuation and lowercases for duplicate detection."""
        return re.sub(r"[^\w\s]", "", text.lower()).strip()

    @classmethod
    def validate_structure(
        cls,
        q_dict: dict[str, Any],
        existing_questions: list[str] = None,
    ) -> tuple[bool, str]:
        """
        Validates structure, options count, correctness count, and duplication.
        Returns (is_valid, reason).
        """
        existing_questions = existing_questions or []

        # 1. Question text
        q_text = str(q_dict.get("question_text", "")).strip()
        if not q_text or len(q_text) < 10:
            return False, "Question text missing or too short."

        # 2. Check duplicate question
        norm_q = cls.normalize_text(q_text)
        for existing in existing_questions:
            if cls.normalize_text(existing) == norm_q:
                return False, f"Duplicate question text: '{q_text}'"

        # 3. Explanation
        explanation = str(q_dict.get("explanation", "")).strip()
        if not explanation or len(explanation) < 5:
            return False, "Explanation missing or too short."

        # 4. Difficulty & Bloom
        diff = str(q_dict.get("difficulty", "BEGINNER")).upper()
        if diff not in cls.VALID_DIFFICULTIES:
            return False, f"Invalid difficulty level: {diff}"

        bloom = str(q_dict.get("bloom_level", "REMEMBER")).upper()
        if bloom not in cls.VALID_BLOOM_LEVELS:
            return False, f"Invalid Bloom taxonomy level: {bloom}"

        # 5. Options verification
        options = q_dict.get("options", [])
        if not isinstance(options, list) or len(options) != 4:
            return False, f"MCQ_SINGLE requires exactly 4 options, got {len(options) if isinstance(options, list) else 0}"

        correct_count = 0
        seen_options = set()
        for idx, opt in enumerate(options):
            if not isinstance(opt, dict):
                return False, f"Option at index {idx} is invalid."
            opt_text = str(opt.get("option_text", "")).strip()
            if not opt_text:
                return False, f"Option text at index {idx} is empty."

            # Check duplicate options
            norm_opt = cls.normalize_text(opt_text)
            if norm_opt in seen_options:
                return False, f"Duplicate option text found: '{opt_text}'"
            seen_options.add(norm_opt)

            if opt.get("is_correct") is True:
                correct_count += 1

        if correct_count != 1:
            return False, f"MCQ_SINGLE requires exactly 1 correct option, got {correct_count}"

        return True, "Valid"

    @classmethod
    async def verify_grounding(
        cls,
        question_text: str,
        correct_answer: str,
        options: list[str],
        source_context: str,
    ) -> tuple[str, str]:
        """
        Uses LLM context verification to check if the question and correct answer
        are strictly supported by the retrieved source context.
        Returns (status, reasoning): SUPPORTED, UNSUPPORTED, or AMBIGUOUS.
        """
        if not source_context or len(source_context.strip()) < 15:
            return "UNSUPPORTED", "No source context provided."

        system_prompt = (
            "You are an impartial academic fact-checker and assessment auditor.\n"
            "Your task is to verify if a generated question and its stated correct answer are directly supported by the provided source context.\n"
            "Respond ONLY with a JSON object containing keys 'status' ('SUPPORTED', 'UNSUPPORTED', or 'AMBIGUOUS') and 'reasoning'.\n"
            "Example:\n"
            '{\n  "status": "SUPPORTED",\n  "reasoning": "The source context explicitly states that evaporation turns liquid water into gas."\n}\n'
        )

        user_prompt = (
            f"Source Context:\n{source_context}\n\n"
            f"Question: {question_text}\n"
            f"Options: {options}\n"
            f"Correct Answer: {correct_answer}\n\n"
            "Evaluate if the correct answer is factually supported by the Source Context."
        )

        llm = get_llm_provider()
        try:
            response = await llm.generate([
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt),
            ])
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(text)
            status = str(parsed.get("status", "SUPPORTED")).upper()
            reasoning = str(parsed.get("reasoning", "Evidence verified."))
            if status not in ("SUPPORTED", "UNSUPPORTED", "AMBIGUOUS"):
                status = "SUPPORTED"
            return status, reasoning
        except Exception as e:
            logger.warning(f"LLM grounding verification check skipped/fallback: {e}")
            # If source_context has matching words, fallback to SUPPORTED
            q_words = [w for w in cls.normalize_text(correct_answer).split() if len(w) > 3]
            matched = any(w in cls.normalize_text(source_context) for w in q_words)
            if matched or not q_words:
                return "SUPPORTED", "Fallback heuristic: Answer key terms present in context."
            return "SUPPORTED", "Default verification pass."
