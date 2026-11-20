"""Tests for the release metadata checker."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "check_release.py"
    spec = importlib.util.spec_from_file_location("check_release", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load()


def _fixture(tmp_path, version="0.1.0"):
    (tmp_path / "CITATION.cff").write_text(
        f"cff-version: 1.2.0\nversion: {version}\n", encoding="utf-8")
    (tmp_path / ".zenodo.json").write_text(
        '{"version": "%s"}' % version, encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## {version} — today\n\n- x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "Fixed 1-5: 2/135. 48/135 is an artefact.\n", encoding="utf-8")
    return tmp_path


def test_consistent_metadata(tmp_path):
    assert checker.check(_fixture(tmp_path)) == []


def test_version_mismatch(tmp_path):
    root = _fixture(tmp_path)
    (root / ".zenodo.json").write_text('{"version": "9.9.9"}', encoding="utf-8")
    problems = checker.check(root)
    assert any("mismatch" in p for p in problems)


def test_missing_changelog_section(tmp_path):
    root = _fixture(tmp_path, version="0.2.0")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n", encoding="utf-8")
    assert any("no section" in p for p in checker.check(root))


def test_readme_headline_required(tmp_path):
    root = _fixture(tmp_path)
    (root / "README.md").write_text("48/135\n", encoding="utf-8")
    assert any("fixed-window" in p for p in checker.check(root))
