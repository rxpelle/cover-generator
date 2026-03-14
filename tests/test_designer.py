"""Tests for design parameter generation."""

import pytest
from cover_generator.designer import _default_params
from cover_generator.genres import GENRE_PROFILES


class TestDefaultParams:
    def test_returns_dict(self):
        params = _default_params('Test Title', GENRE_PROFILES['thriller'])
        assert isinstance(params, dict)

    def test_has_required_keys(self):
        params = _default_params('Test Title', GENRE_PROFILES['thriller'])
        required = [
            'palette_index', 'title_font', 'author_font', 'subtitle_font',
            'title_lines', 'title_scale', 'layout_variant',
            'decorative_elements', 'design_rationale',
        ]
        for key in required:
            assert key in params, f"Missing key: {key}"

    def test_title_lines_from_title(self):
        params = _default_params('The First Key', GENRE_PROFILES['thriller'])
        assert params['title_lines'] == ['THE', 'FIRST', 'KEY']

    def test_all_genres_produce_valid_params(self):
        for key, profile in GENRE_PROFILES.items():
            params = _default_params(f'Test {key}', profile)
            assert isinstance(params['title_font'], str)
            assert isinstance(params['title_lines'], list)
            assert len(params['title_lines']) > 0

    def test_palette_index_is_zero(self):
        params = _default_params('Test', GENRE_PROFILES['thriller'])
        assert params['palette_index'] == 0

    def test_title_scale_is_one(self):
        params = _default_params('Test', GENRE_PROFILES['thriller'])
        assert params['title_scale'] == 1.0
