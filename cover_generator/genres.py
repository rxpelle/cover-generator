"""Genre-specific design conventions for book covers.

Each genre defines color palettes, font preferences, layout patterns,
and mood keywords that match reader expectations in that category.
"""


GENRE_PROFILES = {
    'thriller': {
        'name': 'Thriller / Suspense',
        'palettes': [
            {'bg': (10, 10, 10), 'primary': (200, 30, 30), 'secondary': (255, 255, 255), 'accent': (200, 168, 78)},
            {'bg': (15, 15, 25), 'primary': (255, 255, 255), 'secondary': (200, 30, 30), 'accent': (180, 180, 180)},
            {'bg': (20, 10, 10), 'primary': (200, 168, 78), 'secondary': (212, 197, 160), 'accent': (200, 30, 30)},
        ],
        'title_weight': 'heavy',
        'title_case': 'upper',
        'preferred_fonts': ['Impact', 'Arial Black', 'Helvetica Bold', 'Georgia Bold'],
        'layout': 'centered',
        'mood_keywords': ['dark', 'tension', 'shadows', 'urban', 'isolated'],
        'dalle_style': 'Dark atmospheric scene, cinematic lighting, dramatic shadows, noir aesthetic',
    },
    'historical': {
        'name': 'Historical Fiction',
        'palettes': [
            {'bg': (25, 20, 15), 'primary': (200, 168, 78), 'secondary': (212, 197, 160), 'accent': (140, 100, 50)},
            {'bg': (10, 10, 10), 'primary': (255, 255, 255), 'secondary': (200, 180, 140), 'accent': (200, 168, 78)},
            {'bg': (15, 10, 10), 'primary': (255, 255, 255), 'secondary': (200, 168, 78), 'accent': (200, 40, 40)},
        ],
        'title_weight': 'medium',
        'title_case': 'upper',
        'preferred_fonts': ['Georgia Bold', 'Garamond Bold', 'Palatino Bold'],
        'layout': 'centered',
        'mood_keywords': ['antiqued', 'textured', 'parchment', 'aged', 'architectural'],
        'dalle_style': 'Historical atmospheric scene, aged textures, warm muted tones, painterly quality',
    },
    'scifi': {
        'name': 'Science Fiction',
        'palettes': [
            {'bg': (5, 10, 25), 'primary': (0, 180, 255), 'secondary': (255, 255, 255), 'accent': (0, 255, 180)},
            {'bg': (10, 5, 20), 'primary': (180, 100, 255), 'secondary': (200, 200, 220), 'accent': (0, 200, 255)},
            {'bg': (0, 0, 0), 'primary': (255, 255, 255), 'secondary': (0, 180, 255), 'accent': (255, 100, 50)},
        ],
        'title_weight': 'heavy',
        'title_case': 'upper',
        'preferred_fonts': ['Helvetica Bold', 'Arial Black', 'Futura Bold'],
        'layout': 'centered',
        'mood_keywords': ['space', 'futuristic', 'technology', 'cosmic', 'neon'],
        'dalle_style': 'Futuristic scene, sci-fi atmosphere, dramatic cosmic lighting, sleek technology',
    },
    'mystery': {
        'name': 'Mystery / Crime',
        'palettes': [
            {'bg': (20, 20, 30), 'primary': (255, 255, 255), 'secondary': (200, 30, 30), 'accent': (150, 150, 170)},
            {'bg': (10, 15, 10), 'primary': (255, 220, 100), 'secondary': (200, 200, 200), 'accent': (100, 150, 100)},
            {'bg': (25, 15, 15), 'primary': (255, 255, 255), 'secondary': (200, 168, 78), 'accent': (180, 50, 50)},
        ],
        'title_weight': 'heavy',
        'title_case': 'upper',
        'preferred_fonts': ['Georgia Bold', 'Impact', 'Helvetica Bold'],
        'layout': 'centered',
        'mood_keywords': ['fog', 'shadows', 'silhouette', 'rain', 'night'],
        'dalle_style': 'Noir atmosphere, fog and shadows, mysterious silhouettes, moody lighting',
    },
    'literary': {
        'name': 'Literary Fiction',
        'palettes': [
            {'bg': (245, 240, 230), 'primary': (30, 30, 30), 'secondary': (100, 80, 60), 'accent': (180, 50, 50)},
            {'bg': (30, 40, 50), 'primary': (240, 235, 220), 'secondary': (180, 170, 150), 'accent': (200, 100, 80)},
            {'bg': (240, 230, 210), 'primary': (40, 40, 40), 'secondary': (120, 100, 80), 'accent': (60, 100, 140)},
        ],
        'title_weight': 'medium',
        'title_case': 'title',
        'preferred_fonts': ['Garamond Bold', 'Georgia Bold', 'Palatino Bold'],
        'layout': 'centered',
        'mood_keywords': ['minimalist', 'elegant', 'textured', 'abstract', 'muted'],
        'dalle_style': 'Minimalist artistic scene, muted palette, elegant composition, painterly texture',
    },
    'romance': {
        'name': 'Romance',
        'palettes': [
            {'bg': (25, 15, 20), 'primary': (255, 180, 200), 'secondary': (255, 255, 255), 'accent': (200, 100, 130)},
            {'bg': (240, 230, 235), 'primary': (80, 20, 40), 'secondary': (150, 80, 100), 'accent': (200, 150, 170)},
            {'bg': (20, 20, 35), 'primary': (200, 168, 78), 'secondary': (220, 200, 180), 'accent': (180, 60, 80)},
        ],
        'title_weight': 'medium',
        'title_case': 'title',
        'preferred_fonts': ['Georgia Bold', 'Garamond Bold', 'Palatino Bold'],
        'layout': 'centered',
        'mood_keywords': ['warm', 'intimate', 'sunset', 'flowers', 'soft focus'],
        'dalle_style': 'Romantic atmospheric scene, warm lighting, soft focus, intimate mood',
    },
    'fantasy': {
        'name': 'Fantasy',
        'palettes': [
            {'bg': (15, 10, 25), 'primary': (200, 168, 78), 'secondary': (180, 160, 200), 'accent': (100, 200, 150)},
            {'bg': (10, 20, 15), 'primary': (220, 200, 140), 'secondary': (200, 200, 220), 'accent': (100, 180, 120)},
            {'bg': (20, 15, 10), 'primary': (200, 180, 140), 'secondary': (255, 255, 255), 'accent': (200, 100, 50)},
        ],
        'title_weight': 'heavy',
        'title_case': 'upper',
        'preferred_fonts': ['Georgia Bold', 'Garamond Bold', 'Palatino Bold'],
        'layout': 'centered',
        'mood_keywords': ['magical', 'epic', 'ancient', 'mystical', 'enchanted'],
        'dalle_style': 'Epic fantasy scene, magical atmosphere, dramatic landscape, rich detail',
    },
    'horror': {
        'name': 'Horror',
        'palettes': [
            {'bg': (0, 0, 0), 'primary': (200, 30, 30), 'secondary': (255, 255, 255), 'accent': (100, 0, 0)},
            {'bg': (10, 10, 10), 'primary': (255, 255, 255), 'secondary': (180, 0, 0), 'accent': (80, 80, 80)},
            {'bg': (15, 10, 10), 'primary': (200, 200, 200), 'secondary': (200, 30, 30), 'accent': (100, 80, 80)},
        ],
        'title_weight': 'heavy',
        'title_case': 'upper',
        'preferred_fonts': ['Impact', 'Arial Black', 'Helvetica Bold'],
        'layout': 'centered',
        'mood_keywords': ['dark', 'decay', 'isolated', 'dread', 'distorted'],
        'dalle_style': 'Dark horror scene, unsettling atmosphere, deep shadows, dread',
    },
}


def get_genre(name):
    """Get genre profile by name (case-insensitive, partial match)."""
    name_lower = name.lower().strip()
    # Direct match
    if name_lower in GENRE_PROFILES:
        return GENRE_PROFILES[name_lower]
    # Partial match
    for key, profile in GENRE_PROFILES.items():
        if name_lower in key or name_lower in profile['name'].lower():
            return profile
    return None


def list_genres():
    """Return list of available genre names."""
    return [(k, v['name']) for k, v in GENRE_PROFILES.items()]
