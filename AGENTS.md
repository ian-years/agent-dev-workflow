# Agent Dev Workflow

## 5 Skills with Multi-Agent Delegation

| Skill | Phases | Who Does What | Autopilot |
|-------|--------|---------------|-----------|
| `feature-dev` | Coordinate -> Design -> Implement -> Test -> Review -> Archive | orchestrator coordinates / architect designs / coder implements / reviewer reviews | Phase 0 and Phase 1 need your confirmation, rest is automatic |
| `bugfix` | Coordinate -> Locate & Fix -> Verify -> Complete | orchestrator coordinates / debugger locates / coder fixes | Phase 0 needs your confirmation |
| `design` | Coordinate -> (Proposal) -> Design -> Confirm | orchestrator coordinates / architect designs | Each confirm point needs you |
| `quick-code` | Coordinate -> Implement -> Complete | orchestrator handles everything (lightweight, no independent review) | Fully automatic |
| `code-review` | Coordinate -> Review -> Complete | reviewer independently reviews | Fully automatic |

## Core Mechanism: Role Isolation

```
You (User) -> Orchestrator (coordinates, never writes production code)
                |-> Architect (designs, never implements)
                |-> Coder (implements, never reviews own code)
                |-> Reviewer (reviews, independent agent, only sees the diff)
```

- **orchestrator never writes production code**
- **coder never reviews their own code**
- **reviewer is an independent agent that only sees the diff, not the implementation session**

## Quick Start

**New feature / refactoring (runs the full 6-phase workflow with multi-agent collaboration):**
> I want to develop a new feature: user permission management
> Refactor this module into a service

**Bug fix (debugger finds root cause -> coder fixes):**
> Fix a bug: the submit button doesn't respond

**Design only (no code written):**
> Help me design a caching solution

**Quick small change (no review, fast):**
> Add a phone field to the User model

**Independent review:**
> Review the recent changes

## Project Structure After Use

- `docs/progress/` - in-progress design docs, bug reports, review reports
- `docs/archives/` - archived work after completion
- `docs/progress/workflow-state.md` - state file for resume after interruptions
