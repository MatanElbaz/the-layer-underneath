"""
Checks that need no model and no network. They keep the saved fixtures, the scripts and the docs consistent with
agent.py. They do not run the demo itself: that needs Ollama and a 13 GB model (see docs/walkthrough.md).
"""
import ast
import py_compile
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEBREW = re.compile("[֐-׿]")
TEXT_SUFFIXES = {".py", ".md", ".txt", ".sh", ".yml", ".yaml", ".json", ""}


def required_pages():
    """REQUIRED from agent.py, read without running the file"""
    for node in ast.parse((ROOT / "agent.py").read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REQUIRED" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("REQUIRED not found in agent.py")


def run_spec(fit_path):
    return subprocess.run([sys.executable, "-I", str(ROOT / "fixtures" / "test_fit.py"), str(fit_path)],
                          capture_output=True, text=True, timeout=60)


class FixturesMatchTheHarness(unittest.TestCase):
    def test_fallback_wiki_has_every_page_the_ingest_check_requires(self):
        for page in required_pages():
            f = ROOT / "fixtures" / "fallback-wiki" / page
            self.assertTrue(f.exists(), f"missing fixtures/fallback-wiki/{page}")
            self.assertIn("## Facts", f.read_text(encoding="utf-8"), f"{page} has no '## Facts' list")

    def test_every_required_page_is_named_in_the_rules(self):
        rules = (ROOT / "template" / "AGENTS.md").read_text(encoding="utf-8")
        for page in required_pages():
            self.assertIn(f"wiki/{page}", rules, f"AGENTS.md does not mention wiki/{page}")

    def test_rules_have_the_four_workflows(self):
        rules = (ROOT / "template" / "AGENTS.md").read_text(encoding="utf-8")
        for heading in ("## Ingest", "## Query", "## Lint", "## Code"):
            self.assertIn(heading, rules)

    def test_fallback_code_passes_the_spec(self):
        r = run_spec(ROOT / "fixtures" / "fallback-code" / "fit.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_spec_rejects_a_wrong_number(self):
        good = (ROOT / "fixtures" / "fallback-code" / "fit.py").read_text(encoding="utf-8")
        self.assertIn("'gpt-oss-20b': 13", good)
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "fit.py"
            bad.write_text(good.replace("'gpt-oss-20b': 13", "'gpt-oss-20b': 32"), encoding="utf-8")
            self.assertNotEqual(run_spec(bad).returncode, 0, "the spec accepted a wrong size")

    def test_spec_rejects_code_that_runs_on_import(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "fit.py"
            bad.write_text("import sys\nMODELS = {}\nprint(int(sys.argv[1]))\n", encoding="utf-8")
            self.assertNotEqual(run_spec(bad).returncode, 0)

    def test_the_forum_post_says_it_is_fictional(self):
        self.assertIn("FICTIONAL", (ROOT / "fixtures" / "04-forum-post.md").read_text(encoding="utf-8"))


class ScriptsParse(unittest.TestCase):
    def test_agent_compiles(self):
        with tempfile.TemporaryDirectory() as d:
            py_compile.compile(str(ROOT / "agent.py"), cfile=str(Path(d) / "agent.pyc"), doraise=True)

    def test_setup_script_is_valid_bash(self):
        r = subprocess.run(["bash", "-n", str(ROOT / "setup.sh")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_agent_refuses_to_start_without_a_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(ROOT / "agent.py"), d], capture_output=True, text=True, timeout=30)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("setup.sh", r.stdout + r.stderr)


class RepositoryRules(unittest.TestCase):
    def test_everything_is_in_english(self):
        bad = []
        for f in ROOT.rglob("*"):
            if not f.is_file() or ".git" in f.parts or f.suffix not in TEXT_SUFFIXES or f.name == ".DS_Store":
                continue
            if f.resolve() == Path(__file__).resolve():
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if HEBREW.search(text):
                bad.append(str(f.relative_to(ROOT)))
        self.assertEqual(bad, [], f"Hebrew text found in: {bad}")

    def test_agent_uses_the_standard_library_only(self):
        tree = ast.parse((ROOT / "agent.py").read_text(encoding="utf-8"))
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        self.assertLessEqual(mods, set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else mods)
        self.assertFalse(mods & {"requests", "ollama", "openai", "numpy"}, f"third-party import: {mods}")


if __name__ == "__main__":
    unittest.main()
