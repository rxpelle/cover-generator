"""Tests for font discovery."""

import pytest
from cover_generator.fonts import find_font, load_font, get_best_font, list_available_fonts


class TestFindFont:
    def test_georgia_bold_exists(self):
        path = find_font('Georgia Bold')
        assert path is not None
        assert 'Georgia' in path

    def test_georgia_exists(self):
        path = find_font('Georgia')
        assert path is not None

    def test_nonexistent_font(self):
        path = find_font('NonExistentFont12345')
        assert path is None

    def test_caching(self):
        # Second call should use cache
        path1 = find_font('Georgia Bold')
        path2 = find_font('Georgia Bold')
        assert path1 == path2


class TestLoadFont:
    def test_load_known_font(self):
        font = load_font('Georgia Bold', 48)
        assert font is not None

    def test_load_unknown_falls_back(self):
        font = load_font('NonExistentFont12345', 48)
        assert font is not None  # should fallback

    def test_different_sizes(self):
        small = load_font('Georgia Bold', 24)
        large = load_font('Georgia Bold', 96)
        assert small is not None
        assert large is not None


class TestGetBestFont:
    def test_returns_first_available(self):
        result = get_best_font(['Georgia Bold', 'Impact', 'Arial Black'])
        assert result in ['Georgia Bold', 'Impact', 'Arial Black']

    def test_skips_unavailable(self):
        result = get_best_font(['FakeFont123', 'Georgia Bold'])
        assert result == 'Georgia Bold'

    def test_all_unavailable_returns_fallback(self):
        result = get_best_font(['FakeFont1', 'FakeFont2'])
        assert result == 'Georgia Bold'


class TestListAvailableFonts:
    def test_returns_list(self):
        fonts = list_available_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) >= 1  # at least Georgia should exist

    def test_tuples_of_name_path(self):
        for name, path in list_available_fonts():
            assert isinstance(name, str)
            assert isinstance(path, str)
