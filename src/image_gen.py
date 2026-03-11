# -*- coding: utf-8 -*-
"""
Genera variantes de imagen: logo de A Altas Horas + título del episodio.
Tipografía atractiva (Bebas Neue) y texto más visible.
"""
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int, bold_display: bool = True):
    """Fuente principal: Bebas Neue (display). Fallback: Helvetica Bold."""
    base = Path(__file__).resolve().parent.parent
    bebas = base / "fonts" / "BebasNeue-Regular.ttf"
    if bold_display and bebas.exists():
        try:
            return ImageFont.truetype(str(bebas), size)
        except OSError:
            pass
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except OSError:
            return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def generar_imagen(
    logo_path: str,
    titulo_episodio: str,
    output_dir: Path,
    prefijo: str = "aah",
) -> List[Path]:
    """
    Crea variantes de imagen con el logo y el título del episodio.
    Devuelve lista de rutas de archivos generados.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(logo_path).convert("RGBA")
    w, h = img.size
    salidas = []

    # Fuente display más grande y visible (Bebas Neue)
    font_size = min(w // 9, 56)
    font = _get_font(font_size)
    line_height = int(font.size * 1.15)
    max_line_w = int(w * 0.92)

    # Variante 1: título abajo, barra negra sólida, texto blanco con borde sutil
    out1 = img.copy()
    draw1 = ImageDraw.Draw(out1)
    lines = _wrap_text(titulo_episodio, font, max_line_w)
    block_h = line_height * len(lines) + 32
    y0 = h - block_h - 24
    overlay = Image.new("RGBA", (w, block_h + 24), (0, 0, 0, 230))
    out1.paste(overlay, (0, y0), overlay)
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        y = y0 + 16 + i * line_height
        # Borde oscuro para legibilidad
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1),(0,-1),(0,1),(-1,0),(1,0)]:
            draw1.text((x+dx, y+dy), line, fill=(0, 0, 0, 180), font=font)
        draw1.text((x, y), line, fill=(255, 255, 255), font=font)
    path1 = output_dir / f"{prefijo}_episodio_abajo.png"
    out1.convert("RGB").save(path1, "PNG")
    salidas.append(path1)

    # Variante 2: título arriba (Story)
    font2_size = min(w // 10, 48)
    font2 = _get_font(font2_size)
    line_height2 = int(font2.size * 1.15)
    lines2 = _wrap_text(titulo_episodio, font2, max_line_w)
    block_h2 = line_height2 * len(lines2) + 24
    overlay2 = Image.new("RGBA", (w, block_h2 + 24), (0, 0, 0, 235))
    out2 = img.copy()
    out2.paste(overlay2, (0, 0), overlay2)
    draw2 = ImageDraw.Draw(out2)
    for i, line in enumerate(lines2):
        bbox = font2.getbbox(line)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        y = 14 + i * line_height2
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            draw2.text((x+dx, y+dy), line, fill=(0, 0, 0, 200), font=font2)
        draw2.text((x, y), line, fill=(255, 255, 255), font=font2)
    path2 = output_dir / f"{prefijo}_episodio_arriba.png"
    out2.convert("RGB").save(path2, "PNG")
    salidas.append(path2)

    return salidas
