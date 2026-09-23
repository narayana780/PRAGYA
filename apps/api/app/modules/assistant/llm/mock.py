import asyncio
import re
from typing import Any, AsyncIterator

from app.modules.assistant.llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for unit, integration, and offline testing.
    Produces grounded structured answers with valid source IDs based on input context.
    """

    def __init__(self, model_name: str = "pragya-mock-llm-v1", should_fail: bool = False):
        self._model_name = model_name
        self.should_fail = should_fail

    @property
    def model_name(self) -> str:
        return self._model_name

    async def health_check(self) -> bool:
        return not self.should_fail

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if self.should_fail:
            raise ConnectionError("Mock LLM Provider simulated failure: connection refused")

        user_query = ""
        for m in reversed(messages):
            role = getattr(m, "role", None) if not isinstance(m, dict) else m.get("role")
            content = getattr(m, "content", "") if not isinstance(m, dict) else m.get("content", "")
            if role == "user":
                user_query = content
                break

        # Check language across system prompt, messages, and user query
        all_text = (
            " ".join([
                getattr(m, "content", "") if not isinstance(m, dict) else m.get("content", "")
                for m in messages
            ])
            + (" " + (system_prompt or ""))
            + (" " + (context or ""))
        )

        lang = "en"
        all_lower = all_text.lower()
        if "hindi" in all_lower or "हिंदी" in all_text or any("\u0900" <= c <= "\u097F" for c in all_text):
            lang = "hi"
        elif "telugu" in all_lower or "తెలుగు" in all_text or any("\u0C00" <= c <= "\u0C7F" for c in all_text):
            lang = "te"

        query_lower = user_query.lower()

        # Check available sources in context
        available_sources = []
        if context:
            # Extract source IDs from context like [Source 1], [Source 2], etc.
            matches = re.findall(r"\[(?:Source\s+)?(\d+)\]", context)
            available_sources = sorted(list(set(int(m) for m in matches if int(m) > 0)))

        # Default citation list: cite available sources up to 2
        citations = available_sources[:2] if available_sources else []
        cite_tag = f" [{citations[0]}]" if citations else ""

        # Extract keywords or build grounded response
        if "evaporation" in query_lower or "वाष्पीकरण" in user_query or "బాష్పీభవనం" in user_query:
            if lang == "hi":
                answer = f"वाष्पीकरण (Evaporation) वह प्रक्रिया है जिसके द्वारा जल तरल अवस्था से गैसीय या वाष्प अवस्था में परिवर्तित होता है{cite_tag}।"
                explanation = "जब सौर ऊर्जा जल के तापमान को बढ़ाती है, तो अणु तीव्र गति से गति करते हैं और वायुमंडल में वाष्प के रूप में विलीन हो जाते हैं।"
                example = "उदाहरण के लिए, सूर्य के प्रकाश में गीले कपड़े सूखना जल चक्र के वाष्पीकरण चरण का स्पष्ट प्रमाण है।"
            elif lang == "te":
                answer = f"బాష్పీభవనం (Evaporation) అనేది నీరు ద్రవ స్థితి నుండి వాయు లేదా ఆవిరి స్థితికి మారే ప్రక్రియ{cite_tag}."
                explanation = "సౌర ఉష్ణోగ్రత పెరిగినప్పుడు నీటి అణువులు వేగంగా కదిలి వాతావరణంలోకి ఆవిరిగా చేరుతాయి."
                example = "ఉదాహరణకు, ఎండలో తడి బట్టలు ఆరడం అనేది నీటి చక్రంలో బాష్పీభవన ప్రక్రియకు ప్రత్యక్ష నిదర్శనం."
            else:
                answer = f"Evaporation is the fundamental thermodynamic process by which water changes from a liquid to a gas or vapor{cite_tag}."
                explanation = "Thermal energy from solar radiation breaks intermolecular bonds between water molecules, allowing water to enter the atmosphere as vapor."
                example = "A common practical example is a shallow puddle drying up on the pavement on a sunny day."

        elif "stratified sampling" in query_lower:
            answer = f"Stratified sampling is a probabilistic survey design where the heterogeneous population is partitioned into mutually exclusive and exhaustive homogeneous subgroups called strata{cite_tag}."
            explanation = "Independent samples are selected from each stratum, dramatically decreasing sampling variance for skewed statistical distributions."
            example = "For example, MoSPI establishment surveys stratify enterprises by employment size classes (1-9, 10-49, 50+) before random selection."

        elif "pragya" in query_lower:
            answer = f"PRAGYA is an AI-powered workforce intelligence and competency management platform built for national statistical architectures{cite_tag}."
            explanation = "It correlates empirical job role requirements with official training material, diagnosing micro-level skill gaps and delivering verified, source-grounded evidence."
            example = "For example, PRAGYA ingests MoSPI manuals to adapt explanations and recommendations to each statistical officer's evaluated level."

        elif "hint" in query_lower:
            answer = f"Here is a guided conceptual hint to help you solve this{cite_tag}: focus on identifying the distinct strata before drawing any sample elements."
            explanation = "Consider how partitioning the target population affects within-strata homogeneity versus between-strata variation."
            example = None

        elif "practice" in query_lower or "test" in query_lower:
            answer = f"Practice Question{cite_tag}: If an establishment population has high variance across states, why is stratified allocation statistically superior to simple random sampling?"
            explanation = "Formulate your response focusing on standard error reduction and subgroup representation."
            example = "Key hint: Think about proportional versus optimum (Neyman) allocation."

        elif "summarize" in query_lower:
            answer = f"Key Summary from retrieved materials{cite_tag}: The core focus is establishing standardized, auditable survey procedures across statistical field operations."
            explanation = "The guidelines mandate systematic stratification, documentation of non-response, and adherence to quality assurance benchmarks."
            example = None

        else:
            answer = f"Based on the official learning materials retrieved for your study{cite_tag}, this concept addresses statistical framework standards and operational procedures."
            explanation = "The reference text specifies criteria, domain definitions, and analytical protocols governing this topic."
            example = "Review the cited manual sections for step-by-step procedural guidelines."

        return LLMResponse(
            answer=answer,
            explanation=explanation,
            example=example,
            citations=citations,
            model=self._model_name,
            usage={"prompt_tokens": 120, "completion_tokens": 85, "total_tokens": 205},
            raw_output=f"{answer}\n\n{explanation or ''}\n\n{example or ''}".strip(),
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        response = await self.generate(
            messages=messages,
            system_prompt=system_prompt,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        words = response.answer.split(" ")
        for w in words:
            yield w + " "
            await asyncio.sleep(0.01)
