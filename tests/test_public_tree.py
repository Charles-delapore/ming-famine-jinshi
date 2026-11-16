"""Tests for tools/check_public_tree.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "check_public_tree.py"
    spec = importlib.util.spec_from_file_location("check_public_tree", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load()


def test_clean_file(tmp_path):
    path = tmp_path / "clean.md"
    path.write_text("no private content here\n", encoding="utf-8")
    assert checker.check_file(path) == []


def test_absolute_path(tmp_path):
    path = tmp_path / "bad.md"
    path.write_text("raw table at I:\\L\\Work_ming\\raw\\x.xlsx\n", encoding="utf-8")
    problems = checker.check_file(path)
    assert any("absolute path" in p for p in problems)


def test_process_language(tmp_path):
    path = tmp_path / "bad.md"
    path.write_text("Local only; no push\n", encoding="utf-8")
    problems = checker.check_file(path)
    assert any("process language" in p for p in problems)


def test_person_level_csv(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("PersonID,EntryYear\n1,1500\n", encoding="utf-8")
    problems = checker.check_file(path)
    assert any("person-level" in p for p in problems)


def test_blocklisted_name(tmp_path):
    path = tmp_path / "a14_network_edges.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    problems = checker.check_file(path)
    assert any("must not be published" in p for p in problems)
