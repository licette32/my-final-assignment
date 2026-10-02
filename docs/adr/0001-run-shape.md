# ADR 0001: the shape of one run

**Filled by:** session 10, for the choice you measured in session 8 (chain,
loop or graph, and the model calls each one cost). The four fields are the
ones `ch10-e2` reads.

- Status: accepted
- Date: 2026-10-02

## Context

The capstone contract requires: zero model calls on an unsupported question, at most one corrective retry on a parse failure, and a flagged refusal on provider error or timeout. Each of these is a guarantee about the number of model calls one question costs. A loop whose exit condition the model controls cannot give that guarantee. Measured on the practice set with `claude-sonnet-5`: a chain costs 0 or 1 model call per question.

## Decision (`decision`)

We keep the chain in `agent.py`: retrieve, filter by topic, one model call, verify citations, flag or refuse. `max_tool_calls=3` is a budget, not a loop condition.

## Options considered (`options_considered`)

1. Chain: fixed steps, one model call at most.
2. Loop: the model decides the next step until it stops.

## Why not the other option (`why_not`)

A loop makes the "zero model calls" and "one corrective retry" guarantees structural only if the loop itself is bounded, which turns it into a chain with extra machinery. The practice set has no case that needs a second retrieval round after reading the first, so the loop buys nothing today.

## What would reverse it (`reverses_it`)

When a question in the golden set needs more than 2 model calls in 10 of 10 runs to cover its required concepts, the chain's one-call guarantee stops holding and a bounded loop becomes the honest shape.
