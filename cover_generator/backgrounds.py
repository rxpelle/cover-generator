"""Background generation — gradient fills and optional DALL-E art."""

import logging
from PIL import Image, ImageDraw, ImageFilter
from .config import Config

logger = logging.getLogger(__name__)


def create_gradient_background(width, height, color_top, color_bottom):
    """Create a vertical gradient background."""
    img = Image.new('RGB', (width, height), color_top)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def create_solid_background(width, height, color):
    """Create a solid color background."""
    return Image.new('RGB', (width, height), color)


def add_noise_texture(img, intensity=15):
    """Add subtle noise texture to an image for a less flat look."""
    import random
    pixels = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            noise = random.randint(-intensity, intensity)
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)),
            )
    return img


def add_vignette(img, strength=0.4):
    """Add a vignette (darkened edges) effect."""
    import math
    width, height = img.size

    # Create a luminance mask: bright in center, dark at edges
    mask = Image.new('L', (width, height), 0)
    cx, cy = width / 2, height / 2
    max_dist = math.sqrt(cx * cx + cy * cy)

    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ratio = dist / max_dist
            # 255 at center, darkens toward edges
            val = int(255 * (1 - strength * ratio * ratio))
            pixels[x, y] = max(0, min(255, val))

    mask = mask.filter(ImageFilter.GaussianBlur(radius=width // 20))

    # Multiply: pixel * (mask/255)
    result = img.copy()
    r, g, b = result.split()
    from PIL import ImageChops
    r = ImageChops.multiply(r, mask)
    g = ImageChops.multiply(g, mask)
    b = ImageChops.multiply(b, mask)

    # ImageChops.multiply does (a*b)/255, but our mask is already 0-255 scale
    # so we need to adjust — use composite instead
    black = Image.new('RGB', (width, height), (0, 0, 0))
    mask_img = mask.convert('L')
    return Image.composite(img, black, mask_img)


def generate_dalle_background(prompt, width, height):
    """Generate a background image using DALL-E 3.

    Returns a PIL Image or None if generation fails.
    """
    if not Config.has_openai_key():
        logger.warning("No OpenAI API key — skipping DALL-E generation")
        return None

    try:
        from openai import OpenAI
        import urllib.request
        import io

        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # DALL-E 3 supports 1024x1024, 1024x1792, 1792x1024
        # Pick the closest aspect ratio
        aspect = width / height
        if aspect > 1.3:
            dalle_size = '1792x1024'
        elif aspect < 0.7:
            dalle_size = '1024x1792'
        else:
            dalle_size = '1024x1024'

        full_prompt = (
            f"Book cover background art (NO TEXT, NO WORDS, NO LETTERS): {prompt}. "
            "Atmospheric, high resolution, suitable as a book cover background. "
            "Leave space at top and bottom for text overlay."
        )

        logger.info(f"Generating DALL-E background ({dalle_size})...")
        response = client.images.generate(
            model='dall-e-3',
            prompt=full_prompt,
            size=dalle_size,
            quality='hd',
            n=1,
        )

        image_url = response.data[0].url
        logger.info("Downloading generated image...")

        req = urllib.request.Request(image_url)
        with urllib.request.urlopen(req) as resp:
            image_data = resp.read()

        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        # Resize to target dimensions
        img = img.resize((width, height), Image.LANCZOS)
        return img

    except Exception as e:
        logger.error(f"DALL-E generation failed: {e}")
        return None
