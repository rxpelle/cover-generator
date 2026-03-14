"""Core cover rendering engine.

Takes design parameters and generates a KDP-ready cover image
with front, spine, and back panels.
"""

import logging
from PIL import Image, ImageDraw, ImageFilter
from .config import Config
from .fonts import load_font
from .genres import get_genre, GENRE_PROFILES
from .backgrounds import (
    create_gradient_background,
    create_solid_background,
    add_vignette,
    generate_dalle_background,
)

logger = logging.getLogger(__name__)


def _text_size(draw, text, font):
    """Get text width and height."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _center_text(draw, text, font, color, center_x, y, shadow=False, outline=False):
    """Draw centered text with optional drop shadow and outline, return height."""
    w, h = _text_size(draw, text, font)
    x = center_x - w // 2
    if shadow:
        # Heavy black shadow for readability over busy backgrounds
        shadow_color = (0, 0, 0)
        # Multiple passes at increasing offsets for thick shadow
        for offset in range(max(4, h // 12), 0, -1):
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    if outline:
        # Black outline for extra contrast
        outline_w = max(3, h // 25)
        outline_color = (0, 0, 0)
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx * dx + dy * dy <= outline_w * outline_w:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=color)
    return h


def _fit_font_size(draw, text, font_name, max_width, start_size=280, min_size=40):
    """Find the largest font size that fits within max_width."""
    size = start_size
    while size > min_size:
        font = load_font(font_name, size)
        w, _ = _text_size(draw, text, font)
        if w <= max_width:
            return size
        size -= 2
    return min_size


def _word_wrap(draw, text, font, max_width):
    """Wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = f'{current} {word}'.strip()
        w, _ = _text_size(draw, test, font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_front_cover(img, draw, dims, palette, design_params, book):
    """Render the front cover panel."""
    spine_end = dims['bleed_px'] + dims['trim_w_px'] + dims['spine_w_px']
    margin = int(0.5 * Config.DPI)  # 0.5" margin
    fc_left = spine_end + margin
    fc_right = dims['width_px'] - dims['bleed_px'] - margin
    fc_width = fc_right - fc_left
    fc_center = spine_end + (dims['width_px'] - spine_end) // 2

    title_lines = design_params.get('title_lines', book['title'].upper().split())
    title_font_name = design_params.get('title_font', 'Georgia Bold')
    author_font_name = design_params.get('author_font', 'Georgia Bold')
    subtitle_font_name = design_params.get('subtitle_font', 'Georgia')
    title_scale = design_params.get('title_scale', 1.0)
    layout = design_params.get('layout_variant', 'centered')
    decorative = design_params.get('decorative_elements', [])

    primary = tuple(palette['primary'])
    secondary = tuple(palette['secondary'])
    accent = tuple(palette.get('accent', palette['secondary']))

    # Calculate title font sizes — largest line determines base size
    longest_line = max(title_lines, key=len)
    base_size = _fit_font_size(draw, longest_line, title_font_name, fc_width, start_size=300)
    base_size = int(base_size * title_scale)

    # Layout positioning
    if layout == 'top-heavy':
        title_y_start = margin + int(0.3 * Config.DPI)
    elif layout == 'bottom-heavy':
        title_y_start = dims['height_px'] // 3
    else:  # centered
        # Estimate total title height to center vertically
        total_h = 0
        for line in title_lines:
            font = load_font(title_font_name, base_size)
            _, h = _text_size(draw, line, font)
            total_h += h + int(0.1 * Config.DPI)
        title_y_start = (dims['height_px'] - total_h) // 3  # upper third

    use_shadow = 'text_shadow' in decorative

    # Draw title lines
    y = title_y_start
    line_spacing = int(0.12 * Config.DPI)  # ~36px at 300dpi

    for i, line in enumerate(title_lines):
        # Scale down smaller words
        if len(line) <= 3 and len(title_lines) > 1:
            size = int(base_size * 0.55)
        else:
            size = base_size

        font = load_font(title_font_name, size)
        h = _center_text(draw, line, font, primary, fc_center, y, shadow=use_shadow)
        y += h + line_spacing

    # Decorative divider after title
    if 'divider_line' in decorative:
        div_y = y + int(0.15 * Config.DPI)
        line_w = fc_width // 3
        draw.line(
            [(fc_center - line_w // 2, div_y), (fc_center + line_w // 2, div_y)],
            fill=accent,
            width=2,
        )
        y = div_y + int(0.2 * Config.DPI)
    else:
        y += int(0.3 * Config.DPI)

    # Subtitle / series line
    if book.get('subtitle') or book.get('series'):
        sub_text = book.get('subtitle') or book.get('series', '')
        sub_size = max(36, base_size // 4)
        sub_font = load_font(subtitle_font_name, sub_size)
        _center_text(draw, sub_text, sub_font, secondary, fc_center, y, shadow=use_shadow)
        y += sub_size + int(0.1 * Config.DPI)

    # Author name at bottom
    author_size = max(48, base_size // 3)
    author_font = load_font(author_font_name, author_size)
    author_text = book.get('author', '').upper()
    _, ah = _text_size(draw, author_text, author_font)
    author_y = dims['height_px'] - dims['bleed_px'] - margin - ah - int(0.3 * Config.DPI)
    _center_text(draw, author_text, author_font, primary, fc_center, author_y, shadow=use_shadow)

    # Border
    if 'border' in decorative:
        border_margin = int(0.3 * Config.DPI)
        draw.rectangle(
            [
                (spine_end + border_margin, dims['bleed_px'] + border_margin),
                (dims['width_px'] - dims['bleed_px'] - border_margin,
                 dims['height_px'] - dims['bleed_px'] - border_margin),
            ],
            outline=accent,
            width=2,
        )


def render_spine(img, draw, dims, palette, book):
    """Render the spine panel."""
    spine_start = dims['bleed_px'] + dims['trim_w_px']
    spine_w = dims['spine_w_px']
    spine_center = spine_start + spine_w // 2

    if spine_w < 30:
        logger.info("Spine too narrow for text (<0.1\"), skipping")
        return

    primary = tuple(palette['primary'])
    margin = dims['bleed_px'] + int(0.3 * Config.DPI)

    # Find font size that fits spine width
    max_text_w = spine_w - 20  # 10px padding each side
    usable_h = dims['height_px'] - 2 * margin

    title = book.get('title', '').upper()
    author = book.get('author', '').upper()

    # Find common font size for both
    size = 120
    font_name = 'Georgia Bold'
    while size > 12:
        font = load_font(font_name, size)
        tw, th = _text_size(draw, title, font)
        aw, ah = _text_size(draw, author, font)
        if th <= max_text_w and ah <= max_text_w and tw + aw + 40 <= usable_h:
            break
        size -= 2

    size = int(size * 0.8)  # 20% smaller for safety

    for text, is_top in [(title, True), (author, False)]:
        font = load_font(font_name, size)
        tw, th = _text_size(draw, text, font)
        pad = 20
        text_img = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(text_img).text((pad, pad), text, font=font, fill=primary)
        rotated = text_img.rotate(-90, expand=True)

        # Center horizontally on spine
        bbox = rotated.getbbox()
        if bbox:
            content_cx = (bbox[0] + bbox[2]) // 2
            rx = spine_center - content_cx
        else:
            rx = spine_center - rotated.width // 2

        if is_top:
            ry = margin
        else:
            ry = dims['height_px'] - margin - rotated.height

        img.paste(rotated, (rx, ry), rotated)


def render_back_cover(img, draw, dims, palette, book):
    """Render the back cover panel."""
    margin = int(0.5 * Config.DPI)
    bl = dims['bleed_px'] + margin
    br = dims['bleed_px'] + dims['trim_w_px'] - margin
    bw = br - bl
    back_center = dims['bleed_px'] + dims['trim_w_px'] // 2

    primary = tuple(palette['primary'])
    secondary = tuple(palette['secondary'])
    accent = tuple(palette.get('accent', palette['secondary']))

    # ISBN barcode zone (bottom-right, KDP will overlay)
    bcw, bch = 600, 360
    bcx = br - bcw
    bcy = dims['height_px'] - dims['bleed_px'] - margin - bch

    y = dims['bleed_px'] + margin + int(0.3 * Config.DPI)

    # Blurb text
    blurb = book.get('blurb', '')
    if blurb:
        blurb_font = load_font('Georgia', 46)
        paragraphs = blurb.split('\n\n') if '\n\n' in blurb else [blurb]

        for para in paragraphs:
            lines = _word_wrap(draw, para.strip(), blurb_font, bw)
            for line in lines:
                # Avoid barcode zone
                line_w = bw
                if y > bcy and y < bcy + bch:
                    line_w = min(bw, bcx - bl - 30)
                draw.text((bl, y), line, font=blurb_font, fill=secondary)
                _, lh = _text_size(draw, line, blurb_font)
                y += lh + 10
            y += 26  # paragraph spacing

    # Gold divider above barcode zone
    if y < bcy - 60:
        div_y = bcy - 60
        draw.line([(bl, div_y), (br, div_y)], fill=accent, width=2)

    # Series text below divider, left of barcode
    series = book.get('series', '')
    if series:
        small_font = load_font('Georgia', 36)
        small_w = bcx - bl - 40
        series_lines = _word_wrap(draw, series, small_font, small_w)
        sy = bcy + 20
        for line in series_lines:
            draw.text((bl, sy), line, font=small_font, fill=secondary)
            _, lh = _text_size(draw, line, small_font)
            sy += lh + 6


def render_cover(book, design_params, dims, genre_name='thriller',
                 use_dalle=False, background_image=None):
    """Render a complete book cover.

    Args:
        book: dict with title, subtitle, author, series, blurb
        design_params: dict from designer.get_design_params()
        dims: dict from Config.calculate_cover_dimensions()
        genre_name: genre key for palette selection
        use_dalle: whether to attempt DALL-E background generation
        background_image: optional PIL Image to use as background

    Returns:
        PIL Image of the complete cover
    """
    genre_profile = get_genre(genre_name) or GENRE_PROFILES['thriller']
    palette_idx = design_params.get('palette_index', 0)
    palette = genre_profile['palettes'][min(palette_idx, len(genre_profile['palettes']) - 1)]

    bg_color = tuple(palette['bg'])
    width = dims['width_px']
    height = dims['height_px']

    # Create background
    if background_image:
        img = background_image.resize((width, height), Image.LANCZOS)
    elif use_dalle and design_params.get('dalle_prompt'):
        dalle_img = generate_dalle_background(design_params['dalle_prompt'], width, height)
        if dalle_img:
            img = dalle_img
        else:
            # Fallback to gradient
            lighter = tuple(min(255, c + 20) for c in bg_color)
            img = create_gradient_background(width, height, lighter, bg_color)
    else:
        lighter = tuple(min(255, c + 20) for c in bg_color)
        img = create_gradient_background(width, height, lighter, bg_color)

    # Apply vignette for depth
    if 'gradient_overlay' in design_params.get('decorative_elements', []):
        img = add_vignette(img, strength=0.3)

    draw = ImageDraw.Draw(img)

    # Render panels
    render_spine(img, draw, dims, palette, book)
    draw = ImageDraw.Draw(img)  # refresh after spine paste operations

    render_front_cover(img, draw, dims, palette, design_params, book)
    render_back_cover(img, draw, dims, palette, book)

    return img


def _add_text_gradient(img, zone_top, zone_height, opacity=180, from_top=True):
    """Add a dark gradient overlay in a zone to improve text readability."""
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    for i in range(zone_height):
        if from_top:
            y = zone_top + i
            alpha = int(opacity * (1 - i / zone_height) ** 1.5)
        else:
            y = zone_top + zone_height - 1 - i
            alpha = int(opacity * (1 - i / zone_height) ** 1.5)
        if 0 <= y < height:
            draw_ov.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    img_rgba = img.convert('RGBA')
    composited = Image.alpha_composite(img_rgba, overlay)
    return composited.convert('RGB')


def render_front_only(book, design_params, genre_name='thriller',
                      width=1600, height=2560, use_dalle=False):
    """Render just the front cover (for ebook or thumbnail testing).

    Standard ebook cover: 1600x2560 (1:1.6 ratio).
    """
    genre_profile = get_genre(genre_name) or GENRE_PROFILES['thriller']
    palette_idx = design_params.get('palette_index', 0)
    palette = genre_profile['palettes'][min(palette_idx, len(genre_profile['palettes']) - 1)]

    bg_color = tuple(palette['bg'])
    has_dalle_bg = False

    if use_dalle and design_params.get('dalle_prompt'):
        img = generate_dalle_background(design_params['dalle_prompt'], width, height)
        if img:
            has_dalle_bg = True
        else:
            lighter = tuple(min(255, c + 20) for c in bg_color)
            img = create_gradient_background(width, height, lighter, bg_color)
    else:
        lighter = tuple(min(255, c + 20) for c in bg_color)
        img = create_gradient_background(width, height, lighter, bg_color)

    # Add dark gradient overlays for text zones on DALL-E backgrounds
    if has_dalle_bg:
        # Dark gradient from top (title zone) — covers top 55%
        img = _add_text_gradient(img, 0, int(height * 0.55), opacity=220, from_top=True)
        # Dark gradient from bottom (author + subtitle zone) — covers bottom 40%
        # Extended higher and darker to tame busy backgrounds and make author/subtitle readable
        img = _add_text_gradient(img, int(height * 0.60), int(height * 0.40), opacity=240, from_top=False)

    draw = ImageDraw.Draw(img)

    primary = tuple(palette['primary'])
    secondary = tuple(palette['secondary'])
    accent = tuple(palette.get('accent', palette['secondary']))

    title_lines = design_params.get('title_lines', book['title'].upper().split())
    title_font_name = design_params.get('title_font', 'Georgia Bold')
    author_font_name = design_params.get('author_font', 'Georgia Bold')
    subtitle_font_name = design_params.get('subtitle_font', 'Georgia')
    title_scale = design_params.get('title_scale', 1.0)
    decorative = design_params.get('decorative_elements', [])

    # Always use shadow + outline on DALL-E backgrounds for readability
    use_shadow = has_dalle_bg or 'text_shadow' in decorative
    use_outline = has_dalle_bg

    margin = width // 10
    usable_w = width - 2 * margin
    center_x = width // 2

    # Title
    longest = max(title_lines, key=len)
    base_size = _fit_font_size(draw, longest, title_font_name, usable_w, start_size=250)
    base_size = int(base_size * title_scale)

    # Estimate total height to center
    total_h = 0
    for line in title_lines:
        size = int(base_size * 0.55) if len(line) <= 3 and len(title_lines) > 1 else base_size
        font = load_font(title_font_name, size)
        _, h = _text_size(draw, line, font)
        total_h += h + width // 30

    y = (height - total_h) // 3

    for line in title_lines:
        size = int(base_size * 0.55) if len(line) <= 3 and len(title_lines) > 1 else base_size
        font = load_font(title_font_name, size)
        h = _center_text(draw, line, font, primary, center_x, y,
                         shadow=use_shadow, outline=use_outline)
        y += h + width // 30

    # Divider
    if 'divider_line' in decorative:
        div_y = y + margin // 2
        lw = usable_w // 3
        draw.line([(center_x - lw // 2, div_y), (center_x + lw // 2, div_y)], fill=accent, width=2)
        y = div_y + margin // 2
    else:
        y += margin

    # Subtitle / series — sized for readability, word-wrapped within margins
    if book.get('subtitle') or book.get('series'):
        sub_text = book.get('subtitle') or book.get('series', '')
        sub_size = max(44, int(base_size * 0.35))
        sub_font = load_font(subtitle_font_name, sub_size)
        # Word-wrap to fit within usable width (with extra padding)
        sub_max_w = int(usable_w * 0.85)
        sub_lines = _word_wrap(draw, sub_text, sub_font, sub_max_w)
        for sub_line in sub_lines:
            h = _center_text(draw, sub_line, sub_font, secondary, center_x, y,
                             shadow=use_shadow, outline=use_outline)
            y += h + 8

    # Author — sized for thumbnail readability (must be visible at 150px)
    author_size = max(56, int(base_size * 0.45))
    author_font = load_font(author_font_name, author_size)
    author_text = book.get('author', '').upper()
    _, ah = _text_size(draw, author_text, author_font)
    author_y = height - margin - ah - margin
    _center_text(draw, author_text, author_font, primary, center_x, author_y,
                 shadow=use_shadow, outline=use_outline)

    # Border
    if 'border' in decorative:
        bm = margin // 2
        draw.rectangle([(bm, bm), (width - bm, height - bm)], outline=accent, width=2)

    return img


def create_thumbnail(img, size=300):
    """Create a thumbnail preview for readability testing."""
    aspect = img.width / img.height
    if aspect > 1:
        thumb_w = size
        thumb_h = int(size / aspect)
    else:
        thumb_h = size
        thumb_w = int(size * aspect)
    return img.resize((thumb_w, thumb_h), Image.LANCZOS)
