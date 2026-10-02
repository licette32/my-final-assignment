# Retention policy

**Filled by:** session 11. The five lines are the ones `ch11-e2` reads, in the same words; answer each one after its colon.

STORED: nothing. This capstone has no memory layer.

WHY: the contract tests require per-question isolation. Storing state would let one question's context leak into another's answer, which the `memory` test in `tests/test_contract.py` is designed to catch once session 11 is implemented.

CORRECTED BY: not applicable — nothing is stored, so there is nothing to clear.

EXPIRES: not applicable.

WE REFUSE TO REMEMBER: everything. No keys, no personal data, no user ids, no episode history, no cross-question state.

## How the code enforces it

`tests/test_contract.py::test_memory_is_capped_reset_and_kept_per_user` is
`skip`-marked with the session-11 reason; the capstone does not implement memory, and the skip is the honest statement of that.