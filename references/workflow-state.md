# Workflow State Persistence Protocol

This document defines how workflows persist and resume state across conversation interruptions, with sub-task level tracking for idempotent recovery.

## The Problem

When a conversation is compacted or interrupted, the orchestrator loses context about:
- Which workflow was running
- Which phase it was in
- Whether it was in multi-agent or solo mode
- Which sub-tasks within a phase were already dispatched/completed

Without sub-task tracking, resume causes duplicate execution: the orchestrator re-dispatches tasks that were already done, leading to repeated work, conflicting commits, and wasted tokens.

## State File

Every workflow writes to `docs/progress/workflow-state.md`. This file is the single source of truth.

### Format

```markdown
# Workflow State

- **Workflow**: [feature-dev|bugfix|design|quick-code|code-review]
- **Mode**: [multi-agent|solo]
- **Work type**: [new feature|refactor|bug fix|design|quick code|code review]
- **Current phase**: [N] ([phase name])
- **Started**: [timestamp]

## Completed Phases
- Phase 0 (Coordinate): [one-line result]. See [file path].
- Phase 1 (Design): [one-line result]. See [file path].

## Current Phase Status
- Phase [N] ([name])

### Sub-Tasks
| Task ID | Description | Status | Agent | Commit | Files |
|---------|-------------|--------|-------|--------|-------|
| T1 | [what to do] | completed | coder | abc1234 | src/a.ts, src/b.ts |
| T2 | [what to do] | dispatched | coder | (pending) | src/c.ts |
| T3 | [what to do] | pending | (not dispatched) | | src/d.ts |

## Pending Phases
- Phase [N+1] ([name])

## Key Files
- [document type]: [path or "(not yet created)"]
```

### Sub-Task Status Values

- **pending**: Not yet dispatched. Orchestrator should dispatch this task.
- **dispatched**: Subagent has been sent but has not returned yet. On resume, re-dispatch (the subagent's context is lost).
- **completed**: Subagent returned successfully and committed code. On resume, SKIP this task.
- **failed**: Subagent returned with errors. On resume, re-dispatch with the failure context.

## Write Rules

1. **After each phase completes**, update the phase-level status.
2. **Before dispatching a subagent for a sub-task**, update the state file: set task status to `dispatched`.
3. **After a subagent returns**, update the state file: set task status to `completed` or `failed`, record the commit hash and files changed.
4. The state file must always reflect the CURRENT state, not a plan.
5. On the final phase (Archive/Complete), delete or mark the state file as completed.

## Resume Rules

1. **Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.
2. **If it exists** and shows this workflow in progress:
   - Read it.
   - Announce: "Resuming [workflow] at Phase [N], [mode] mode."
   - **Preserve the original mode.** If it was multi-agent, resume in multi-agent mode.
   - For the current phase, read the sub-task table.
   - **Skip tasks with status `completed`.** Their work is already committed.
   - **Re-dispatch tasks with status `dispatched` or `failed`.** Their context is lost.
   - **Dispatch tasks with status `pending`.**
   - Do NOT restart from Phase 0.
3. **If it does not exist**: Start fresh from Phase 0.

## Idempotency Rules

This is the fix for "retry causes duplicate execution":

1. **Each sub-task has a unique Task ID** (T1, T2, T3, ...) assigned by the architect during design.
2. **Coder commits must include the Task ID** in the commit message: `[T1]: implemented user login`.
3. **Before dispatching a coder for a task**, the orchestrator checks `git log --oneline` for commits containing the Task ID. If found, the task is already done — skip it.
4. **Before starting work**, the coder agent checks `git log --oneline` for its Task ID. If found, report "Task [ID] already completed" and return without doing anything.
5. **If a task was partially done** (some files changed but no commit), the coder should detect the partial state and either continue from where it left off or report the partial state.

## Compensation Rules

If a phase fails partially and the work is inconsistent:

1. The orchestrator can revert specific commits using `git revert <hash>`.
2. The state file records which commits belong to which task, so the orchestrator knows exactly what to revert.
3. After reverting, mark the task status as `pending` in the state file and re-dispatch.
4. Never revert another task's commits to fix a different task's failure.

## Critical Rules

- **On resume, the mode MUST match the original.** Do NOT silently switch from multi-agent to solo.
- **On resume, skip completed sub-tasks.** Do NOT re-dispatch work that is already committed.
- **Task IDs are stable.** T1 is always T1 across interruptions and resumes.
- **Git log is the ground truth for idempotency.** If a commit with the task ID exists, the task is done.
