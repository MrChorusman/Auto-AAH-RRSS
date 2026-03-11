# -*- coding: utf-8 -*-
"""
Genera el texto (copy) y hashtags para cada red.
Tono: cercano, irónico; "el indie que más nos gusta", "una hora de buena música", "Los benditos tarados".
Siempre en español. Enlace en bio donde aplique.
"""
import os
import re
from typing import List, Optional

import requests

from config import GROQ_API_KEY, LINK_BIO, LINK_X


def copy_plantilla(
    titulo: str,
    bandas: List[str],
    red: str,
) -> str:
    """
    Copy solo CTA: llamada a escuchar. Sin bandas, sin juicios ni valoraciones.
    """
    frases_cta = [
        "Una hora de buena música.",
        "El indie que más nos gusta.",
        "Nuevo episodio listo para escuchar 🎧",
    ]
    idx = hash(titulo) % len(frases_cta)
    cta = frases_cta[idx]

    if red == "x":
        base = f"🕐 {titulo}\n\n{cta}\n{LINK_X}"
        return base[:280]
    if red == "instagram":
        return f"Nuevo episodio: {titulo}\n\n{cta} Enlace en bio."
    if red == "tiktok":
        return f"🕐 {titulo}\n\n{cta} Enlace en bio."
    return f"{titulo}\n\n{cta}\n\n{LINK_BIO}"


def sugerir_hashtags(titulo: str, bandas: List[str], red: str) -> List[str]:
    """
    Hashtags orientados a viralidad: indie, música, podcast, nombres de bandas.
    """
    base = ["#indie", "#podcast", "#musica", "#AAltasHoras", "#LosBenditosTarados"]
    if bandas:
        for b in bandas[:7]:
            tag = "#" + re.sub(r"[^\wáéíóúñ]", "", b.replace(" ", ""))[:20]
            if tag != "#" and tag not in base:
                base.append(tag)
    if red == "instagram":
        base.extend(["#indiespanish", "#nuevomusic", "#goodmusic"])
    if red == "tiktok":
        base.extend(["#indie", "#music", "#fyp", "#podcast"])
    return base[:15]


def copy_con_ia(
    titulo: str,
    bandas: List[str],
    red: str,
) -> Optional[str]:
    """
    Copy solo CTA: llamada a escuchar. SIN mencionar bandas. Sin juicios ni valoraciones.
    """
    if not GROQ_API_KEY:
        return None
    instrucciones = {
        "x": f"Para X: MÁXIMO 275 caracteres. Solo título + llamada a escuchar. Incluye SIEMPRE este enlace exacto: {LINK_X}",
        "instagram": "Para Instagram: MÁXIMO 250 caracteres. Solo título + CTA para escuchar.",
        "tiktok": "Para TikTok: MÁXIMO 150 caracteres. Solo CTA breve para escuchar.",
    }
    prompt = (
        "Eres el community manager del podcast 'A Altas Horas'. "
        "Escribe UN mensaje para anunciar el episodio. "
        "REGLAS ESTRICTAS: NO menciones bandas ni artistas. NO hagas juicios ni valoraciones. "
        "Solo: título del episodio + llamada a la acción para escuchar. "
        "Frases permitidas: 'una hora de buena música', 'el indie que más nos gusta'. "
        f"Título: {titulo}. "
        f"{instrucciones.get(red, '')} "
        "En español. Sin hashtags. Sin comillas."
    )
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
            },
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
            if text:
                text = text.strip('"\'')
                if red == "x" and len(text) > 280:
                    text = text[:277] + "..."
                if red == "x" and LINK_X not in text:
                    extra = f" {LINK_X}"
                    if len(text) + len(extra) <= 280:
                        text = text + extra
                    else:
                        base = text[: max(0, 280 - len(extra) - 1)].rstrip(" .")
                        text = base + extra
                if red == "instagram" and len(text) > 400:
                    text = text[:397] + "..."
                if red == "tiktok" and len(text) > 200:
                    text = text[:197] + "..."
                return text
    except Exception:
        pass
    return None


def _copy_menciona_bandas(copy: str, bandas: List[str]) -> bool:
    """True si el copy menciona alguna banda (no queremos eso)."""
    copy_lower = copy.lower()
    for b in bandas:
        if b.lower() in copy_lower:
            return True
    return False


def generar_copy_y_hashtags(
    titulo: str,
    bandas: List[str],
    usar_ia: bool = True,
) -> dict:
    """
    Devuelve {"x": {"copy": "...", "hashtags": []}, "instagram": ..., "tiktok": ...}
    Copy solo CTA, sin bandas ni valoraciones.
    """
    resultado = {}
    for red in ("x", "instagram", "tiktok"):
        copy = copy_con_ia(titulo, bandas, red) if usar_ia else None
        if not copy or _copy_menciona_bandas(copy, bandas):
            copy = copy_plantilla(titulo, bandas, red)
        resultado[red] = {
            "copy": copy,
            "hashtags": sugerir_hashtags(titulo, bandas, red),
        }
    return resultado
