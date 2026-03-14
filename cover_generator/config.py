"""Configuration management for Cover Generator."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv


_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / '.env')


class Config:
    """Central configuration for Cover Generator."""

    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    MODEL = os.getenv('COVER_MODEL', 'claude-sonnet-4-20250514')

    # Output
    OUTPUT_DIR = os.getenv('COVER_OUTPUT_DIR', str(_project_root / 'output'))
    DPI = 300

    # KDP Trim Sizes (width x height in inches)
    TRIM_SIZES = {
        '5x8': (5.0, 8.0),
        '5.25x8': (5.25, 8.0),
        '5.5x8.5': (5.5, 8.5),
        '6x9': (6.0, 9.0),
    }
    DEFAULT_TRIM = '5.5x8.5'

    # KDP bleed: 0.125" on all sides
    BLEED = 0.125

    # Spine width per page (inches) — KDP standard for B&W cream paper
    SPINE_PER_PAGE_BW_CREAM = 0.0025
    SPINE_PER_PAGE_BW_WHITE = 0.002252
    SPINE_PER_PAGE_COLOR = 0.002347

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def has_anthropic_key(cls):
        return bool(cls.ANTHROPIC_API_KEY)

    @classmethod
    def has_openai_key(cls):
        return bool(cls.OPENAI_API_KEY)

    @classmethod
    def setup_logging(cls):
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    @classmethod
    def calculate_spine_width(cls, page_count, paper='cream'):
        """Calculate spine width in inches for a given page count."""
        rate = {
            'cream': cls.SPINE_PER_PAGE_BW_CREAM,
            'white': cls.SPINE_PER_PAGE_BW_WHITE,
            'color': cls.SPINE_PER_PAGE_COLOR,
        }.get(paper, cls.SPINE_PER_PAGE_BW_CREAM)
        return page_count * rate

    @classmethod
    def calculate_cover_dimensions(cls, trim='5.5x8.5', page_count=300, paper='cream'):
        """Calculate full cover dimensions in pixels (front + spine + back + bleed)."""
        trim_w, trim_h = cls.TRIM_SIZES.get(trim, cls.TRIM_SIZES[cls.DEFAULT_TRIM])
        spine_w = cls.calculate_spine_width(page_count, paper)
        bleed = cls.BLEED

        total_w = (trim_w + bleed) * 2 + spine_w  # back + front + bleeds
        total_h = trim_h + bleed * 2

        return {
            'width_px': int(total_w * cls.DPI),
            'height_px': int(total_h * cls.DPI),
            'trim_w_px': int(trim_w * cls.DPI),
            'trim_h_px': int(trim_h * cls.DPI),
            'spine_w_px': int(spine_w * cls.DPI),
            'bleed_px': int(bleed * cls.DPI),
            'total_w_in': total_w,
            'total_h_in': total_h,
            'spine_w_in': spine_w,
        }
