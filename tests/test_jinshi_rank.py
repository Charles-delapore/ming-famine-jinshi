"""Unit tests for the Jinshi rank normalizer."""

from src.data_processing.jinshi_rank import rank_class, rank_level


def test_arabic_ranks():
    assert rank_class("第1甲第3名") == 1
    assert rank_class("第2甲第26名") == 2
    assert rank_class("第3甲第75名") == 3


def test_chinese_ranks():
    assert rank_class("第一甲第三名") == 1
    assert rank_class("第二甲第二十六名") == 2
    assert rank_class("第三甲第七十五名") == 3


def test_prefix_variants():
    assert rank_class("二甲第10名") == 2
    assert rank_class("三甲第5名") == 3
    assert rank_class("1甲第2名") == 1


def test_unknown_values():
    assert rank_class(None) is None
    assert rank_class("乙榜") is None
    assert rank_class("第1名") is None


def test_rank_level_alias():
    assert rank_level("第一甲第一名") == 1
