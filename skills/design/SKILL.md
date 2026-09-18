---
name: design
description: Technical design workflow — two modes: simple (coordinate → quick design → confirm) or complex (coordinate → proposal → confirm → design → confirm). Dispatches architect subagent when available, falls back to solo mode. No code written. Triggers on: design, architect, 设计, 方案, 怎么设计, 架构.
---

# Design Workflow

**Announce at start:** "Starting design workflow."

## Resume Protocol

**Before starting Phase 0**, check if `docs/progress/workflow-state.md` exists.

- **If it exists** and shows this workflow (design) in progress: Read it. Announce "Resuming design at Phase [N], [mode] mode." Continue from the recorded phase.
- **If it does not exist**: Start fresh from Phase 0.

**After each phase completes**, update `docs/progress/workflow-state.md`.

**On resume, preserve the original mode.** If it was multi-agent, dispatch architect subagent again.

See `references/workflow-state.md` for the state file format and detailed protocol.

## Subagent Mode Detection

- **Multi-agent mode**: Dispatch `architect` subagent for proposals and detailed designs.
- **Solo mode**: Do the design work yourself. Announce: "Running in solo mode — I'll design directly."

**Never block.** If subagents are unavailable, design it yourself.

## Model Assignment

When dispatching the architect subagent in multi-agent mode, use this model:

| Agent | Model | Why |
|-------|-------|-----|
| architect | your-strong-model | Strong reasoning for architecture decisions, trade-off analysis, risk assessment |

Rationale: design is the phase where reasoning quality matters most. A good design prevents rework downstream. The strong model is worth the token cost here because design errors are 10x more expensive to fix in implementation.

## Mode Selection (Simple vs Complex)

At Phase 0, determine complexity:

**Simple** (coordinate → quick design → confirm):
- Touches 1-2 modules with clear boundaries
- No new dependencies or structural decisions

**Complex** (coordinate → proposal → confirm → design → confirm):
- Spans 3+ modules or involves architectural decisions
- User is uncertain about the best approach

Tell the user which mode and why.

## Simple Mode

```
Phase 0  Coordinate       You + User                 Brief confirmed
Phase 1  Quick Design     architect subagent / you   Design doc
Phase 2  Confirm          User                       Approved / revise
```

### Phase 0 — Coordinate
1. Ask: what problem? what context?
2. Assess complexity. Tell the user which mode.
3. Write `docs/progress/design-brief.md`.
4. **Write `docs/progress/workflow-state.md`**: workflow=design, mode, phase=0, simple/complex.

### Phase 1 — Quick Design
**Multi-agent:** Dispatch `architect` subagent (model: your-strong-model) with the brief.
**Solo:** Read relevant code yourself. Write the design.
Output: `docs/progress/design.md`.
**Update workflow-state.md**: phase=1 completed.

### Phase 2 — Confirm
Present to user. Revise if needed. Offer to transition to `feature-dev`.
**Delete or mark `docs/progress/workflow-state.md` as completed.**

## Complex Mode

```
Phase 0  Coordinate       You + User                 Problem brief
Phase 1  Proposal         architect subagent / you   Options + trade-offs
Phase 2  Confirm          User                       Direction chosen
Phase 3  Design           architect subagent / you   Detailed design
Phase 4  Confirm          User                       Approved / revise
```

### Phase 1 — Proposal
**Multi-agent:** Dispatch `architect` subagent (model: your-strong-model). It produces 2-3 approaches with pros/cons, effort, risk, recommendation.
**Solo:** Research and write 2-3 approaches yourself.
Output: `docs/progress/proposal.md`.
**Update workflow-state.md**: phase=1 completed.

### Phase 2 — Confirm Direction
Present proposal. Let user choose. Document the chosen direction.
**Update workflow-state.md**: phase=2 completed, record chosen direction.

### Phase 3 — Detailed Design
**Multi-agent:** Dispatch `architect` subagent (model: your-strong-model) with the chosen approach.
**Solo:** Write the full design yourself.
Output: `docs/progress/design.md`.
**Update workflow-state.md**: phase=3 completed.

### Phase 4 — Confirm Design
Present to user. Revise if needed. Offer to transition to `feature-dev`.
**Delete or mark `docs/progress/workflow-state.md` as completed.**

## Rules

- Never write code in the design workflow. Design only.
- Tell the user why you chose simple vs complex mode.
- Complex mode: always present at least 2 alternatives.
- **Never block because subagents are unavailable.** Always design in solo mode.
- **Always update workflow-state.md after each phase.**
- **On resume, preserve the original mode.**
- **Use the model specified for each agent.**

## Agent References

See `agents/architect.md` (model: your-strong-model) for architect behavior spec.
