"""Every CSV named in the data dictionary must exist in data/derived."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "data_dictionary.md"
DERIVED = ROOT / "data" / "derived"


def test_dictionary_tables_exist():
    text = DOC.read_text(encoding="utf-8")
    tokens = re.findall(r"`([^`]+\.csv)`", text)
    assert tokens, "no CSV references found in the data dictionary"
    for token in tokens:
        if "*" in token:
            matches = list(DERIVED.glob(token))
            assert matches, f"no file matches {token}"
        else:
            assert (DERIVED / token).exists(), f"missing table: {token}"


def test_dictionary_has_no_private_files():
    text = DOC.read_text(encoding="utf-8")
    for name in ("a14_network_edges.csv", "a18_ego_degrees.csv",
                 "a9_person_addr_link.csv", "a10_coordinate_tiers.csv"):
        assert name not in text or "not published" in text.lower()
