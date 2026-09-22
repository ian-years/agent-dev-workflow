---
name: feature-dev
description: Feature development & refactoring workflow — 6 phases: coordinate, design, implement, test, review, archive. Uses multi-agent delegation when subagents are available, falls back to solo mode otherwise. Triggers on: new feature, build feature, 新功能, 添加功能, refactor, restructure, 重构, 重写, 改造.
---

# Feature Development & Refactoring Workflow

**Announce at start:** "Starting feature-dev workflow (6 phases)."

## Resume Protocol

**Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.

- **If it exists** and shows this workflow (feature-dev) in progress: Read it. Announce "Resuming feature-dev at Phase [N], [mode] mode." Continue from the recorded phase using the recorded mode. Do NOT restart from Phase 0.
- **On resume, read the sub-task table.** Skip tasks with status `completed`. Re-dispatch tasks with status `dispatched` or `failed`. Dispatch tasks with status `pending`.
- **Preserve the original mode.** If it was multi-agent before interruption, resume in multi-agent mode — dispatch subagents again. Do NOT silently switch to solo mode.

**After each phase AND each sub-task completes**, update `docs/progress/workflow-state.md`.

See `references/workflow-state.md` for the state file format, sub-task tracking, and idempotency protocol.

## Subagent Mode Detection

At the start of Phase 0, detect whether you can dispatch subagents:

- **Multi-agent mode** (subagents available): You coordinate only. architect designs, coder implements, reviewer reviews — each a fresh subagent. No self-review.
- **Solo mode** (no subagents): You do every phase yourself, following the same 6-phase structure. Announce: "Running in solo mode — no subagent delegation available. I'll handle all phases myself. Note: self-review is weaker than independent review."

**Never block the workflow.** If subagents are unavailable, proceed in solo mode.

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
workflow uses (architect, coder, reviewer). If any role fails
validation, stop before Phase 1.

## Phase Flow

```
Phase 0  Coordinate       You + User                 Brief confirmed — PAUSE for user
Phase 1  Design           architect subagent / you   Design doc — PAUSE for user approval
Phase 2  Implement        coder subagent(s) / you     Code written — AUTO PROCEED
Phase 3  Test             Coder + Automation          Tests pass — AUTO PROCEED
Phase 4  Review           reviewer subagent / you    Review report — AUTO PROCEED after fixes
Phase 5  Archive          You                        PR, docs, cleanup — AUTO PROCEED
```

**User checkpoints: Phase 0, Phase 1.** All other transitions automatic.

## Mode Detection (Feature vs Refactor)

At Phase 0, also detect the work type:

- **New feature**: Building something new. Design from scratch.
- **Refactoring**: Restructuring existing code without changing behavior. Map current structure, design incremental migration.

## Phase 0 — Coordinate

**Goal:** Align on scope.

1. Ask the user to describe what they want.
2. Rephrase and confirm scope (IN/OUT).
3. Detect mode (feature vs refactor) and tell the user.
4. **Multi-agent mode only:** Pre-resolve and validate the models for all roles (architect, coder, reviewer) per the Model Resolution Protocol. If any role fails validation, stop before Phase 1.
5. Write a brief to `docs/progress/feature-brief.md`.
6. **Write `docs/progress/workflow-state.md`**: workflow=feature-dev, mode=(multi-agent/solo), phase=0, work type.

**Exit check:** User confirms. Then proceed to Phase 1.

## Phase 1 — Design

**Multi-agent:** Dispatch `architect` subagent (model resolved per the Model Resolution Protocol) with the brief and codebase context. Review its output for completeness.
**Solo:** Read the codebase yourself. Write the design following the architect agent's structure (see `agents/architect.md`).

**Output:** `docs/progress/design.md` — affected modules, data flow, API changes, risk assessment, implementation order with Task IDs.

The design MUST include Task IDs (T1, T2, T3, ...) for each implementation task, with affected files AND functions/classes listed. See `agents/architect.md` for the task format.

**Update `docs/progress/workflow-state.md`**: phase=1 completed, record design doc path, list all task IDs as `pending`.

**Exit check:** User approves. Then proceed to Phase 2.

## Phase 2 — Implement

