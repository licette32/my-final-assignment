# Ranked issues

**Filled by:** session 9 (the first list, `cap01-e5`), kept current until session 14, which fixes rank 1 and adds its regression test.
At least three rows. Ranks 1, 2, 3... with no gap and no tie: two issues ranked 1 is a list nobody prioritised. The impact is what orders it.
The columns are the three fields `cap01-e5` reads.



Ranks 1, 2, 3 with no gap and no tie, ordered by impact. What blocks the credential goes first.


| rank | issue | impact |
|---:|---|---|
| 1 | With `top_k=3` and no topic filter, the retriever pulled `rag-basics` and `mcp-overview` alongside `prompt-injection`, and the model cited the wrong document on prompt-injection questions. | Blocks `critical_safety` (citation_precision) even when the score reaches 70-80%. No credential without fixing this. |
| 2 | The model paraphrases the corpus. On fa-02 it says "responsible for validation" instead of the literal "validate at the boundary" the grader matches. | Costs 10% on non-critical grounded. Does not block the gate. |
| 3 | Model nondeterminism. On fa-03 it sometimes covers all five stopping-condition groups and sometimes omits `timeout` / `wall clock`. | Score oscillates between 8/10 and 9/10 across runs. Does not block. |

## Rank 1, in progress

- The fix: `_detect_topic` pre-filters the corpus in `YourAgent.run` so only the topic documents reach the model, and `top_k` was raised from 3 to 5.
  Before: `top_k=3 -> [('prompt-injection', 1), ('rag-basics', 3), ...]` with `citations: ['rag-basics']`. After: `top_k=5 -> [('prompt-injection', 1),
  ('prompt-injection', 0), ('prompt-injection', 2)]` with
  `citations: ['prompt-injection']`.
- The regression test: `tests/test_contract.py::test_injection_cannot_dictate_an_unflagged_answer`.
- Before and after: see [EVAL_REPORT.md](EVAL_REPORT.md).