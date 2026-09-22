import json
import re
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent

SKILLS = {
    "feature-dev",
    "bugfix",
    "design",
    "quick-code",
    "code-review",
}

AGENTS = {
    "architect",
    "coder",
    "debugger",
    "reviewer",
}

EXPECTED_ROLES = {
    "feature-dev": {"architect", "coder", "reviewer"},
    "bugfix": {"debugger", "coder"},
    "design": {"architect"},
    "quick-code": set(),
    "code-review": {"reviewer"},
}

EXPECTED_MODELS = {
    "architect": "your-strong-model",
    "coder": "your-efficient-model",
    "debugger": "your-efficient-model",
    "reviewer": "your-strong-model",
}

TRIGGER_WORDS = {
    "feature-dev": ("new feature", "新功能"),
    "bugfix": ("fix bug", "修复"),
    "design": ("design", "设计"),
    "quick-code": ("quick implement", "快速实现"),
    "code-review": ("code review", "代码审查"),
}


def read_text(path):
    return path.read_text(encoding="utf-8-sig")


def parse_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def skill_text(name):
    return read_text(ROOT / "skills" / name / "SKILL.md")


def agent_text(name):
    return read_text(ROOT / "agents" / f"{name}.md")


class InventoryTests(unittest.TestCase):
    def test_exactly_five_skills_are_declared_everywhere(self):
        plugin = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
        plugin_skills = {
            Path(value).name for value in plugin["skills"]
        }
        disk_skills = {
            path.name
            for path in (ROOT / "skills").iterdir()
            if path.is_dir()
        }
        ps1 = read_text(ROOT / "install.ps1")
        sh = read_text(ROOT / "install.sh")

        self.assertEqual(SKILLS, disk_skills)
        self.assertEqual(SKILLS, plugin_skills)
        for skill in SKILLS:
            self.assertIn(skill, ps1)
            self.assertIn(skill, sh)

    def test_four_agent_roles_exist(self):
        disk_agents = {
            path.stem
            for path in (ROOT / "agents").glob("*.md")
        }
        self.assertEqual(AGENTS, disk_agents)

    def test_every_workflow_has_state_reference_and_resume_protocol(self):
        for skill in SKILLS:
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertIn("Resume Protocol", text)
                self.assertIn("workflow-state.md", text)
                self.assertIn("After each phase", text)


class SkillMetadataTests(unittest.TestCase):
    def test_skill_name_matches_directory(self):
        for skill in SKILLS:
            metadata = parse_frontmatter(skill_text(skill))
            with self.subTest(skill=skill):
                self.assertEqual(skill, metadata.get("name"))
                self.assertTrue(metadata.get("description"))

    def test_english_and_chinese_trigger_words_are_declared(self):
        for skill, (english, chinese) in TRIGGER_WORDS.items():
            description = parse_frontmatter(skill_text(skill))["description"]
            with self.subTest(skill=skill):
                self.assertIn(english.lower(), description.lower())
                self.assertIn(chinese, description)

    def test_declared_phase_counts_match_readme(self):
        cases = {
            "feature-dev": 6,
            "bugfix": 4,
            "quick-code": 3,
            "code-review": 3,
        }
        for skill, expected in cases.items():
            text = skill_text(skill)
            phases = re.findall(r"^Phase\s+\d+\s+", text, re.MULTILINE)
            with self.subTest(skill=skill):
                self.assertEqual(expected, len(phases))

    def test_design_has_simple_and_complex_paths(self):
        text = skill_text("design")
        self.assertIn("Simple Mode", text)
        self.assertIn("Complex Mode", text)
        self.assertIn("2-3 approaches", text)

    def test_markdown_has_no_mojibake_markers(self):
        suspicious = re.compile("鈥\\?|\uFFFD")
        for path in ROOT.rglob("*.md"):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertNotRegex(read_text(path), suspicious)


class SubagentAllocationTests(unittest.TestCase):
    def test_role_matrix_is_correct(self):
        for skill, expected in EXPECTED_ROLES.items():
            text = skill_text(skill)
            actual = set()
            for role in AGENTS:
                if (
                    re.search(rf"Dispatch\s+`?{role}`?", text)
                    or re.search(rf"{role}\s+subagent", text)
                ):
                    actual.add(role)
            with self.subTest(skill=skill):
                self.assertEqual(expected, actual)

    def test_quick_code_never_allocates_subagents(self):
        text = skill_text("quick-code")
        self.assertIn("mode=solo", text)
        self.assertIn("no delegation", text)
        self.assertNotIn("Dispatch", text)
        self.assertNotIn("subagent", text)

    def test_every_referenced_role_has_an_agent_file(self):
        referenced = set().union(*EXPECTED_ROLES.values())
        for role in referenced:
            with self.subTest(role=role):
                metadata = parse_frontmatter(agent_text(role))
                self.assertEqual(role, metadata.get("name"))
                self.assertTrue(metadata.get("description"))

    def test_agent_models_match_workflow_assignments(self):
        for role, expected in EXPECTED_MODELS.items():
            metadata = parse_frontmatter(agent_text(role))
            with self.subTest(role=role):
                self.assertEqual(expected, metadata.get("model"))

    def test_skills_define_model_resolution_protocol(self):
        for skill, roles in EXPECTED_ROLES.items():
            if not roles:
                continue
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertIn("Model Resolution Protocol", text)
                self.assertIn("agents/<role>.md", text)
                self.assertIn("extract the `model:` value", text)
                self.assertRegex(
                    text,
                    r"spawn_agent\(role=<role>, model=<resolved model>",
                )

    def test_skills_fail_fast_on_missing_or_placeholder_model(self):
        for skill, roles in EXPECTED_ROLES.items():
            if not roles:
                continue
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertIn("`your-`", text)
                self.assertIn("STOP", text)
                self.assertIn("Do not dispatch", text)
                self.assertIn("Do not substitute a default model", text)

    def test_skills_do_not_hardcode_models_at_dispatch(self):
        for skill in SKILLS:
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertNotRegex(
                    text,
                    r"Dispatch[^\n]*\(model:\s*your-",
                )
                self.assertNotIn("(model: your-", text)
                self.assertNotRegex(
                    text,
                    r"\|\s*(architect|coder|debugger|reviewer)\s*\|\s*your-",
                )

    def test_phase0_prevalidates_all_role_models(self):
        for skill, roles in EXPECTED_ROLES.items():
            if not roles:
                continue
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertIn("Phase 0", text)
                self.assertIn("pre-resolve and validate", text)
                match = re.search(r"workflow uses \(([^)]*)\)", text)
                self.assertIsNotNone(match)
                named = {
                    role.strip() for role in match.group(1).split(",")
                }
                self.assertEqual(set(roles), named)

    def test_role_boundaries_prevent_role_overlap(self):
        boundaries = {
            "architect": ("never writes production code", "DESIGN"),
            "coder": ("Do NOT review your own code", "IMPLEMENT"),
            "debugger": ("Never applies a fix", "DEBUG"),
            "reviewer": ("Do not fix anything", "REVIEW"),
        }
        for role, phrases in boundaries.items():
            text = agent_text(role)
            with self.subTest(role=role):
                for phrase in phrases:
                    self.assertIn(phrase, text)


