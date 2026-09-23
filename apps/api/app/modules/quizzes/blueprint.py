import uuid
from typing import Any
from pydantic import BaseModel, Field


class QuestionBlueprint(BaseModel):
    concept: str
    difficulty: str = "BEGINNER"
    bloom_level: str = "REMEMBER"
    learning_objective: str
    target_competency_id: uuid.UUID | None = None
    source_chunk_ids: list[uuid.UUID] = Field(default_factory=list)
    source_page_number: int | None = None


class BlueprintGenerator:
    """
    Constructs an auditable distribution of Question Blueprints across concepts,
    difficulty levels, and Bloom's Taxonomy.
    """

    BLOOM_MAP = {
        "BEGINNER": ["REMEMBER", "UNDERSTAND"],
        "INTERMEDIATE": ["UNDERSTAND", "APPLY"],
        "ADVANCED": ["APPLY", "ANALYZE"],
    }

    @staticmethod
    def generate_blueprints(
        concepts: list[dict[str, Any]],
        question_count: int = 5,
        target_difficulty: str = "BEGINNER",
        target_bloom: str | None = None,
        competency_id: uuid.UUID | None = None,
        chunks: list[Any] = None,
    ) -> list[QuestionBlueprint]:
        blueprints: list[QuestionBlueprint] = []
        chunks = chunks or []

        # Determine difficulty distribution policy
        if target_difficulty == "BEGINNER":
            difficulties = ["BEGINNER"] * question_count
        elif target_difficulty == "ADVANCED":
            difficulties = ["ADVANCED"] * question_count
        elif target_difficulty == "INTERMEDIATE":
            difficulties = ["INTERMEDIATE"] * question_count
        else:  # BALANCED
            b_cnt = max(1, int(question_count * 0.4))
            i_cnt = max(1, int(question_count * 0.4))
            a_cnt = question_count - b_cnt - i_cnt
            difficulties = (["BEGINNER"] * b_cnt) + (["INTERMEDIATE"] * i_cnt) + (["ADVANCED"] * max(0, a_cnt))

        for i in range(question_count):
            c_idx = i % len(concepts) if concepts else 0
            c_obj = concepts[c_idx] if concepts else {"concept": "General Concept", "description": "General learning material concept"}
            concept_name = c_obj.get("concept", "General Concept")

            diff = difficulties[i] if i < len(difficulties) else target_difficulty
            if target_bloom:
                bloom = target_bloom
            else:
                possible_blooms = BlueprintGenerator.BLOOM_MAP.get(diff, ["REMEMBER", "UNDERSTAND"])
                bloom = possible_blooms[i % len(possible_blooms)]

            # Map matching chunk if available
            matched_chunk_ids = []
            page_num = None
            if chunks:
                chunk = chunks[i % len(chunks)]
                matched_chunk_ids = [chunk.id]
                page_num = getattr(chunk, "page_number", None)

            bp = QuestionBlueprint(
                concept=concept_name,
                difficulty=diff,
                bloom_level=bloom,
                learning_objective=f"Evaluate understanding of {concept_name} at {bloom} level ({diff}).",
                target_competency_id=competency_id,
                source_chunk_ids=matched_chunk_ids,
                source_page_number=page_num,
            )
            blueprints.append(bp)

        return blueprints
