"""AI-powered design parameter selection.

Uses Claude to choose genre-appropriate colors, fonts, and layout
for a given book's title, genre, and description.
"""

import json
import logging
from anthropic import Anthropic
from .config import Config
from .genres import get_genre, GENRE_PROFILES
from .fonts import get_best_font, list_available_fonts

logger = logging.getLogger(__name__)

DESIGN_PROMPT = """You are a professional book cover designer who specializes in Amazon Kindle bestsellers.
Your covers MUST work at thumbnail size (100px wide on Amazon search results).

CRITICAL AMAZON COVER RULES:
1. Title must be readable at THUMBNAIL SIZE — massive, bold, high-contrast
2. Maximum 2-3 title lines. Fewer words per line = bigger type = more readable
3. Background must be simple and atmospheric — ONE strong mood, not cluttered
4. Text needs EXTREME contrast against background (white/gold on dark, or dark on light)
5. Cover must POP against Amazon's white page — strong edges, saturated colors
6. Genre signaling in 2 seconds — reader knows thriller/historical/etc instantly
7. Author name clearly visible but secondary to title
8. Subtitle/series line small but legible — don't compete with title
9. DALL-E background: atmospheric, moody, NO text/letters/words, leave clear space for text overlay
10. The background image should enhance mood without competing with typography

Available system fonts: {available_fonts}

Genre profile for {genre}:
- Palettes: {palettes}
- Title weight: {title_weight}
- Title case: {title_case}
- Preferred fonts: {preferred_fonts}
- Mood: {mood_keywords}

Book details:
- Title: {title}
- Subtitle: {subtitle}
- Author: {author}
- Series: {series}
- Description: {description}

Choose design parameters. Return ONLY valid JSON (no markdown, no explanation):
{{
    "palette_index": <0-based index into the genre's palettes list>,
    "title_font": "<exact font name from the available fonts list>",
    "author_font": "<exact font name from the available fonts list>",
    "subtitle_font": "<exact font name from the available fonts list>",
    "title_lines": ["<each word or group on its own line — MAX 3 lines, fewest words possible for HUGE type>"],
    "title_scale": <0.8 to 1.3, go BIG — readable at thumbnail>,
    "layout_variant": "<one of: centered, top-heavy, bottom-heavy>",
    "decorative_elements": ["<zero or more of: divider_line, border, gradient_overlay, text_shadow>"],
    "dalle_prompt": "<DALL-E background scene — atmospheric, period-accurate, NO TEXT/WORDS/LETTERS. Must leave clear dark/light zones at top and bottom for text overlay. Describe the historical setting, lighting, and mood specifically.>",
    "design_rationale": "<one sentence explaining your choices>"
}}"""


def get_design_params(title, subtitle='', author='', series='', genre='thriller', description=''):
    """Use Claude to select design parameters for a cover."""
    genre_profile = get_genre(genre)
    if not genre_profile:
        genre_profile = GENRE_PROFILES['thriller']

    available = [name for name, _ in list_available_fonts()]

    prompt = DESIGN_PROMPT.format(
        available_fonts=', '.join(available),
        genre=genre_profile['name'],
        palettes=json.dumps(genre_profile['palettes']),
        title_weight=genre_profile['title_weight'],
        title_case=genre_profile['title_case'],
        preferred_fonts=genre_profile['preferred_fonts'],
        mood_keywords=genre_profile['mood_keywords'],
        title=title,
        subtitle=subtitle or '(none)',
        author=author,
        series=series or '(none)',
        description=description or '(none)',
    )

    if not Config.has_anthropic_key():
        logger.warning("No Anthropic API key — using default design parameters")
        return _default_params(title, genre_profile)

    client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=Config.MODEL,
        max_tokens=1000,
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]

    try:
        params = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse AI response, using defaults")
        return _default_params(title, genre_profile)

    return params


def _default_params(title, genre_profile):
    """Fallback design parameters when AI is unavailable."""
    words = title.upper().split()
    title_font = get_best_font(genre_profile['preferred_fonts'])

    return {
        'palette_index': 0,
        'title_font': title_font,
        'author_font': title_font,
        'subtitle_font': 'Georgia',
        'title_lines': words,
        'title_scale': 1.0,
        'layout_variant': 'centered',
        'decorative_elements': ['divider_line'],
        'dalle_prompt': '',
        'design_rationale': 'Default parameters based on genre conventions',
    }
