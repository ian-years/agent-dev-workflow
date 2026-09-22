---
name: code-review
description: Code review — 3 phases: coordinate, review, complete. Dispatches independent reviewer subagent when available, falls back to inline self-review otherwise. Triggers on: review, code review, 审查, 代码审查, 帮我看下代码.
---

# Code Review (Standalone)

**Announce at start:** "Starting code review (3 phases)."

## Resume Protocol

**Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.

- **If it exists** and shows this workflow (code-review) in progress: Read it. Announce "Resuming code-review at Phase [N], [mode] mode." Continue from the recorded phase.
- **If it does not exist**: Start fresh from Phase 0.

**After each phase completes**, update `docs/progress/workflow-state.md`.

**On resume, preserve the original mode.** If it was multi-agent, dispatch reviewer subagent again.

See `references/workflow-state.md` for the state file format and detailed protocol.

## Subagent Mode Detection

- **Multi-agent mode**: Dispatch `reviewer` subagent with fresh context. It sees only the diff — no knowledge of implementation history.
- **Solo mode**: Review the diff inline yourself. Announce: "Running in solo mode — self-review. Be aware this is weaker than independent review."

**Never block.** If subagents are unavailable, review inline yourself.

## Model Resolution Protocol

The model for every subagent comes from `agents/<role>.md` — never from
this document. Before dispatching any subagent:

1. Read `agents/<role>.md` and extract the `model:` value from its
   frontmatter.
2. Validate: the value must be non-empty and must not contain `your-`
   (placeholder). If invalid, STOP: report "Agent '<role>' has no
   concrete model (found: '<value>'). Set model: in agents/<role>.md
   and retry." Do not dispatch. Do not substitute a default model.
3. Dispatch with the resolved value passed explicitly:
   spawn_agent(role=<role>, model=<resolved model>, prompt=...)

At Phase 0, pre-resolve and validate the models for ALL roles this
workflow uses (reviewer). If any role fails validation, stop before
Phase 1.

```
Phase 0  Coordinate       You + User                 Target confirmed — AUTO PROCEED
Phase 1  Review           reviewer subagent / you    Findings report — AUTO PROCEED
Phase 2  Complete         You                        Delivered, archived — AUTO PROCEED
```

## Phase 0 — Coordinate

1. Determine the review target: uncommitted changes, recent commits (default 3 days), or branch diff.
2. If "review everything" on a 50-file diff, suggest narrowing.
3. **Multi-agent mode only:** Pre-resolve and validate the models for all roles (reviewer) per the Model Resolution Protocol. If any role fails validation, stop before Phase 1.
4. **Write `docs/progress/workflow-state.md`**: workflow=code-review, mode, phase=0, target.
5. Confirm and proceed immediately.

## Phase 1 — Review

**Multi-agent:** Dispatch `reviewer` subagent (model resolved per the Model Resolution Protocol) with ONLY the diff and project conventions. Do not provide implementation context — the reviewer judges code as-is.
**Solo:** Collect the diff yourself. Review in priority order: correctness, regression risk, security, performance, test coverage, style. Apply extra scrutiny since there's no second pair of eyes.

**Output:** `docs/progress/review.md` — findings with file:line references and severity (Critical / Warning / Suggestion).

**Update `docs/progress/workflow-state.md`**: phase=1 completed, record findings count.

## Phase 2 — Complete

1. Summarize: N critical, N warning, N suggestion.
2. Archive to `docs/archives/reviews/<date>-<target>/`.
3. **Delete or mark `docs/progress/workflow-state.md` as completed.**
4. If user wants to act on findings, offer transition to `feature-dev` or `bugfix`.

## Rules

- Every finding must reference a specific file and line.
- Findings only, no compliments.
- If no issues found, say so in one sentence.
- Never flag style preferences as bugs.
- **Never block because subagents are unavailable.** Always review inline in solo mode.
- **Always update workflow-state.md after each phase.**
- **On resume, preserve the original mode.**
- **Use the model resolved per the Model Resolution Protocol for each agent.**