class RecoverySafetyTests(unittest.TestCase):
    def test_partial_recovery_never_discards_user_work(self):
        for role in AGENTS:
            text = agent_text(role)
            with self.subTest(role=role):
                self.assertNotIn("git checkout --", text)

    def test_task_id_idempotency_requires_exact_bracketed_token(self):
        orchestrator_text = skill_text("feature-dev")
        coder_text = agent_text("coder")
        self.assertRegex(
            orchestrator_text,
            r"git log --oneline --all .*--grep",
        )
        self.assertRegex(
            coder_text,
            r"git log --oneline --all .*--grep",
        )

    def test_resume_mode_has_unavailable_subagent_fallback(self):
        for skill in SKILLS - {"quick-code"}:
            text = skill_text(skill)
            with self.subTest(skill=skill):
                self.assertIn("preserve the original mode", text.lower())
                self.assertIn("subagents are unavailable", text.lower())

    def test_feature_marks_task_completed_only_after_verification(self):
        text = skill_text("feature-dev")
        completed_pos = text.index("If verification passes")
        verify_pos = text.index("Check that the commit exists and tests pass")
        self.assertLess(verify_pos, completed_pos)


class PackagingTests(unittest.TestCase):
    def test_zip_contains_the_complete_source_tree(self):
        archive = WORKSPACE_ROOT / "agent-dev-workflow-v7.zip"
        with zipfile.ZipFile(archive, "r") as bundle:
            names = {
                name[2:] if name.startswith("./") else name
                for name in bundle.namelist()
            }
        required = {
            ".codex-plugin/plugin.json",
            "README.md",
            "README_CN.md",
            "references/workflow-state.md",
            "install.ps1",
            "install.sh",
        }
        for name in required:
            with self.subTest(path=name):
                self.assertIn(name, names)
        for skill in SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f"skills/{skill}/SKILL.md", names)
                self.assertIn(f"skills/{skill}/references/workflow-state.md", names)
        for role in AGENTS:
            with self.subTest(role=role):
                self.assertIn(f"agents/{role}.md", names)

    def test_output_directory_matches_source_contract_files(self):
        output = WORKSPACE_ROOT / "outputs" / "agent-dev-workflow"
        self.assertTrue(output.exists())
        self.assertTrue((output / "README_CN.md").exists())
        self.assertTrue((output / "references" / "workflow-state.md").exists())
        source_plugin = json.loads(read_text(ROOT / ".codex-plugin" / "plugin.json"))
        output_plugin = json.loads(read_text(output / ".codex-plugin" / "plugin.json"))
        self.assertEqual(source_plugin, output_plugin)


class InstalledRuntimeTests(unittest.TestCase):
    CODEX_HOME = Path.home() / ".codex"

    def test_five_skills_and_four_agents_are_installed(self):
        installed_skills = {
            path.name
            for path in (self.CODEX_HOME / "skills").iterdir()
            if path.name in SKILLS and (path / "SKILL.md").exists()
        }
        installed_agents = {
            path.stem
            for path in (self.CODEX_HOME / "agents").glob("*.md")
            if path.stem in AGENTS
        }
        self.assertEqual(SKILLS, installed_skills)
        self.assertEqual(AGENTS, installed_agents)

    def test_installed_models_are_concrete(self):
        for role in AGENTS:
            path = self.CODEX_HOME / "agents" / f"{role}.md"
            metadata = parse_frontmatter(read_text(path))
            with self.subTest(role=role):
                self.assertNotIn("your-", metadata.get("model", ""))
                self.assertTrue(metadata.get("model"))

    def test_installed_partial_recovery_never_discards_user_work(self):
        for role in AGENTS:
            path = self.CODEX_HOME / "agents" / f"{role}.md"
            with self.subTest(role=role):
                self.assertNotIn("git checkout --", read_text(path))

    def test_source_installer_validates_placeholder_models(self):
        ps1 = read_text(ROOT / "install.ps1")
        sh = read_text(ROOT / "install.sh")
        installer = ps1 + sh
        self.assertRegex(installer, r"your-(strong|efficient)-model|placeholder")
        self.assertIn("throw", ps1)
        self.assertIn("exit 1", sh)


if __name__ == "__main__":
    unittest.main()
