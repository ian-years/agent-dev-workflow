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
workflow uses (architect). If any role fails validation, stop before
Phase 1.

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
3. **Multi-agent mode only:** Pre-resolve and validate the models for all roles (architect) per the Model Resolution Protocol. If any role fails validation, stop before Phase 1.
4. Write `docs/progress/design-brief.md`.
5. **Write `docs/progress/workflow-state.md`**: workflow=design, mode, phase=0, simple/complex.

### Phase 1 — Quick Design
**Multi-agent:** Dispatch `architect` subagent (model resolved per the Model Resolution Protocol) with the brief.
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
**Multi-agent:** Dispatch `architect` subagent (model resolved per the Model Resolution Protocol). It produces 2-3 approaches with pros/cons, effort, risk, recommendation.
**Solo:** Research and write 2-3 approaches yourself.
Output: `docs/progress/proposal.md`.
**Update workflow-state.md**: phase=1 completed.

### Phase 2 — Confirm Direction
Present proposal. Let user choose. Document the chosen direction.
**Update workflow-state.md**: phase=2 completed, record chosen direction.

### Phase 3 — Detailed Design
**Multi-agent:** Dispatch `architect` subagent (model resolved per the Model Resolution Protocol) with the chosen approach.
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
- **Use the model resolved per the Model Resolution Protocol for each agent.**

## Agent References

See `agents/architect.md` for architect behavior spec.
