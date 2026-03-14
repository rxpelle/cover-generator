"""Tests for configuration and dimension calculations."""

import pytest
from cover_generator.config import Config


class TestSpineWidth:
    def test_cream_300_pages(self):
        width = Config.calculate_spine_width(300, 'cream')
        assert 0.7 < width < 0.8  # ~0.75"

    def test_cream_200_pages(self):
        width = Config.calculate_spine_width(200, 'cream')
        assert 0.4 < width < 0.6  # ~0.50"

    def test_white_paper_thinner(self):
        cream = Config.calculate_spine_width(300, 'cream')
        white = Config.calculate_spine_width(300, 'white')
        assert white < cream

    def test_color_paper(self):
        color = Config.calculate_spine_width(300, 'color')
        assert color > 0

    def test_zero_pages(self):
        assert Config.calculate_spine_width(0) == 0

    def test_unknown_paper_defaults_cream(self):
        result = Config.calculate_spine_width(300, 'unknown')
        expected = Config.calculate_spine_width(300, 'cream')
        assert result == expected


class TestCoverDimensions:
    def test_standard_5_5x8_5(self):
        dims = Config.calculate_cover_dimensions('5.5x8.5', 300, 'cream')
        assert dims['trim_w_px'] == 1650  # 5.5 * 300
        assert dims['trim_h_px'] == 2550  # 8.5 * 300
        assert dims['bleed_px'] == 37     # 0.125 * 300 (truncated)
        assert dims['spine_w_px'] > 0
        assert dims['width_px'] > dims['trim_w_px'] * 2  # back + front + spine + bleed

    def test_6x9_trim(self):
        dims = Config.calculate_cover_dimensions('6x9', 400, 'cream')
        assert dims['trim_w_px'] == 1800  # 6 * 300
        assert dims['trim_h_px'] == 2700  # 9 * 300

    def test_unknown_trim_defaults(self):
        dims = Config.calculate_cover_dimensions('weird', 300)
        assert dims['trim_w_px'] == 1650  # falls back to 5.5x8.5

    def test_more_pages_wider_spine(self):
        thin = Config.calculate_cover_dimensions('5.5x8.5', 200)
        thick = Config.calculate_cover_dimensions('5.5x8.5', 400)
        assert thick['spine_w_px'] > thin['spine_w_px']

    def test_height_includes_bleed(self):
        dims = Config.calculate_cover_dimensions('5.5x8.5', 300)
        assert dims['height_px'] > dims['trim_h_px']

    def test_dimensions_are_ints(self):
        dims = Config.calculate_cover_dimensions()
        for key in ['width_px', 'height_px', 'trim_w_px', 'trim_h_px', 'spine_w_px', 'bleed_px']:
            assert isinstance(dims[key], int)

    def test_dimensions_include_inches(self):
        dims = Config.calculate_cover_dimensions()
        assert 'total_w_in' in dims
        assert 'total_h_in' in dims
        assert 'spine_w_in' in dims
        assert dims['total_w_in'] > 0
