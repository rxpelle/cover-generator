"""Font discovery and management for cover generation.

Finds system fonts on macOS and maps them to design roles.
"""

import os
from pathlib import Path
from PIL import ImageFont

# macOS font directories
FONT_DIRS = [
    '/System/Library/Fonts',
    '/System/Library/Fonts/Supplemental',
    '/Library/Fonts',
    os.path.expanduser('~/Library/Fonts'),
]

# Font file mapping — name -> (filename_patterns, weight)
# We search for these in order of preference
FONT_MAP = {
    'Georgia Bold': (['Georgia Bold.ttf', 'Georgia-Bold.ttf'], 'bold'),
    'Georgia': (['Georgia.ttf'], 'regular'),
    'Georgia Italic': (['Georgia Italic.ttf', 'Georgia-Italic.ttf'], 'italic'),
    'Impact': (['Impact.ttf'], 'bold'),
    'Arial Black': (['Arial Black.ttf'], 'bold'),
    'Helvetica Bold': (['Helvetica-Bold.ttf', 'HelveticaNeue-Bold.ttf', 'Helvetica Bold.ttf'], 'bold'),
    'Helvetica': (['Helvetica.ttf', 'HelveticaNeue.ttf'], 'regular'),
    'Futura Bold': (['Futura-Bold.ttf', 'Futura Bold.ttf'], 'bold'),
    'Garamond Bold': (['AppleGaramond-Bold.ttf', 'Garamond-Bold.ttf'], 'bold'),
    'Palatino Bold': (['Palatino-Bold.ttf', 'Palatino Bold.ttf'], 'bold'),
    'Palatino': (['Palatino.ttf'], 'regular'),
    'Didot Bold': (['Didot-Bold.ttf', 'Didot Bold.ttf'], 'bold'),
    'Didot': (['Didot.ttf'], 'regular'),
}

_font_cache = {}


def find_font(name):
    """Find a font file path by name. Returns path or None."""
    if name in _font_cache:
        return _font_cache[name]

    patterns = FONT_MAP.get(name, ([name], 'regular'))[0]

    for font_dir in FONT_DIRS:
        for pattern in patterns:
            path = os.path.join(font_dir, pattern)
            if os.path.exists(path):
                _font_cache[name] = path
                return path

    # Fallback: search recursively
    for font_dir in FONT_DIRS:
        if not os.path.isdir(font_dir):
            continue
        for root, _, files in os.walk(font_dir):
            for f in files:
                for pattern in patterns:
                    if f.lower() == pattern.lower():
                        path = os.path.join(root, f)
                        _font_cache[name] = path
                        return path

    _font_cache[name] = None
    return None


def load_font(name, size):
    """Load a PIL ImageFont by name and size. Falls back to Georgia Bold, then default."""
    path = find_font(name)
    if path:
        return ImageFont.truetype(path, size)

    # Fallback chain
    for fallback in ['Georgia Bold', 'Georgia', 'Helvetica Bold', 'Impact']:
        path = find_font(fallback)
        if path:
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def get_best_font(preferred_list):
    """Given a list of font names, return the first one that exists on the system."""
    for name in preferred_list:
        if find_font(name):
            return name
    return 'Georgia Bold'  # safe fallback


def list_available_fonts():
    """Return list of (name, path) for all fonts we can find."""
    available = []
    for name in FONT_MAP:
        path = find_font(name)
        if path:
            available.append((name, path))
    return available
