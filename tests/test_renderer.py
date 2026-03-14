"""Tests for cover rendering."""

import pytest
from PIL import Image
from cover_generator.config import Config
from cover_generator.renderer import (
    render_cover, render_front_only, create_thumbnail,
    _text_size, _fit_font_size, _word_wrap,
)
from cover_generator.fonts import load_font
from cover_generator.designer import _default_params
from cover_generator.genres import GENRE_PROFILES


@pytest.fixture
def sample_book():
    return {
        'title': 'The First Key',
        'subtitle': 'Book Three of The Architecture of Survival',
        'author': 'Randy Pellegrini',
        'series': 'The Architecture of Survival',
        'blurb': (
            'A test blurb for the book. This should be long enough '
            'to wrap across multiple lines on the back cover.'
        ),
    }


@pytest.fixture
def sample_dims():
    return Config.calculate_cover_dimensions('5.5x8.5', 300, 'cream')


@pytest.fixture
def sample_design():
    return _default_params('The First Key', GENRE_PROFILES['thriller'])


class TestTextHelpers:
    def test_text_size(self):
        img = Image.new('RGB', (100, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = load_font('Georgia Bold', 48)
        w, h = _text_size(draw, 'Hello', font)
        assert w > 0
        assert h > 0

    def test_longer_text_wider(self):
        img = Image.new('RGB', (1000, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = load_font('Georgia Bold', 48)
        w1, _ = _text_size(draw, 'Hi', font)
        w2, _ = _text_size(draw, 'Hello World', font)
        assert w2 > w1

    def test_fit_font_size(self):
        img = Image.new('RGB', (1000, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        size = _fit_font_size(draw, 'PROTOCOL', 'Georgia Bold', 500)
        assert 40 <= size <= 280

    def test_fit_font_respects_max_width(self):
        img = Image.new('RGB', (1000, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        size_narrow = _fit_font_size(draw, 'TESTING', 'Georgia Bold', 200)
        size_wide = _fit_font_size(draw, 'TESTING', 'Georgia Bold', 800)
        assert size_narrow <= size_wide

    def test_word_wrap(self):
        img = Image.new('RGB', (1000, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = load_font('Georgia', 36)
        lines = _word_wrap(draw, 'This is a test of word wrapping functionality', font, 200)
        assert len(lines) > 1

    def test_word_wrap_short_text_one_line(self):
        img = Image.new('RGB', (1000, 100))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        font = load_font('Georgia', 24)
        lines = _word_wrap(draw, 'Short', font, 500)
        assert len(lines) == 1


class TestRenderCover:
    def test_renders_without_error(self, sample_book, sample_design, sample_dims):
        cover = render_cover(sample_book, sample_design, sample_dims)
        assert isinstance(cover, Image.Image)

    def test_correct_dimensions(self, sample_book, sample_design, sample_dims):
        cover = render_cover(sample_book, sample_design, sample_dims)
        assert cover.width == sample_dims['width_px']
        assert cover.height == sample_dims['height_px']

    def test_different_genres(self, sample_book, sample_dims):
        for genre in ['thriller', 'historical', 'scifi', 'literary', 'mystery']:
            design = _default_params(sample_book['title'], GENRE_PROFILES[genre])
            cover = render_cover(sample_book, design, sample_dims, genre_name=genre)
            assert isinstance(cover, Image.Image)

    def test_no_blurb(self, sample_design, sample_dims):
        book = {
            'title': 'Test Book',
            'subtitle': '',
            'author': 'Test Author',
            'series': '',
            'blurb': '',
        }
        cover = render_cover(book, sample_design, sample_dims)
        assert isinstance(cover, Image.Image)

    def test_long_title(self, sample_design, sample_dims):
        book = {
            'title': 'The Extremely Long Title That Goes On and On',
            'subtitle': 'A Very Long Subtitle Indeed',
            'author': 'Author Mcauthorface',
            'series': 'The Never Ending Series Book Forty-Seven',
            'blurb': 'A blurb.',
        }
        design = _default_params(book['title'], GENRE_PROFILES['thriller'])
        cover = render_cover(book, design, sample_dims)
        assert isinstance(cover, Image.Image)

    def test_different_page_counts(self, sample_book, sample_design):
        for pages in [100, 200, 400, 600]:
            dims = Config.calculate_cover_dimensions('5.5x8.5', pages, 'cream')
            cover = render_cover(sample_book, sample_design, dims)
            assert isinstance(cover, Image.Image)

    def test_custom_background(self, sample_book, sample_design, sample_dims):
        bg = Image.new('RGB', (800, 600), (50, 50, 100))
        cover = render_cover(
            sample_book, sample_design, sample_dims,
            background_image=bg,
        )
        assert isinstance(cover, Image.Image)


class TestRenderFrontOnly:
    def test_renders_ebook(self, sample_book, sample_design):
        cover = render_front_only(sample_book, sample_design)
        assert isinstance(cover, Image.Image)
        assert cover.width == 1600
        assert cover.height == 2560

    def test_custom_size(self, sample_book, sample_design):
        cover = render_front_only(sample_book, sample_design, width=800, height=1200)
        assert cover.width == 800
        assert cover.height == 1200

    def test_different_genres(self, sample_book):
        for genre in ['thriller', 'romance', 'fantasy', 'horror']:
            design = _default_params(sample_book['title'], GENRE_PROFILES[genre])
            cover = render_front_only(sample_book, design, genre_name=genre)
            assert isinstance(cover, Image.Image)


class TestThumbnail:
    def test_creates_thumbnail(self, sample_book, sample_design):
        cover = render_front_only(sample_book, sample_design)
        thumb = create_thumbnail(cover, size=300)
        assert isinstance(thumb, Image.Image)
        assert max(thumb.width, thumb.height) == 300

    def test_different_sizes(self, sample_book, sample_design):
        cover = render_front_only(sample_book, sample_design)
        for size in [100, 200, 500]:
            thumb = create_thumbnail(cover, size=size)
            assert max(thumb.width, thumb.height) == size


class TestAllPalettes:
    """Ensure every genre/palette combination renders without error."""

    def test_all_genre_palette_combos(self, sample_book, sample_dims):
        for genre_key, profile in GENRE_PROFILES.items():
            for i in range(len(profile['palettes'])):
                design = _default_params(sample_book['title'], profile)
                design['palette_index'] = i
                cover = render_cover(
                    sample_book, design, sample_dims, genre_name=genre_key
                )
                assert isinstance(cover, Image.Image), \
                    f"Failed: {genre_key} palette {i}"