**Multi-agent:** Dispatch `coder` subagent(s) (model resolved per the Model Resolution Protocol). You do not write code.
**Solo:** Implement the code yourself, following the design. Break into bite-sized tasks. Commit after each with the Task ID.

### Sub-Task Dispatch Protocol

For each task in the design (T1, T2, T3, ...):

1. **Idempotency check**: Before dispatching, run `git log --oneline --all --extended-regexp --grep="^\[T1\]:"`. If the command returns a commit, the task is already done — mark it `completed` in the state file and skip.
2. **Update state file**: Set task status to `dispatched` in `docs/progress/workflow-state.md`.
3. **Dispatch coder**: Send the coder subagent with the Task ID, task description, files, and acceptance criteria.
4. **Coder returns**: The coder checks git log for its Task ID before starting (idempotency). It commits with `[T1]: description`.
5. **Verify**: Check that the commit exists and tests pass for this task.
6. **Update state file**: If verification passes, set task status to `completed` and record the commit hash and files changed. If verification fails, set task status to `failed` and dispatch a fix.

### Parallel vs Sequential

- Tasks marked `Parallelizable: yes` with zero function/class overlap can be dispatched in parallel.
- Tasks with dependencies (e.g., T2 depends on T1) MUST be sequential.
- When in doubt, run sequentially. Parallelism is an optimization, not a requirement.

### On Resume

If resuming Phase 2 after interruption:
1. Read the sub-task table from `docs/progress/workflow-state.md`.
2. For each task: check `git log` for the Task ID.
3. If commit exists → mark `completed`, skip.
4. If no commit → dispatch the task.
5. This prevents duplicate execution of already-completed tasks.

**Exit check:** All tasks complete, code compiles, existing tests pass. Then proceed to Phase 3.

## Phase 3 — Test

1. Run the full test suite.
2. New features: verify new tests exist and pass.
3. Refactoring: verify all existing tests still pass.
4. If tests fail: multi-agent → dispatch coder (model resolved per the Model Resolution Protocol) to fix; solo → fix yourself. Coder uses the Task ID for the fix commit.

**Update `docs/progress/workflow-state.md`**: phase=3 completed.

**Exit check:** All tests pass. Then proceed to Phase 4.

## Phase 4 — Review

**Multi-agent:** Dispatch `reviewer` subagent (model resolved per the Model Resolution Protocol) with the full diff. The reviewer has fresh context — it sees only the diff, not the implementation session. You do not review yourself.
**Solo:** Review your own diff. Be honest about the limitation — self-review misses things independent review catches. Apply extra scrutiny since there's no second pair of eyes.

**Output:** Review report in `docs/progress/review.md`.

If the reviewer finds issues:
- For Critical/Warning: dispatch coder to fix. Coder commits with the original Task ID + `-fix` suffix: `[T1-fix]: fixed review issue`.
- Update state file with fix commits.

**Exit check:** All Critical issues resolved. Then proceed to Phase 5.

## Phase 5 — Archive

1. Update AGENTS.md if architecture assumptions changed.
2. Create a PR.
3. Archive work docs to `docs/archives/<name>/`.
4. **Delete or mark `docs/progress/workflow-state.md` as completed.**
5. Brief summary to the user.

## Rules

- Never skip Phase 0.
- Never skip Phase 1 for work touching more than 2 files.
- Each phase must pass its exit check before the next begins.
- User checkpoints: Phase 0 and Phase 1 ONLY.
- If new information invalidates the design, go back to Phase 1.
- **Never block because subagents are unavailable.** Always proceed in solo mode.
- **Always update workflow-state.md after each phase AND each sub-task.**
- **On resume, preserve the original mode.** Do NOT silently switch from multi-agent to solo.
- **On resume, skip completed sub-tasks.** Check git log for Task IDs. Do NOT re-dispatch done work.
- **Use the model resolved per the Model Resolution Protocol for each agent.** Do not swap models to save cost.
- **Every coder commit must include the Task ID.** This is the idempotency key.

## Agent References

- `agents/architect.md` — designs with Task IDs and semantic scope boundaries
- `agents/coder.md` — idempotent: checks git log before starting
- `agents/reviewer.md` — reviews, independent of coder and architect

## Templates

See `templates/feature-plan.md` for design document template.
See `templates/workflow-state.md` for state file template.
