# tests/test_plugin_manifests.py
"""CI gate: the plugin + marketplace manifests are valid JSON with the fields
Claude Code requires. Runs in the normal pytest job — no CLI, no auth, no deps."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO / "plugins" / "combined-review"


def _load(rel):
    return json.loads((REPO / rel).read_text())


def test_plugin_manifest_is_valid():
    m = _load("plugins/combined-review/.claude-plugin/plugin.json")
    assert m["name"] == "combined-review"
    assert m["name"].islower() and " " not in m["name"]
    assert isinstance(m.get("version"), str) and m["version"]
    assert isinstance(m.get("description"), str) and m["description"]


def test_marketplace_lists_the_plugin_with_a_resolvable_source():
    mk = _load(".claude-plugin/marketplace.json")
    assert isinstance(mk["name"], str) and mk["name"]
    assert "owner" in mk
    entries = {p["name"]: p for p in mk["plugins"]}
    assert "combined-review" in entries
    src = entries["combined-review"]["source"]
    # relative-path source must start with ./ and point at a real plugin dir
    assert isinstance(src, str) and src.startswith("./")
    target = REPO / src
    assert (target / ".claude-plugin" / "plugin.json").is_file()


def test_skill_is_present_and_namespaced():
    skill = PLUGIN_DIR / "skills" / "review" / "SKILL.md"
    assert skill.is_file(), "skill must live at skills/review/ → /combined-review:review"
    head = skill.read_text()
    assert head.startswith("---"), "SKILL.md needs YAML frontmatter"


def test_skill_has_no_legacy_path_references():
    skill = (PLUGIN_DIR / "skills" / "review" / "SKILL.md").read_text()
    assert "SKILL_DIR" not in skill
    assert ".claude/skills" not in skill


def test_skill_frontmatter_has_required_keys():
    """Shallow gate (no PyYAML): the SKILL.md frontmatter block exists and
    declares the keys the flow depends on. The authoritative check is the
    manual `claude plugin validate --strict`; this catches a frontmatter that
    was dropped or gutted before CI even gets there."""
    skill = (PLUGIN_DIR / "skills" / "review" / "SKILL.md").read_text()
    assert skill.startswith("---\n"), "SKILL.md must open with a YAML frontmatter fence"
    # frontmatter is the block between the first two '---\n' fences
    parts = skill.split("---\n", 2)
    assert len(parts) == 3, "SKILL.md frontmatter must be closed with a '---' fence"
    frontmatter = parts[1]
    for key in ("name:", "description:", "allowed-tools:", "argument-hint:"):
        assert key in frontmatter, f"SKILL.md frontmatter missing {key!r}"
    # the read-only review flow needs exactly these tools allow-listed
    for tool in ("Bash", "Read", "Write", "Task", "Monitor"):
        assert tool in frontmatter, f"allowed-tools should list {tool!r}"
