---
name: quick-code
description: Fast implementation — 3 phases: coordinate, implement, complete. For trivial, well-defined tasks where no design or review is needed. The orchestrator implements directly (no delegation). Accept the trade-off: no independent review. Triggers on: quick implement, 快速实现, 直接写, just code it, simple change, 小改动.
---

# Quick Code Workflow

**Announce at start:** "Starting quick-code. This is a lightweight workflow — I'll implement directly. No independent review for trivial changes."

## Resume Protocol

**Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.

- **If it exists** and shows this workflow (quick-code) in progress: Read it. Announce "Resuming quick-code at Phase [N]." Continue from the recorded phase.
- **If it does not exist**: Start fresh from Phase 0.

**After each phase completes**, update `docs/progress/workflow-state.md`.

See `references/workflow-state.md` for the state file format and detailed protocol.

## Orchestrator Role

You implement everything yourself. This is the ONLY workflow where you write code directly. Accept the trade-off: there is no independent review. If you're wrong, there's no safety net. Use this ONLY for truly trivial changes.

```
Phase 0  Coordinate       You + User                 Task confirmed
Phase 1  Implement        You                        Code + tests
Phase 2  Complete         You                        Verified, committed
```

**No user checkpoints needed.**

## When to Use (vs Not)

**Use quick-code when:**
- Single file or a few lines in 2-3 files.
- No architectural decisions. No new dependencies.
- The user's instructions are specific enough to act on immediately.
- Mechanical changes: add a field, wire up a callback, delete dead code, fix a typo-level bug.

**Do NOT use quick-code when:**
- 4+ files with dependencies → Use `feature-dev` for independent review.
- Ambiguous requirements → Use `design` first.
- Unknown root cause → Use `bugfix` for systematic debugging.

## Phase 0 — Coordinate

1. Read the request. Rephrase in one sentence.
2. If ambiguous, ask ONE clarifying question. No more.
3. **Write `docs/progress/workflow-state.md`**: workflow=quick-code, mode=solo, phase=0.
4. Proceed immediately.

## Phase 1 — Implement

1. Read files you're about to change.
2. Write the code. Run tests.
3. Commit with a clear message.
4. **Update workflow-state.md**: phase=1 completed.

## Phase 2 — Complete

1. Summarize what changed in 1-2 sentences.
2. Confirm tests pass. Done.
3. **Delete or mark `docs/progress/workflow-state.md` as completed.**

## Rules

- If you think "this is more complex than I thought", STOP. Suggest switching to `feature-dev`.
- One task per session. Don't chain quick-codes — that's a feature that needs review.
- Always run tests. Even for one-line fixes.
- No design docs. No review. No archives. Quick means quick.
- **You are the sole implementer with no reviewer.** Be careful.
- **Always update workflow-state.md after each phase.**
