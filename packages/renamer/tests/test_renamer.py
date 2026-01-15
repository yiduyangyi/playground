"""Tests for the renamer package."""

import pytest
from renamer.main import rename_file


def test_rename_file_basic():
    """Test basic file renaming."""
    assert rename_file("雍正王朝44.mkv") == "雍正王朝.S01E44.mkv"
    assert rename_file("test123.mkv") == "test.S01E123.mkv"
    assert rename_file("show01.mkv") == "show.S01E01.mkv"


def test_rename_file_no_match():
    """Test files that don't match the pattern."""
    # Should return unchanged
    assert rename_file("movie.mkv") == "movie.mkv"
    assert rename_file("show.S01E01.mkv") == "show.S01E01.mkv"
    assert rename_file("test.txt") == "test.txt"
    assert rename_file("123.mkv") == "123.mkv"


def test_rename_file_edge_cases():
    """Test edge cases."""
    assert rename_file("a1.mkv") == "a.S01E1.mkv"
    assert rename_file("test.123.mkv") == "test.123.mkv"  # Doesn't match pattern
    assert rename_file("") == ""
    assert rename_file("test.mkv") == "test.mkv"


if __name__ == "__main__":
    pytest.main([__file__])