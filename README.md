# Agent Dev Workflow

English | [中文](README_CN.md)

Multi-agent development workflows for [Codex](https://codex.openai.com/). Five composable skills with role-isolated sub-agent delegation: an orchestrator coordinates, an architect designs, a coder implements, and a reviewer reviews. No agent ever reviews its own work.

## Why

When a single AI agent designs, implements, and reviews its own code, it has a blind spot: it cannot catch its own mistakes with fresh eyes. This project solves that by splitting development into phases and assigning each phase to a different agent with a different model, so design, implementation, and review are always independent.

## What's Included

### 5 Workflow Skills

| Skill | Phases | Agents Involved | User Checkpoints | When to Use |
|-------|--------|-----------------|-----------------|-------------|
| `feature-dev` | Coordinate, Design, Implement, Test, Review, Archive | architect, coder, reviewer | Phase 0, Phase 1 | New features, refactoring (3+ files) |
| `bugfix` | Coordinate, Locate & Fix, Verify, Complete | debugger, coder | Phase 0 | Bug fixes with unknown root cause |
| `design` | Coordinate, (Proposal), Design, Confirm | architect | Each confirm | Design before code; simple or complex mode |
| `quick-code` | Coordinate, Implement, Complete | orchestrator only | None | Trivial changes (1-2 files, mechanical) |
| `code-review` | Coordinate, Review, Complete | reviewer | None | Standalone review of any diff |

### 4 Sub-Agent Roles

| Agent | Role | What It Does | What It Never Does |
|-------|------|--------------|-------------------|
| `architect` | Designer | Reads codebase, proposes architecture, writes implementation plan with Task IDs | Never writes production code |
| `coder` | Implementer | Implements one task, runs tests, commits with Task ID | Never reviews its own code |
| `debugger` | Investigator | Traces code paths, finds root cause, writes evidence | Never applies a fix |
| `reviewer` | Quality gate | Reviews diff for correctness, security, regressions | Never writes code, never sees implementation session |

## Architecture

```
User
  |
  v
Orchestrator (main Codex agent)
  |--- dispatches ---> architect (design phase)
  |--- dispatches ---> coder (implement phase, one per task)
  |--- dispatches ---> debugger (bug locate phase)
  |--- dispatches ---> reviewer (review phase)
  |
  v
Project files + git commits (ground truth)
``+
### Key Design Decisions

- **Pure Markdown, zero runtime dependencies.** Skills are `.md` files read by Codex's skill system. No npm packages, no scripts, no databases.
- **Git log as idempotency key.** Each coder commit includes a Task ID (`[T1]: description`). On resume after interruption, the orchestrator checks `git log` to skip already-completed tasks.
- **State file for resume.** `docs/progress/workflow-state.md` tracks phase + sub-task level status. Survives model stream interruptions and context compaction.
- **Graceful degradation.** If sub-agents are unavailable (e.g. CLI without delegation support), every workflow falls back to solo mode and completes end-to-end.
- **Model assignment per role.** Each subagent's model is resolved from `agents/<role>.md` frontmatter at dispatch time, never hardcoded in the skill. Strong models handle design and review; efficient models handle implementation.

## Install

### Option A: Manual copy

Copy the contents of this repo into your Codex home:

```bash
# Clone
git clone https://github.com/ian-years/agent-dev-workflow.git
cd agent-dev-workflow

# Copy skills
cp -r skills/* ~/.codex/skills/

# Copy agents
cp -r agents/* ~/.codex/agents/
```

### Option B: Windows PowerShell

```powershell
git clone https://github.com/ian-years/agent-dev-workflow.git
cd agent-dev-workflow
Copy-Item -Path skills\* -Destination "$env:USERPROFILE\.codex\skills\" -Recurse -Force
Copy-Item -Path agents\* -Destination "$env:USERPROFILE\.codex\agents\" -Recurse -Force
```

After install, restart Codex or start a new conversation. The skills auto-trigger based on your request keywords.

## Configure Models

Each agent has a `model:` field in its frontmatter. Edit the files to match your available models. This file is the single source of truth: every workflow reads it at Phase 0 and before each dispatch, and stops with a clear error if a value is missing or still a placeholder (`your-`).

| File | Role | Default Placeholder | Suggested Model Tier |
|------|------|---------------------|----------------------|
| `agents/architect.md` | Design | `your-strong-model` | Strongest reasoning model |
| `agents/coder.md` | Implementation | `your-efficient-model` | Efficient coding model |
| `agents/debugger.md` | Debugging | `your-efficient-model` | Efficient coding model |
| `agents/reviewer.md` | Review | `your-strong-model` | Strongest reasoning model |

Replace `your-strong-model` and `your-efficient-model` with your actual model identifiers. The rationale: design and review need deep reasoning (worth the token cost), while implementation and debugging are execution-heavy (efficient models suffice).

Example configuration:

```yaml
# agents/architect.md frontmatter
---
name: architect
model: gpt-4o
description: ...
---
```

```yaml
# agents/coder.md frontmatter
---
name: coder
model: gpt-4o-mini
description: ...
---
```

## Usage

Just talk to Codex naturally. The skills trigger on keywords.

### New Feature
``+> I want to build a user authentication system with OAuth
```
Codex triggers `feature-dev` workflow (6 phases). You confirm scope at Phase 0 and approve design at Phase 1. Phases 2-5 run automatically with multi-agent delegation.

### Bug Fix
```
> Fix a bug: the login button throws a 500 error when the password contains special characters
```
Codex triggers `bugfix` workflow. Debugger traces the root cause, coder applies the fix.

### Design Only
```
> Help me design a caching layer for our API
```
Codex triggers `design` workflow. No code is written. You get a design document with options and trade-offs.

### Quick Change
```
> Add a `phone` field to the User model
```
Codex triggers `quick-code` workflow. Fast, no review, for trivial changes.

### Code Review
```
> Review my recent changes from the last 3 days
```
Codex triggers `code-review` workflow. Independent reviewer sees only the diff.

### Resume After Interruption
```
> Continue the unfinished work
```
Codex reads `docs/progress/workflow-state.md`, resumes at the correct phase, preserves multi-agent mode, and skips already-completed sub-tasks via git log Task ID check.

## How It Works: Consistency Mechanisms

This system addresses the classic multi-agent consistency challenges:

| Challenge | Solution |
|-----------|----------|
| Task semantic overlap (duplicate execution) | Architect assigns Task IDs with affected files AND functions/classes. Overlapping tasks must be sequential. |
| Retry after partial failure (duplicate commits) | Coder checks `git log` for its Task ID before starting. If found, skips. |
| Interruption mid-task (uncommitted changes) | Coder checks `git status` for partial work. Continues or discards based on assessment. |
| Orchestrator crash (state loss) | `workflow-state.md` persists phase + sub-task status. Git log is ground truth. |
| Sub-agent unavailable | Graceful degradation to solo mode. Workflow never blocks. |

## Project Structure

```
agent-dev-workflow/
  .codex-plugin/
    plugin.json              # Codex plugin manifest
  agents/
    architect.md             # Designer agent (strong model)
    coder.md                 # Implementer agent (efficient model)
    debugger.md              # Bug investigator agent (efficient model)
    reviewer.md              # Independent reviewer agent (strong model)
  skills/
    feature-dev/
      SKILL.md               # 6-phase feature development workflow
      references/
        workflow-state.md    # State persistence & resume protocol
    bugfix/
      SKILL.md               # 4-phase bug fix workflow
      references/
        workflow-state.md
    design/
      SKILL.md               # Design workflow (simple/complex modes)
      references/
        workflow-state.md
    quick-code/
      SKILL.md               # 3-phase quick implementation
      references/
        workflow-state.md
    code-review/
      SKILL.md               # 3-phase standalone review
      references/
        workflow-state.md
  templates/
    feature-plan.md           # Design document template
    bug-report.md            # Bug report template
    review-report.md         # Review report template
    workflow-state.md        # State file template
  references/
    workflow-state.md        # Shared state persistence protocol
  AGENTS.md                  # Project-level agent instructions
  README.md
  LICENSE
```

## Requirements

- [Codex](https://codex.openai.com/) (desktop app or CLI with sub-agent support)
- Git (for idempotency and state tracking)
- Any codebase (the workflows are language-agnostic)

## Limitations

- Sub-agent delegation requires Codex desktop or CLI with delegation support. In environments without it, workflows degrade to solo mode (weaker: self-review instead of independent review).
- The `model:` field in agent frontmatter is the source of truth for dispatch. Every workflow resolves it at Phase 0 and before each dispatch, and fails fast if it is missing or still a placeholder. Actual model availability still depends on Codex's delegation implementation.
- State persistence uses a Markdown file, not a database. Suitable for single-developer workflows, not concurrent multi-agent systems.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and pull requests welcome.

## License

[MIT License](LICENSE)
