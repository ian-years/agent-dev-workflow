---
name: bugfix
description: Bug fix workflow — 4 phases: confirm, locate & fix, verify, complete. Uses debugger+coder subagents when available, falls back to solo mode otherwise. Triggers on: fix bug, bug, 修 bug, 修复, 报错, 异常, crash, error, broken.
---

# Bug Fix Workflow

**Announce at start:** "Starting bugfix workflow (4 phases)."

## Resume Protocol

**Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.

- **If it exists** and shows this workflow (bugfix) in progress: Read it. Announce "Resuming bugfix at Phase [N], [mode] mode." Continue from the recorded phase. Do NOT restart from Phase 0.
- **If it does not exist**: Start fresh from Phase 0.

**After each phase completes**, update `docs/progress/workflow-state.md`: current phase, completed phases, mode (preserve original), key file paths.

**On resume, preserve the original mode.** If it was multi-agent before interruption, resume in multi-agent mode — dispatch debugger/coder subagents again. Do NOT silently switch to solo mode.

See `references/workflow-state.md` for the state file format and detailed protocol.

## Subagent Mode Detection

At Phase 0, detect whether you can dispatch subagents:

- **Multi-agent mode**: debugger finds root cause, coder applies fix — separate agents, no self-fix.
- **Solo mode**: You do everything yourself. Announce: "Running in solo mode — I'll debug and fix myself."

**Never block.** If subagents are unavailable, proceed in solo mode.

For **trivial bugs** (typo, wrong variable name, obvious one-liner): skip delegation entirely in both modes. Fix it yourself and say "This is a trivial fix."

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
workflow uses (debugger, coder). If any role fails validation, stop
before Phase 1.

```
Phase 0  Confirm          You + User                 Bug report — PAUSE for user
Phase 1  Locate & Fix     debugger→coder / you       Root cause + fix — AUTO PROCEED
Phase 2  Verify           You + Automation           Tests pass — AUTO PROCEED
Phase 3  Complete         You                        Commit, archive — AUTO PROCEED
```

**User checkpoint: Phase 0 only.**

## Phase 0 — Confirm

1. Ask: what happened vs what should have happened?
2. Collect: error messages, repro steps, environment.
3. Try to reproduce it yourself.
4. **Multi-agent mode only:** Pre-resolve and validate the models for all roles (debugger, coder) per the Model Resolution Protocol. If any role fails validation, stop before Phase 1.
5. Write `docs/progress/bug-report.md`.
6. **Write `docs/progress/workflow-state.md`**: workflow=bugfix, mode=(multi-agent/solo), phase=0.

**Exit check:** User confirms. Trivial bug → fix yourself, skip to Phase 2. Non-trivial → Phase 1.

## Phase 1 — Locate & Fix

**Multi-agent:** Dispatch `debugger` subagent (model resolved per the Model Resolution Protocol) with the bug report. Debugger finds root cause, writes `docs/progress/root-cause.md`. Then dispatch `coder` subagent (model resolved per the Model Resolution Protocol) with the root cause analysis to apply the minimal fix.
**Solo:** Trace the code path yourself. Find the exact line where behavior diverges. Apply the minimal fix.

**Iron rule:** NO fix without root cause confirmed first.

**Update `docs/progress/workflow-state.md`**: phase=1, record root cause found + fix applied.

**Exit check:** Root cause clear. Fix committed and minimal. Then proceed to Phase 2.

## Phase 2 — Verify

1. Regression test exists and fails before fix, passes after.
2. Run full test suite.
3. Manually verify original repro steps no longer trigger the bug.
4. Check related functionality.

**Update `docs/progress/workflow-state.md`**: phase=2 completed.

**Exit check:** Regression test passes. Full suite green. Then proceed to Phase 3.

## Phase 3 — Complete

1. Commit fix + regression test.
2. If GitHub: reference issue (`Fixes #123`).
3. Archive bug report to `docs/archives/bugs/<id>/`.
4. **Delete or mark `docs/progress/workflow-state.md` as completed.**
5. Summary to user: root cause and what changed.

## Rules

- Never skip Phase 0.
- For non-trivial bugs, prefer multi-agent mode. But never block if unavailable.
- Keep the fix minimal. No "while I'm here" changes.
- Regression test is mandatory.
- User checkpoint at Phase 0 only.
- **Always update workflow-state.md after each phase.**
- **On resume, preserve the original mode.**
- **Use the model resolved per the Model Resolution Protocol for each agent.**

## Agent References

- `agents/debugger.md` — finds root cause, never fixes
- `agents/coder.md` — applies fix, never debugs complex issues
