# my-final-assignment

Answers developer questions from the six course documents, cites the source it quoted, and refuses visibly (flagged, no citation, no model call) when the corpus does not support an answer.

## The problem

Developer questions about agents, RAG, evaluation, prompt injection, MCP, and structured outputs are usually answered from training data with no source and no trace. When the model is wrong, there is no way to see which step failed. This agent answers only from a versioned corpus, cites what it quoted, and refuses when the corpus says nothing.

## Demo

Two runs, pasted exactly as the commands printed them. Never an edited one.
`trace` prints every step the agent took, then the answer.

### One supported answer

```bash
uv run bootcamp capstone trace "How does chunking work in RAG?"
```

```text
[retrieve] top_k=5 -> [('rag-basics', 0), ('rag-basics', 1), ('rag-basics', 2)]
[llm_call] attempt 1: 396 chars
[decision] answered with citations ['rag-basics']

answer: In retrieval-augmented generation, chunking splits documents into
passages small enough to be individually relevant. The key principle is to
respect paragraph boundaries rather than cutting at a fixed character count
mid-sentence.
citations: ['rag-basics']
confidence: 0.95
needs_human_review: False
```

### One refusal

```bash
uv run bootcamp capstone trace "What is the capital city of Mongolia?"
```

```text
[retrieve] top_k=5 -> []
[decision] no relevant chunks; refusing without an LLM call

answer: I don't know based on the provided corpus.
citations: []
confidence: 0.0
needs_human_review: True
```

## Architecture

One run is a short chain, not a loop:

1. **Retrieve** — `retrieve(question, documents, top_k=5)` scores chunks. Zero hits → flagged refusal, zero model calls.
2. **Pre-filter by topic** — `_detect_topic(question)` keeps only the corpus documents that can answer, plus any non-course document (so the contract tests can inject their own).
3. **One model call** — `answer_question` calls the provider once, with `ANSWER_JSON_INSTRUCTIONS` on the system prompt. One corrective retry on a parse failure, then a flagged refusal.
4. **Citation verification** — citations the retriever never returned are stripped and the answer is flagged for human review.
5. **Injection flag** — if any retrieved document matches `_INJECTION_PATTERNS`, the answer is flagged and confidence is clamped
   to 0.2.
6. **Timeout wrapper** — the whole run executes in a worker thread bounded by `timeout_s=30`. A hanging provider or a provider error becomes a flagged refusal, never a raised exception.

One question costs **zero model calls** (empty retrieval) or **one model call** (one corrective retry at most).

See [docs/adr/0001-run-shape.md](docs/adr/0001-run-shape.md).

## Measured results

| What | Command | Model | Result |
|---|---|---|---|
| Contract tests | `uv run pytest` | fake | 7 passed, 2 skipped |
| Practice grader | `uv run bootcamp final grade` | `claude-sonnet-5` | 9/10 (90%), critical safety gate PASSED |
| Evaluation, before and after | see [docs/EVAL_REPORT.md](docs/EVAL_REPORT.md) | `claude-sonnet-5` | 7/10 → 9/10 |



## The honest limitation

`fa-02` fails `claim_support` on runs where the model paraphrases "validate at the boundary" as "responsible for validation": the grader matches literal phrases. The next step is mine, in `agent.py`: force the literal phrasing (e.g. a retry that asks the model to include the missing phrases), not change the grader. The full ranked list is in [docs/ISSUES.md](docs/ISSUES.md).


## How to run it

```bash
git clone https://github.com/licette32/my-final-assignment && cd my-final-assignment && uv sync && uv run pytest
```

No key needed: without a `.env` it runs on the offline fake model. For a real model, copy `.env.example` to `.env`, fill in your provider, and `uv sync --extra anthropic` (or `--extra openai`).

To hand in the final assignment, commit and push, then run
`uv run bootcamp capstone submit --github licette32`. It runs the practice set first, then answers the final questions and opens the pull request.
`--dry-run` shows the bundle without handing anything in.



## Credits

Peer review from a classmate during sessions 13-14 surfaced the injection-flag idea. The reimplementation is mine: `_detect_topic`, the wrapper, the timeout handling, and this documentation.


---

| Path | What it is |
|---|---|
| `agent.py` | The agent: `YourAgent`, the class the tests, `trace` and the grader run |
| `tests/test_contract.py` | The capstone contract, as tests (`uv run pytest -k refusal`, `-k injection`, ...) |
| `data/corpus/` | The six source documents, versioned; nothing here writes to them |
| `docs/EVAL_REPORT.md` | Numbers you produced, before and after, with the command behind each |
| `docs/SKILL.md` | A skill another assistant can load (session 10) |
| `docs/adr/0001-run-shape.md` | The architecture decision and what would reverse it (session 10) |
| `docs/RETENTION.md` | What a session remembers, and what it refuses to (session 11) |
| `docs/ISSUES.md` | The ranked issue list (session 9, kept until 14) |

Built during the Dev3Pack AI Engineering bootcamp, on the course package at
commit `85ad371e3e6354fc18edb4522b1fd66ac6223f62` of https://github.com/Gecko-Academy/dev3pack-cohort-2026-09.


