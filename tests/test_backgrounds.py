"""Tests for background generation."""

import pytest
from PIL import Image
from cover_generator.backgrounds import (
    create_gradient_background,
    create_solid_background,
    add_vignette,
)


class TestSolidBackground:
    def test_correct_size(self):
        img = create_solid_background(800, 600, (0, 0, 0))
        assert img.size == (800, 600)

    def test_correct_color(self):
        img = create_solid_background(10, 10, (255, 0, 0))
        assert img.getpixel((5, 5)) == (255, 0, 0)

    def test_rgb_mode(self):
        img = create_solid_background(10, 10, (0, 0, 0))
        assert img.mode == 'RGB'


class TestGradientBackground:
    def test_correct_size(self):
        img = create_gradient_background(800, 600, (0, 0, 0), (255, 255, 255))
        assert img.size == (800, 600)

    def test_top_is_top_color(self):
        img = create_gradient_background(100, 100, (255, 0, 0), (0, 0, 255))
        r, g, b = img.getpixel((50, 0))
        assert r > 200  # should be close to red

    def test_bottom_is_bottom_color(self):
        img = create_gradient_background(100, 100, (255, 0, 0), (0, 0, 255))
        r, g, b = img.getpixel((50, 99))
        assert b > 200  # should be close to blue

    def test_middle_is_blended(self):
        img = create_gradient_background(100, 100, (0, 0, 0), (200, 200, 200))
        r, g, b = img.getpixel((50, 50))
        assert 70 < r < 130  # roughly halfway


class TestVignette:
    def test_returns_image(self):
        img = create_solid_background(200, 200, (200, 200, 200))
        result = add_vignette(img, strength=0.4)
        assert isinstance(result, Image.Image)
        assert result.size == (200, 200)

    def test_center_brighter_than_edges(self):
        # Use a larger image so the blur behaves correctly
        img = create_solid_background(1000, 1000, (200, 200, 200))
        result = add_vignette(img, strength=0.5)
        center = sum(result.getpixel((500, 500)))
        corner = sum(result.getpixel((10, 10)))
        assert center >= corner
