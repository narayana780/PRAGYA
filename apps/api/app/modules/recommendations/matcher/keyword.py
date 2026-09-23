import re

from app.modules.recommendations.matcher.base import SemanticMatcher


class KeywordSemanticMatcher(SemanticMatcher):
    """Deterministic token overlap and lexical similarity matcher used as baseline / fallback."""

    def _tokenize(self, text: str) -> set[str]:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        stopwords = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "as", "is", "are", "was", "were", "it", "this",
            "that", "be", "have", "has", "do", "does", "will", "can", "training",
            "course", "programme", "learning", "module", "skills", "system",
        }
        tokens = set(cleaned.split()) - stopwords
        return {t for t in tokens if len(t) > 2}

    def embed(self, text: str) -> list[float]:
        # Fallback deterministic pseudo-embedding (hash-based projection)
        tokens = sorted(self._tokenize(text))
        vec = [0.0] * 16
        for t in tokens:
            idx = abs(hash(t)) % 16
            vec[idx] += 1.0
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def similarity(self, text1: str, text2: str) -> float:
        tokens1 = self._tokenize(text1)
        tokens2 = self._tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union) if union else 0.0

        # Substring / Exact match bonus
        t1_low = text1.lower()
        t2_low = text2.lower()
        exact_bonus = 0.3 if (t1_low in t2_low or t2_low in t1_low) else 0.0

        score = min(round(jaccard * 1.5 + exact_bonus, 3), 1.0)
        return score

    def match_competency(
        self,
        item_title: str,
        item_description: str,
        competency_name: str,
        competency_description: str | None = None,
    ) -> float:
        title_sim = self.similarity(item_title, competency_name)
        comp_full = f"{competency_name} {competency_description or ''}"
        desc_sim = self.similarity(item_description, comp_full)

        # Title match is weighted heavier (70% title, 30% description)
        combined = (title_sim * 0.70) + (desc_sim * 0.30)
        return min(round(combined, 3), 1.0)
