#!/usr/bin/env bash
# Agent Dev Workflow - Install Script (macOS/Linux)
# Usage: bash install.sh

set -e

SKILLS_DEST="$HOME/.codex/skills"
AGENTS_DEST="$HOME/.codex/agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Agent Dev Workflow..."

# Create directories
mkdir -p "$SKILLS_DEST"
mkdir -p "$AGENTS_DEST"

# Install skills (including references/)
SKILLS=("feature-dev" "bugfix" "code-review" "design" "quick-code")
for skill in "${SKILLS[@]}"; do
    src_dir="$SCRIPT_DIR/skills/$skill"
    dst_dir="$SKILLS_DEST/$skill"
    mkdir -p "$dst_dir"
    cp "$src_dir/SKILL.md" "$dst_dir/SKILL.md"
    # Copy references if they exist
    if [ -d "$src_dir/references" ]; then
        mkdir -p "$dst_dir/references"
        cp "$src_dir/references/"* "$dst_dir/references/"
    fi
    echo "  Skill: $skill installed"
done

# Install agents
AGENTS=("architect" "coder" "debugger" "reviewer")
for agent in "${AGENTS[@]}"; do
    src_file="$SCRIPT_DIR/agents/$agent.md"
    if grep -Eq "your-(strong|efficient)-model" "$src_file"; then
        echo "Agent '$agent' still contains a placeholder model. Replace your-strong-model or your-efficient-model before installing." >&2
        exit 1
    fi
    cp "$src_file" "$AGENTS_DEST/$agent.md"
    echo "  Agent: $agent installed"
done

echo ""
echo "Installation complete!"
echo "Skills installed to: $SKILLS_DEST"
echo "Agents installed to: $AGENTS_DEST"
echo ""
echo "Restart Codex, then try saying:"
echo "  - 'I want to build a new feature: [describe]'"
echo "  - 'Fix a bug: [describe]'"
echo "  - 'Review my recent changes'"
echo "  - 'Help me design a caching solution'"
echo "  - 'Add a phone field to the User model'"
