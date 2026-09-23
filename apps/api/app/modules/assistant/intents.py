import enum
import re


class AssistantIntent(str, enum.Enum):
    EXPLAIN = "EXPLAIN"
    DEFINE = "DEFINE"
    SUMMARIZE = "SUMMARIZE"
    EXAMPLE = "EXAMPLE"
    HINT = "HINT"
    PRACTICE = "PRACTICE"
    REVISE = "REVISE"
    COMPARE = "COMPARE"


class IntentClassifier:
    """
    Deterministic regex/keyword intent classifier for user learning inquiries.
    """

    @staticmethod
    def classify(query: str) -> AssistantIntent:
        text = query.lower().strip()

        # Check in order of specificity
        if re.search(r"\b(hint|clue|guide me without giving|point me in the right direction)\b", text):
            return AssistantIntent.HINT

        if re.search(r"\b(practice|quiz|test my|question for me|exercise|challenge me|problem to solve)\b", text):
            return AssistantIntent.PRACTICE

        if re.search(r"\b(revise|revision|recap|what should i review|brush up|refresh my)\b", text):
            return AssistantIntent.REVISE

        if re.search(r"\b(compare|contrast|difference between|versus|vs\.?|distinguish)\b", text):
            return AssistantIntent.COMPARE

        if re.search(r"\b(summarize|summary|overview|tldr|key takeaways|bullet points|wrap up)\b", text):
            return AssistantIntent.SUMMARIZE

        if re.search(r"\b(example|illustration|case study|sample scenario|demonstrate with|show me an instance)\b", text):
            return AssistantIntent.EXAMPLE

        if re.search(r"\b(define|definition|what is meant by|meaning of|define the term)\b", text):
            return AssistantIntent.DEFINE

        # Default fallback
        return AssistantIntent.EXPLAIN

    @staticmethod
    def get_intent_instruction(intent: AssistantIntent) -> str:
        instructions = {
            AssistantIntent.EXPLAIN: "Deliver a clear, structured explanation addressing the user's question, followed by an applied context.",
            AssistantIntent.DEFINE: "Deliver a concise, rigorous, grounded definition of the concept directly citing the reference text.",
            AssistantIntent.SUMMARIZE: "Synthesize a structured summary highlighting the core principles and operational rules documented in the evidence.",
            AssistantIntent.EXAMPLE: "Provide an applied, concrete workplace example directly grounded in the provided document scenarios.",
            AssistantIntent.HINT: "Provide a conceptual hint that nudges the learner towards the answer without revealing the entire solution.",
            AssistantIntent.PRACTICE: "Formulate 1-2 focused, conceptual practice questions based strictly on the retrieved document material to test comprehension.",
            AssistantIntent.REVISE: "Highlight the key concepts and common pitfalls from the material that the learner should review.",
            AssistantIntent.COMPARE: "Compare and contrast the requested concepts using only the evidence provided; explicitly state if material is insufficient for comparison.",
        }
        return instructions.get(intent, instructions[AssistantIntent.EXPLAIN])
