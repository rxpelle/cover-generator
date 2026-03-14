"""CLI interface for Cover Generator."""

import os
import json
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import Config
from .designer import get_design_params
from .renderer import render_cover, render_front_only, create_thumbnail
from .genres import list_genres, get_genre
from .fonts import list_available_fonts

console = Console()


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Generate KDP-ready book covers with genre-aware typography."""
    Config.setup_logging()


@main.command()
@click.argument('title')
@click.option('--subtitle', '-s', default='', help='Book subtitle')
@click.option('--author', '-a', default='Randy Pellegrini', help='Author name')
@click.option('--series', default='', help='Series name (e.g., "Book Three of The Architecture of Survival")')
@click.option('--genre', '-g', default='thriller', help='Genre for design conventions')
@click.option('--blurb', '-b', default='', help='Back cover blurb text')
@click.option('--blurb-file', type=click.Path(exists=True), help='File containing blurb text')
@click.option('--pages', '-p', default=300, type=int, help='Page count (for spine width)')
@click.option('--trim', default='5.5x8.5', help='Trim size (e.g., 5.5x8.5, 6x9)')
@click.option('--paper', default='cream', type=click.Choice(['cream', 'white', 'color']), help='Paper type')
@click.option('--dalle', is_flag=True, help='Use DALL-E 3 for background art')
@click.option('--background', type=click.Path(exists=True), help='Custom background image')
@click.option('--variants', '-v', default=1, type=int, help='Number of design variants to generate')
@click.option('--output', '-o', default='', help='Output directory')
@click.option('--description', '-d', default='', help='Book description (helps AI choose design)')
def generate(title, subtitle, author, series, genre, blurb, blurb_file,
             pages, trim, paper, dalle, background, variants, output, description):
    """Generate a full cover (front + spine + back) for KDP paperback."""

    if blurb_file and not blurb:
        blurb = Path(blurb_file).read_text().strip()

    output_dir = output or Config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    book = {
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'series': series,
        'blurb': blurb,
    }

    dims = Config.calculate_cover_dimensions(trim=trim, page_count=pages, paper=paper)

    console.print(Panel.fit(
        f"[bold]{title}[/bold]\n"
        f"Genre: {genre} | Trim: {trim} | Pages: {pages} | Paper: {paper}\n"
        f"Cover: {dims['width_px']}x{dims['height_px']}px | "
        f"Spine: {dims['spine_w_in']:.3f}\" ({dims['spine_w_px']}px)"
        + (f"\nDALL-E: enabled" if dalle else ""),
        title="Cover Generator",
    ))

    bg_img = None
    if background:
        from PIL import Image
        bg_img = Image.open(background).convert('RGB')
        console.print(f"[dim]Using custom background: {background}[/dim]")

    for i in range(variants):
        if variants > 1:
            console.print(f"\n[bold]Variant {i + 1}/{variants}[/bold]")

        console.print("[dim]Generating design parameters...[/dim]")
        design = get_design_params(
            title=title, subtitle=subtitle, author=author,
            series=series, genre=genre, description=description,
        )

        console.print(f"[dim]Design: {design.get('design_rationale', 'N/A')}[/dim]")
        console.print(f"[dim]Fonts: title={design.get('title_font')}, "
                       f"author={design.get('author_font')}[/dim]")
        console.print(f"[dim]Layout: {design.get('layout_variant', 'centered')} | "
                       f"Elements: {design.get('decorative_elements', [])}[/dim]")

        console.print("[dim]Rendering cover...[/dim]")
        cover = render_cover(
            book=book,
            design_params=design,
            dims=dims,
            genre_name=genre,
            use_dalle=dalle,
            background_image=bg_img,
        )

        # Save outputs
        slug = title.lower().replace(' ', '-').replace("'", '')[:40]
        suffix = f'-v{i + 1}' if variants > 1 else ''

        # Full cover
        cover_path = os.path.join(output_dir, f'{slug}-cover{suffix}.png')
        cover.save(cover_path, 'PNG', dpi=(300, 300))
        console.print(f"[green]Saved:[/green] {cover_path}")

        # PDF version
        pdf_path = os.path.join(output_dir, f'{slug}-cover{suffix}.pdf')
        cover.convert('RGB').save(pdf_path, 'PDF', resolution=300)
        console.print(f"[green]Saved:[/green] {pdf_path}")

        # Thumbnail
        thumb = create_thumbnail(cover, size=400)
        thumb_path = os.path.join(output_dir, f'{slug}-thumbnail{suffix}.png')
        thumb.save(thumb_path, 'PNG')
        console.print(f"[green]Saved:[/green] {thumb_path}")

        # Save design params
        params_path = os.path.join(output_dir, f'{slug}-design{suffix}.json')
        with open(params_path, 'w') as f:
            json.dump(design, f, indent=2)
        console.print(f"[dim]Design params: {params_path}[/dim]")


@main.command()
@click.argument('title')
@click.option('--subtitle', '-s', default='', help='Book subtitle')
@click.option('--author', '-a', default='Randy Pellegrini', help='Author name')
@click.option('--series', default='', help='Series name')
@click.option('--genre', '-g', default='thriller', help='Genre for design conventions')
@click.option('--dalle', is_flag=True, help='Use DALL-E 3 for background art')
@click.option('--variants', '-v', default=3, type=int, help='Number of variants')
@click.option('--output', '-o', default='', help='Output directory')
@click.option('--description', '-d', default='', help='Book description')
def ebook(title, subtitle, author, series, genre, dalle, variants, output, description):
    """Generate ebook cover (front only, 1600x2560)."""

    output_dir = output or Config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    book = {
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'series': series,
    }

    console.print(Panel.fit(
        f"[bold]{title}[/bold]\n"
        f"Genre: {genre} | Format: ebook (1600x2560)"
        + (f"\nDALL-E: enabled" if dalle else ""),
        title="Ebook Cover Generator",
    ))

    for i in range(variants):
        if variants > 1:
            console.print(f"\n[bold]Variant {i + 1}/{variants}[/bold]")

        console.print("[dim]Generating design parameters...[/dim]")
        design = get_design_params(
            title=title, subtitle=subtitle, author=author,
            series=series, genre=genre, description=description,
        )

        console.print(f"[dim]Design: {design.get('design_rationale', 'N/A')}[/dim]")

        console.print("[dim]Rendering ebook cover...[/dim]")
        cover = render_front_only(
            book=book,
            design_params=design,
            genre_name=genre,
            use_dalle=dalle,
        )

        slug = title.lower().replace(' ', '-').replace("'", '')[:40]
        suffix = f'-v{i + 1}' if variants > 1 else ''

        cover_path = os.path.join(output_dir, f'{slug}-ebook{suffix}.png')
        cover.save(cover_path, 'PNG', dpi=(300, 300))
        console.print(f"[green]Saved:[/green] {cover_path}")

        # Thumbnail for quick preview
        thumb = create_thumbnail(cover, size=300)
        thumb_path = os.path.join(output_dir, f'{slug}-ebook-thumb{suffix}.png')
        thumb.save(thumb_path, 'PNG')
        console.print(f"[green]Saved:[/green] {thumb_path}")

        # Amazon-realistic thumbnail (what shoppers actually see)
        amazon_thumb = create_thumbnail(cover, size=150)
        amazon_path = os.path.join(output_dir, f'{slug}-amazon-thumb{suffix}.png')
        amazon_thumb.save(amazon_path, 'PNG')
        console.print(f"[green]Saved:[/green] {amazon_path} (Amazon search size)")

        params_path = os.path.join(output_dir, f'{slug}-ebook-design{suffix}.json')
        with open(params_path, 'w') as f:
            json.dump(design, f, indent=2)


@main.command('genres')
def show_genres():
    """List available genre profiles."""
    table = Table(title="Available Genre Profiles")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Title Style")
    table.add_column("Palettes")

    for key, name in list_genres():
        profile = get_genre(key)
        table.add_row(
            key, name,
            f"{profile['title_weight']} / {profile['title_case']}",
            str(len(profile['palettes'])),
        )

    console.print(table)


@main.command('fonts')
def show_fonts():
    """List available system fonts."""
    table = Table(title="Available System Fonts")
    table.add_column("Font Name", style="cyan")
    table.add_column("Path", style="dim")

    for name, path in list_available_fonts():
        table.add_row(name, path)

    console.print(table)
    console.print(f"\n[dim]{len(list_available_fonts())} fonts found[/dim]")


@main.command()
@click.argument('title')
@click.option('--genre', '-g', default='thriller')
@click.option('--subtitle', '-s', default='')
@click.option('--author', '-a', default='Randy Pellegrini')
@click.option('--series', default='')
@click.option('--description', '-d', default='')
def design(title, genre, subtitle, author, series, description):
    """Preview AI-generated design parameters without rendering."""
    console.print("[dim]Generating design parameters...[/dim]")

    params = get_design_params(
        title=title, subtitle=subtitle, author=author,
        series=series, genre=genre, description=description,
    )

    console.print(Panel(
        json.dumps(params, indent=2),
        title=f"Design Parameters for \"{title}\"",
    ))


if __name__ == '__main__':
    main()
