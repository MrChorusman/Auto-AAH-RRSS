# -*- coding: utf-8 -*-
"""
Genera un collage con las 7 bandas y canciones del episodio.
Con imágenes reales (iTunes API) o fallback a texto.
"""
import io
import time
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int):
    base = Path(__file__).resolve().parent.parent
    bebas = base / "fonts" / "BebasNeue-Regular.ttf"
    if bebas.exists():
        try:
            return ImageFont.truetype(str(bebas), size)
        except OSError:
            pass
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except OSError:
        return ImageFont.load_default()


def generar_collage(
    bandas_y_canciones: List[Tuple[str, str]],
    titulo_episodio: str,
    output_dir: Path,
    prefijo: str = "aah",
    logo_path: str = "",
) -> Path:
    """
    Crea un collage 4+3 (o 3+4) con banda y canción por celda.
    Tamaño final: 1080x1080 (Instagram).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    items = bandas_y_canciones[:7]
    if not items:
        raise ValueError("Se necesitan al menos una banda-canción")

    # Grid: 4 arriba, 3 abajo (o 2 filas si < 4)
    cols = 4 if len(items) >= 4 else len(items)
    rows = (len(items) + cols - 1) // cols
    cell_w = 1080 // cols
    cell_h = 1080 // max(rows, 2)

    img = Image.new("RGB", (1080, 1080), (45, 25, 30))  # Granate oscuro
    draw = ImageDraw.Draw(img)

    # Colores por celda (variación sutil)
    colores = [
        (80, 35, 45), (70, 30, 40), (90, 40, 50), (75, 32, 42),
        (65, 28, 38), (85, 38, 48), (78, 34, 44),
    ]
    for i, (banda, cancion) in enumerate(items):
        row, col = divmod(i, cols)
        x0 = col * cell_w
        y0 = row * cell_h
        color = colores[i % len(colores)]
        draw.rectangle([x0, y0, x0 + cell_w - 2, y0 + cell_h - 2], fill=color, outline=(120, 60, 70))

        # Texto: banda (grande) + canción (pequeña)
        font_banda = _get_font(min(cell_w // 8, 28))
        font_cancion = _get_font(min(cell_w // 14, 16))
        texto_banda = banda[:25] + "…" if len(banda) > 25 else banda
        texto_cancion = cancion[:30] + "…" if len(cancion) > 30 else cancion

        bbox_b = font_banda.getbbox(texto_banda)
        tw_b = bbox_b[2] - bbox_b[0]
        tx = x0 + (cell_w - tw_b) // 2
        ty = y0 + cell_h // 2 - 30
        draw.text((tx, ty), texto_banda, fill=(255, 255, 255), font=font_banda)

        if cancion:
            bbox_c = font_cancion.getbbox(texto_cancion)
            tw_c = bbox_c[2] - bbox_c[0]
            cx = x0 + (cell_w - tw_c) // 2
            cy = y0 + cell_h // 2 + 5
            draw.text((cx, cy), texto_cancion, fill=(220, 200, 200), font=font_cancion)

    # Barra inferior con título del episodio
    barra_h = 80
    draw.rectangle([0, 1080 - barra_h, 1080, 1080], fill=(30, 15, 20))
    font_tit = _get_font(24)
    tit_short = titulo_episodio[:60] + "…" if len(titulo_episodio) > 60 else titulo_episodio
    bbox_t = font_tit.getbbox(tit_short)
    tw_t = bbox_t[2] - bbox_t[0]
    draw.text(((1080 - tw_t) // 2, 1080 - barra_h + 25), tit_short, fill=(255, 255, 255), font=font_tit)

    path = output_dir / f"{prefijo}_collage.png"
    img.save(path, "PNG")
    return path


def _obtener_artwork_itunes(banda: str, cancion: str) -> Optional[bytes]:
    """Busca en iTunes y devuelve los bytes de la portada (600x600) o None."""
    term = f"{banda} {cancion}".strip()
    if not term:
        return None
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": term, "media": "music", "entity": "song", "limit": 1},
            headers={"User-Agent": "AutoAAHRRSS/1.0"},
            timeout=8,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("results", [])
        if not results:
            return None
        url = results[0].get("artworkUrl600") or results[0].get("artworkUrl100", "").replace("100x100", "600x600")
        if not url:
            return None
        img_r = requests.get(url, timeout=10)
        if img_r.status_code == 200:
            return img_r.content
    except Exception:
        pass
    return None


def generar_collage_con_imagenes(
    bandas_y_canciones: List[Tuple[str, str]],
    titulo_episodio: str,
    output_dir: Path,
    prefijo: str = "aah",
) -> Path:
    """
    Collage de 4 bandas con portadas reales. Solo incluimos las que encuentren imagen.
    Recorremos la lista: si encontramos imagen → la añadimos; si no → siguiente.
    Paramos al tener 4. Grid 2x2 homogéneo. Footer: título + "Y más..."
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    items = bandas_y_canciones[:7]
    if not items:
        raise ValueError("Se necesitan al menos una banda-canción")

    # Recoger solo las 4 primeras que tengan imagen
    seleccionados: List[Tuple[str, str, Image.Image]] = []
    for banda, cancion in items:
        if len(seleccionados) >= 4:
            break
        data = _obtener_artwork_itunes(banda, cancion)
        if data:
            try:
                im = Image.open(io.BytesIO(data)).convert("RGB")
                seleccionados.append((banda, cancion, im))
            except Exception:
                pass
        time.sleep(0.5)  # Rate limit iTunes

    if not seleccionados:
        raise ValueError("No se encontró imagen para ninguna banda")

    # Layout: franja marca (top) + grid 2x2 + footer
    franja_marca_h = 70
    footer_h = 100
    grid_h = 1080 - franja_marca_h - footer_h
    cols, rows = 2, 2
    cell_w = 1080 // cols
    cell_h = grid_h // rows

    img = Image.new("RGB", (1080, 1080), (45, 25, 30))
    draw = ImageDraw.Draw(img)

    # Franja de marca: más contraste para destacar en feed
    draw.rectangle([0, 0, 1080, franja_marca_h], fill=(118, 36, 48))
    draw.rectangle([0, franja_marca_h - 3, 1080, franja_marca_h], fill=(206, 76, 88))
    font_marca = _get_font(46)
    texto_marca = "A ALTAS HORAS"
    bbox_m = font_marca.getbbox(texto_marca)
    draw.text(((1080 - (bbox_m[2] - bbox_m[0])) // 2, (franja_marca_h - (bbox_m[3] - bbox_m[1])) // 2 - 4), texto_marca, fill=(255, 255, 255), font=font_marca)

    font_banda = _get_font(28)
    font_cancion = _get_font(16)

    for i, (banda, cancion, im) in enumerate(seleccionados[:4]):
        row, col = divmod(i, 2)
        x0 = col * cell_w + 2
        y0 = franja_marca_h + row * cell_h + 2
        im_resized = im.resize((cell_w - 4, cell_h - 4), Image.Resampling.LANCZOS)
        img.paste(im_resized, (x0, y0))

        # Barra semitransparente + texto para legibilidad
        texto_b = (banda[:18] + "…") if len(banda) > 18 else banda
        texto_c = (cancion[:22] + "…") if len(cancion) > 22 else cancion
        barra_y = y0 + cell_h - 4 - 55
        draw.rectangle([x0, barra_y, x0 + cell_w - 4, y0 + cell_h - 4], fill=(30, 15, 20))
        bbox_b = font_banda.getbbox(texto_b)
        tx = x0 + (cell_w - 4 - (bbox_b[2] - bbox_b[0])) // 2
        draw.text((tx, barra_y + 8), texto_b, fill=(255, 255, 255), font=font_banda)
        if cancion:
            bbox_c = font_cancion.getbbox(texto_c)
            cx = x0 + (cell_w - 4 - (bbox_c[2] - bbox_c[0])) // 2
            draw.text((cx, barra_y + 36), texto_c, fill=(220, 220, 220), font=font_cancion)

    # Footer simplificado: título + CTA (mejor jerarquía y legibilidad)
    barra_h = 100
    draw.rectangle([0, 1080 - barra_h, 1080, 1080], fill=(38, 18, 25))
    font_tit = _get_font(24)
    tit_short = titulo_episodio[:42] + "…" if len(titulo_episodio) > 42 else titulo_episodio
    bbox_t = font_tit.getbbox(tit_short)
    draw.text(((1080 - (bbox_t[2] - bbox_t[0])) // 2, 1080 - barra_h + 14), tit_short, fill=(255, 255, 255), font=font_tit)
    texto_cta = "ESCUCHALO EN BIO"
    font_cta = _get_font(20)
    bbox_cta = font_cta.getbbox(texto_cta)
    draw.text(((1080 - (bbox_cta[2] - bbox_cta[0])) // 2, 1080 - barra_h + 52), texto_cta, fill=(230, 200, 205), font=font_cta)

    path = output_dir / f"{prefijo}_collage_imagenes.png"
    img.save(path, "PNG")
    return path
