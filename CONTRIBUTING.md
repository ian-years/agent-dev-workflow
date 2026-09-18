# Contributing

Thanks for your interest in improving Agent Dev Workflow. This project is pure Markdown skills and agent definitions for Codex, so contributions are mostly editing `.md` files.

## Ways to Contribute

- **Bug reports**: If a workflow behaves incorrectly (e.g. resume fails, sub-agent delegation breaks), open an issue with the workflow name, phase, and what happened.
- **New workflows**: If you have a development workflow not covered by the existing 5 (e.g. migration, performance audit), propose it in an issue first.
- **Agent improvements**: Better prompts for architect, coder, debugger, or reviewer.
- **Model compatibility**: Test with different model configurations and report what works.
- **Documentation**: README improvements, usage examples, translations.

## How to Contribute

1. Fork the repo.
2. Create a branch: `git checkout -b my-improvement`.
3. Make your changes. Keep edits scoped to the files relevant to your change.
4. Test manually in Codex: trigger the affected workflow and verify it runs end-to-end.
5. If you changed agent prompts, test both multi-agent and solo mode (set `mode: solo` in state file to force solo).
6. Commit with a clear message.
7. Open a PR.

## Guidelines

- **Pure Markdown only.** No scripts, no npm packages, no runtime dependencies. If a feature requires code, it belongs in a separate tool, not in these skills.
- **English for all skill/agent content.** The skills must work for any language project.
- **Keep agent role boundaries strict.** Architect never codes. Coder never reviews. Debugger never fixes. Reviewer never writes code. If you blur these lines, the isolation benefit is lost.
- **Preserve the idempotency contract.** Every coder commit must include a Task ID. Every resume must check git log. If you change the commit format, update all references.
- **Test resume.** After any change to `workflow-state.md` or resume protocol, test by interrupting a workflow mid-phase and resuming.

## Repository Structure

```
skills/     - 5 workflow skills (SKILL.md + references/)
agents/     - 4 sub-agent definitions
templates/  - document templates
references/ - shared protocol docs
```

## License

By contributing, you agree that your contributions are licensed under the MIT License.
