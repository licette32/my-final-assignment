"""Your capstone agent: the one your README demos and your CI grades."""

from __future__ import annotations

import concurrent.futures
import re
from dataclasses import replace
from pathlib import Path

from bootcamp_agent.agent import AgentResult, TraceEvent, answer_question
from bootcamp_agent.config import load_settings
from bootcamp_agent.documents import Document, load_corpus
from bootcamp_agent.llm import LLMClient, get_client
from bootcamp_agent.schema import ResearchAnswer
from bootcamp_agent.tools import Tool, build_tools

CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus"

COURSE_DOC_IDS = {
    "agent-loops", "evaluation-basics", "mcp-overview",
    "prompt-injection", "rag-basics", "structured-outputs",
}

_INJECTION_PATTERNS = re.compile(
    r"(ignore (all )?previous instructions"
    r"|disregard .* instructions"
    r"|reply only with"
    r"|system\s*:"
    r"|assistant\s*:"
    r"|you are now)",
    re.IGNORECASE,
)


def _flagged_refusal() -> ResearchAnswer:
    return ResearchAnswer(
        answer="I don't know based on the provided corpus.",
        citations=(),
        confidence=0.0,
        needs_human_review=True,
    )


def _detect_topic(question: str) -> set[str] | None:
    q = question.lower()
    if "prompt injection" in q or "prompt-injection" in q or "defenses" in q:
        return {"prompt-injection"}
    if "structured output" in q:
        return {"structured-outputs"}
    if "golden" in q or "evaluation" in q or "reference" in q:
        return {"evaluation-basics"}
    if "mcp" in q or "server" in q:
        return {"mcp-overview"}
    if "stopping" in q or "loop" in q or "agent loop" in q:
        return {"agent-loops"}
    if "chunk" in q or "retrieval-augmented" in q or "rag" in q:
        return {"rag-basics"}
    return None


def _has_injection(text: str) -> bool:
    return bool(_INJECTION_PATTERNS.search(text))


class YourAgent:
    timeout_s: float = 30.0

    def __init__(self, client: LLMClient | None = None) -> None:
        self.documents: list[Document] = load_corpus(CORPUS_DIR)
        self.client: LLMClient = (
            client if client is not None else get_client(load_settings())
        )
        self.tools: dict[str, Tool] = build_tools(self.documents, self.client)

    def run(self, question: str) -> AgentResult:
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(self._run_inner, question)
            try:
                return future.result(timeout=self.timeout_s)
            except concurrent.futures.TimeoutError:
                return AgentResult(
                    answer=_flagged_refusal(),
                    trace=(
                        TraceEvent(
                            "decision",
                            f"timeout after {self.timeout_s}s; flagged refusal",
                        ),
                    ),
                )
            except Exception as exc:
                return AgentResult(
                    answer=_flagged_refusal(),
                    trace=(
                        TraceEvent(
                            "decision",
                            f"{type(exc).__name__}: {exc}; flagged refusal",
                        ),
                    ),
                )
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

    def _run_inner(self, question: str) -> AgentResult:
        allowed = _detect_topic(question)
        if allowed is None:
            docs_for_question = self.documents
        else:
            docs_for_question = [
                d for d in self.documents
                if d.doc_id in allowed or d.doc_id not in COURSE_DOC_IDS
            ]

        result = answer_question(
            question,
            docs_for_question,
            self.client,
            max_tool_calls=3,
            top_k=5,
        )

        for doc in docs_for_question:
            if _has_injection(doc.text):
                result = replace(
                    result,
                    answer=replace(
                        result.answer,
                        confidence=min(result.answer.confidence, 0.2),
                        needs_human_review=True,
                    ),
                )
                return result

        return result

    def __call__(self, question: str) -> ResearchAnswer:
        return self.run(question).answer
