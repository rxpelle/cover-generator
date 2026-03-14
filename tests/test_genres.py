"""Tests for genre profiles."""

import pytest
from cover_generator.genres import get_genre, list_genres, GENRE_PROFILES


class TestGetGenre:
    def test_direct_match(self):
        profile = get_genre('thriller')
        assert profile is not None
        assert profile['name'] == 'Thriller / Suspense'

    def test_case_insensitive(self):
        assert get_genre('THRILLER') is not None
        assert get_genre('Thriller') is not None

    def test_partial_match(self):
        profile = get_genre('sci')
        assert profile is not None
        assert 'Science Fiction' in profile['name']

    def test_unknown_genre(self):
        assert get_genre('underwater-basket-weaving') is None

    def test_all_genres_have_required_keys(self):
        required = ['name', 'palettes', 'title_weight', 'title_case',
                     'preferred_fonts', 'layout', 'mood_keywords', 'dalle_style']
        for key, profile in GENRE_PROFILES.items():
            for req in required:
                assert req in profile, f"Genre '{key}' missing '{req}'"

    def test_all_palettes_have_required_colors(self):
        for key, profile in GENRE_PROFILES.items():
            assert len(profile['palettes']) >= 1
            for i, palette in enumerate(profile['palettes']):
                assert 'bg' in palette, f"Genre '{key}' palette {i} missing 'bg'"
                assert 'primary' in palette, f"Genre '{key}' palette {i} missing 'primary'"
                assert 'secondary' in palette, f"Genre '{key}' palette {i} missing 'secondary'"

    def test_all_colors_are_rgb_tuples(self):
        for key, profile in GENRE_PROFILES.items():
            for palette in profile['palettes']:
                for color_key in ['bg', 'primary', 'secondary']:
                    color = palette[color_key]
                    assert isinstance(color, tuple), f"Genre '{key}' {color_key} not tuple"
                    assert len(color) == 3, f"Genre '{key}' {color_key} not RGB"
                    for c in color:
                        assert 0 <= c <= 255, f"Genre '{key}' {color_key} value {c} out of range"


class TestListGenres:
    def test_returns_list(self):
        genres = list_genres()
        assert isinstance(genres, list)
        assert len(genres) >= 6

    def test_tuples_of_key_name(self):
        for key, name in list_genres():
            assert isinstance(key, str)
            assert isinstance(name, str)
            assert key in GENRE_PROFILES
