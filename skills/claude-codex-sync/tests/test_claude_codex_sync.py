from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


CLI_PATH = Path(__file__).resolve().parents[1] / "claude-codex-sync" / "cli.py"
SPEC = importlib.util.spec_from_file_location("claude_codex_sync_cli", CLI_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise ImportError(f"Unable to load CLI module from {CLI_PATH}")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules.setdefault(SPEC.name, MODULE)
SPEC.loader.exec_module(MODULE)

SyncContext = MODULE.SyncContext
apply_plan = MODULE.apply_plan
build_sync_plan = MODULE.build_sync_plan
ensure_codex_fallbacks = MODULE.ensure_codex_fallbacks
parse_frontmatter = MODULE.parse_frontmatter
resolve_repo_root = MODULE.resolve_repo_root
stage_skill_tree = MODULE.stage_skill_tree


class ClaudeCodexSyncTests(unittest.TestCase):
    def test_parse_frontmatter(self) -> None:
        frontmatter, body = parse_frontmatter(
            "---\nname: demo\ndescription: test skill\ndisable-model-invocation: true\n---\n\nhello\n"
        )
        self.assertEqual(frontmatter["name"], "demo")
        self.assertEqual(frontmatter["description"], "test skill")
        self.assertEqual(frontmatter["disable-model-invocation"], "true")
        self.assertIn("hello", body)

    def test_ensure_codex_fallbacks(self) -> None:
        updated = ensure_codex_fallbacks('model = "gpt-5.4"\n')
        self.assertIn('project_doc_fallback_filenames = ["CLAUDE.md"]', updated)
        self.assertIn("project_doc_max_bytes = 65536", updated)

    def test_stage_skill_tree_maps_claude_to_codex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source-skill"
            source.mkdir()
            (source / "SKILL.md").write_text(
                "---\nname: test-skill\ndescription: Test skill\ndisable-model-invocation: true\n---\n\nBody\n",
                encoding="utf-8",
            )
            staged = stage_skill_tree(source, root / "target", "claude", "codex")
            skill_text = (staged / "SKILL.md").read_text(encoding="utf-8")
            openai_yaml = (staged / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn("name: test-skill", skill_text)
            self.assertIn("description: \"Test skill\"", skill_text)
            self.assertIn("allow_implicit_invocation: false", openai_yaml)

    def test_stage_skill_tree_keeps_codex_agents_when_mapping_to_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source-skill"
            (source / "agents").mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: test-skill\ndescription: Test skill\n---\n\nBody\n",
                encoding="utf-8",
            )
            (source / "agents" / "openai.yaml").write_text(
                "interface:\n  default_prompt: \"demo\"\n",
                encoding="utf-8",
            )

            staged = stage_skill_tree(source, root / "target", "codex", "claude")

            self.assertTrue((staged / "agents" / "openai.yaml").exists())

    def test_build_repo_plan_creates_skill_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".git").mkdir()
            (repo / "CLAUDE.md").write_text("Repo instructions\n", encoding="utf-8")
            (repo / ".claude" / "skills" / "demo").mkdir(parents=True)
            (repo / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill\n---\n\nDemo\n",
                encoding="utf-8",
            )
            ctx = SyncContext(cwd=repo, home=repo / "home")
            plan = build_sync_plan(ctx, "claude", "codex", "repo", repo)
            paths = {str(op.path) for op in plan}
            self.assertIn(str(repo / "AGENTS.md"), paths)
            self.assertIn(str(repo / ".agents" / "skills" / "demo"), paths)

    def test_build_user_plan_reads_codex_skills_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            (home / ".codex" / "skills" / "demo").mkdir(parents=True)
            (home / ".codex" / "skills" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill\n---\n\nDemo\n",
                encoding="utf-8",
            )
            ctx = SyncContext(cwd=home, home=home)

            plan = build_sync_plan(ctx, "codex", "claude", "user", None)

            paths = {str(op.path) for op in plan}
            self.assertIn(str(home / ".claude" / "skills" / "demo"), paths)

    def test_build_user_plan_targets_agents_skills_for_codex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            (home / ".claude" / "skills" / "demo").mkdir(parents=True)
            (home / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill\n---\n\nDemo\n",
                encoding="utf-8",
            )
            ctx = SyncContext(cwd=home, home=home)

            plan = build_sync_plan(ctx, "claude", "codex", "user", None)

            paths = {str(op.path) for op in plan}
            self.assertIn(str(home / ".agents" / "skills" / "demo"), paths)
            self.assertNotIn(str(home / ".codex" / "skills" / "demo"), paths)

    def test_apply_plan_refuses_unmanaged_skill_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".git").mkdir()
            (repo / ".claude" / "skills" / "demo").mkdir(parents=True)
            (repo / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: Demo skill\n---\n\nDemo\n",
                encoding="utf-8",
            )
            (repo / ".agents" / "skills" / "demo").mkdir(parents=True)
            (repo / ".agents" / "skills" / "demo" / "user.txt").write_text("keep me\n", encoding="utf-8")
            ctx = SyncContext(cwd=repo, home=repo / "home")

            plan = build_sync_plan(ctx, "claude", "codex", "repo", repo)

            with self.assertRaises(SystemExit):
                apply_plan(plan, backup_root=repo / "backups", force=False)

            self.assertFalse((repo / ".codex" / "config.toml").exists())
            self.assertTrue((repo / ".agents" / "skills" / "demo" / "user.txt").exists())

    def test_resolve_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            nested = repo / "a" / "b"
            nested.mkdir(parents=True)
            (repo / ".git").mkdir()
            self.assertEqual(resolve_repo_root(nested, None), repo)


if __name__ == "__main__":
    unittest.main()
