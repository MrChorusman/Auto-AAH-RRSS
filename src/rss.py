# -*- coding: utf-8 -*-
"""
Lee el feed RSS de A Altas Horas (Ivoox), detecta episodio nuevo y extrae bandas de la descripción.
"""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import feedparser


@dataclass
class Episodio:
    titulo: str
    enlace: str
    fecha: datetime
    descripcion: str
    guid: str
    bandas: list[str]
    bandas_y_canciones: list[tuple[str, str]]  # [(banda, canción), ...]


def fetch_feed(rss_url: str) -> feedparser.FeedParserDict:
    return feedparser.parse(rss_url, agent="AutoAAHRRSS/1.0")


def obtener_ultimo_episodio(rss_url: str) -> Optional[Episodio]:
    feed = fetch_feed(rss_url)
    if not feed.entries:
        return None
    entry = feed.entries[0]
    titulo = entry.get("title", "").strip()
    link = entry.get("link", "")
    guid = entry.get("id", link)
    desc = entry.get("description", "") or entry.get("summary", "")
    # Limpiar HTML básico
    desc_limpia = re.sub(r"<[^>]+>", " ", desc)
    desc_limpia = re.sub(r"\s+", " ", desc_limpia).strip()
    published = entry.get("published_parsed")
    if published:
        from time import mktime
        fecha = datetime.fromtimestamp(mktime(published))
    else:
        fecha = datetime.utcnow()
    bandas, bandas_y_canciones = extraer_bandas_y_canciones(desc_limpia, titulo)
    return Episodio(
        titulo=titulo,
        enlace=link,
        fecha=fecha,
        descripcion=desc_limpia,
        guid=guid,
        bandas=bandas,
        bandas_y_canciones=bandas_y_canciones,
    )


# Palabras que no son nombres de banda
_EXCLUIR = {
    "el", "la", "los", "las", "de", "del", "y", "en", "con", "más", "etc",
    "bienvenidos", "bienvenidas", "edición", "nueva", "nacional", "internacional",
    "bienvenida", "altas", "horas", "podcast", "programa", "échanos", "oído",
    "como", "viejos", "conocidos",
}


def extraer_bandas_y_canciones(descripcion: str, titulo: str) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Formato Ivoox: "Banda - Canción" por línea.
    Ej: "Temples - Jet Stream Heart", "Tigercub - Fall In Fall Out"
    Devuelve (bandas, [(banda, canción), ...])
    """
    bandas = []
    bandas_y_canciones: list[tuple[str, str]] = []

    # 1) Lista en descripción: "sonarán... como: - Temples - Jet Stream Heart - Tigercub - Fall In Fall Out - ..."
    for patron in (
        r"(?:sonarán|suenan|conocidos como|artistas?|bandas?)\s*[:\-]\s*([^¡]+?)(?:¡|$)",
        r"(?:artistas?|bandas?|con|música)\s*[:\-]\s*([^\n.]+)",
    ):
        for m in re.finditer(patron, descripcion, re.IGNORECASE):
            trozo = m.group(1).strip().lstrip("-").strip()
            partes = [p.strip() for p in re.split(r"\s+-\s+", trozo) if p.strip()]
            # Pares: índice par = banda, impar = canción
            for i in range(0, len(partes) - 1, 2):
                banda, cancion = partes[i], partes[i + 1]
                if banda and len(banda) < 50 and banda.lower() not in _EXCLUIR:
                    bandas.append(banda)
                    bandas_y_canciones.append((banda, cancion))
            if bandas_y_canciones:
                break
        if bandas_y_canciones:
            break

    # 2) Fallback: solo título (ej. "Temples, Tigercub y más") — sin canciones
    if not bandas and " - " in titulo:
        trozo = titulo.split(" - ", 1)[1].strip()
        trozo = re.sub(r"\.\.\.?$", "", trozo)
        for parte in re.split(r"[,;]|\s+y\s+|\s+&\s+", trozo):
            nombre = parte.strip()
            if nombre and len(nombre) > 1 and nombre.lower() not in _EXCLUIR:
                bandas.append(nombre)
                bandas_y_canciones.append((nombre, ""))

    # Quitar duplicados en bandas manteniendo orden
    vistos = set()
    bandas_unicas = []
    byc_unicas = []
    for b, (banda, cancion) in zip(bandas, bandas_y_canciones):
        key = banda.lower().strip()
        if key and key not in vistos:
            vistos.add(key)
            bandas_unicas.append(banda)
            byc_unicas.append((banda, cancion))
    return bandas_unicas, byc_unicas


def episodio_ya_procesado(guid: str, archivo_estado: str) -> bool:
    """Comprueba si este episodio (guid) ya fue procesado (guardado en archivo)."""
    from pathlib import Path
    p = Path(archivo_estado)
    if not p.exists():
        return False
    return guid.strip() in p.read_text(encoding="utf-8").splitlines()


def marcar_episodio_procesado(guid: str, archivo_estado: str) -> None:
    from pathlib import Path
    p = Path(archivo_estado)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(guid.strip() + "\n")
