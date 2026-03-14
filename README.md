# Cover Generator

Generate KDP-ready book covers with genre-aware typography and optional DALL-E 3 backgrounds. AI picks the design — colors, fonts, layout — based on your genre and book description. One command, print-ready output.

## What It Does

- **Claude designs your cover** — picks fonts, colors, layout, and DALL-E prompts based on genre conventions and your book description
- **Pillow renders it** — typography-driven covers with proper KDP dimensions, bleed, and spine calculations
- **DALL-E 3 generates backgrounds** (optional) — atmospheric, period-accurate art with dark zones for text readability
- **Outputs everything** — full-size PNG, PDF, thumbnail, and Amazon-size thumbnail for readability testing

## Examples

<p align="center">
<em>Bronze Age Egypt historical thriller — DALL-E background + auto typography</em>
</p>

## Quick Start

```bash
# Clone and install
git clone https://github.com/randypellegrini/cover-generator.git
cd cover-generator
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Configure API keys
cp .env.example .env
# Edit .env with your Anthropic key (required) and OpenAI key (optional)

# Generate an ebook cover
cover-generator ebook "The First Key" \
  --genre historical \
  --author "Randy Pellegrini" \
  --dalle \
  --variants 3 \
  -d "Bronze Age Egypt, 1200 BCE. Ancient temples, hieroglyphics, torchlight."
```

## Commands

| Command | Description |
|---------|-------------|
| `generate` | Full paperback cover (front + spine + back) for KDP |
| `ebook` | Front cover only (1600x2560) for Kindle |
| `design` | Preview AI design parameters without rendering |
| `genres` | List available genre profiles |
| `fonts` | List available system fonts |

### Full Paperback Cover

```bash
cover-generator generate "The First Key" \
  --author "Randy Pellegrini" \
  --series "Book Three of The Architecture of Survival" \
  --genre historical \
  --pages 350 \
  --trim 5.5x8.5 \
  --paper cream \
  --blurb-file blurb.txt \
  --dalle
```

Outputs a full wrap cover (back + spine + front) with correct KDP dimensions, spine width calculated from page count, and bleed margins.

### Ebook Cover

```bash
cover-generator ebook "The First Key" \
  --genre thriller \
  --dalle \
  --variants 3 \
  -d "Description of your book for the AI designer"
```

Generates 1600x2560 front covers. Each variant gets a fresh AI design pass and (if `--dalle`) a unique DALL-E background. Outputs full-size, thumbnail, and Amazon-realistic thumbnail.

### Custom Background

```bash
cover-generator ebook "My Book" --background my-art.png --genre scifi
```

Use your own image as the background instead of DALL-E.

## Options

| Option | Description |
|--------|-------------|
| `--genre` | `thriller`, `historical`, `scifi`, `mystery`, `literary`, `romance`, `fantasy`, `horror` |
| `--dalle` | Generate DALL-E 3 background art (requires OpenAI API key) |
| `--background` | Use a custom image as background |
| `--variants N` | Generate N design variants |
| `--pages N` | Page count for spine width calculation |
| `--trim` | Trim size: `5x8`, `5.25x8`, `5.5x8.5`, `6x9` |
| `--paper` | Paper type: `cream`, `white`, `color` |
| `--blurb-file` | Text file for back cover blurb |
| `-d` | Book description (helps AI choose better design) |
| `-o` | Output directory |

## How It Works

1. **Designer** (Claude) — analyzes your genre, title, and description. Picks a color palette, fonts, title line breaks, layout variant, decorative elements, and writes a DALL-E prompt for period-accurate background art.

2. **Background** — either generates a DALL-E 3 image, uses a gradient from the genre palette, or uses your custom image. DALL-E backgrounds get automatic dark gradient overlays at top and bottom for text readability.

3. **Renderer** (Pillow) — composites the cover: title with shadow/outline for contrast, subtitle, author name, and optional decorative elements. For paperbacks, adds spine text and back cover with blurb.

4. **Output** — full-size PNG (300 DPI), PDF, thumbnail (300px), and Amazon-realistic thumbnail (150px) for readability testing.

## Genre Profiles

Each genre defines:
- **Color palettes** — 3 options per genre (dark/moody, high-contrast, warm)
- **Font preferences** — genre-appropriate typeface choices
- **Title style** — heavy/medium weight, upper/title case
- **Layout patterns** — centered, top-heavy, bottom-heavy
- **DALL-E style hints** — mood and aesthetic for background generation

## Configuration

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...    # Required — Claude designs cover parameters
OPENAI_API_KEY=sk-proj-...      # Optional — DALL-E 3 background art
COVER_OUTPUT_DIR=./output
```

Without an Anthropic key, falls back to genre-default parameters.
Without an OpenAI key, `--dalle` falls back to gradient backgrounds.

## Development

```bash
# Run tests
pytest tests/ -v

# 68 tests covering:
# - KDP dimension calculations
# - Genre profile validation
# - Font discovery
# - Background generation
# - Full cover rendering across all genre/palette combos
# - Thumbnail generation
```

## Requirements

- Python 3.9+
- macOS (uses system fonts — Georgia, Impact, Helvetica, etc.)
- Anthropic API key (for AI design)
- OpenAI API key (optional, for DALL-E backgrounds)

## Cost

- **Claude API**: ~$0.01 per design pass
- **DALL-E 3 HD**: ~$0.08 per background image
- **3 variants with DALL-E**: ~$0.27 total

## License

MIT
