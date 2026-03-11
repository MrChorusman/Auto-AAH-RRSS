# -*- coding: utf-8 -*-
"""
Envía el borrador (imagen, textos, hashtags) al usuario por Telegram para revisión.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def enviar_borrador(
    imagen_path: Path,
    titulo: str,
    bandas: List[str],
    copies: Dict[str, Dict[str, Any]],
    guid: str,
) -> bool:
    """
    Envía al chat de Telegram: imagen (caption corta) + mensaje con textos.
    Telegram limita captions a 1024 chars, por eso separamos.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    caption_corta = f"📻 *Nuevo episodio listo para revisar*\n\n*{titulo}*\n\nBandas: {', '.join(bandas[:7]) if bandas else '—'}"
    texto_completo = (
        f"*X:*\n{copies.get('x', {}).get('copy', '')}\n\n"
        f"*Instagram:*\n{copies.get('instagram', {}).get('copy', '')}\n\n"
        f"*TikTok:*\n{copies.get('tiktok', {}).get('copy', '')}\n\n"
        f"Hashtags: {' '.join(copies.get('instagram', {}).get('hashtags', [])[:8])}\n\n"
        f"Guid: `{guid}`\n\n"
        "Usa el bot para aprobar o editar antes de publicar."
    )
    try:
        with open(imagen_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption_corta[:1024], "parse_mode": "Markdown"}
            r = requests.post(f"{base}/sendPhoto", data=data, files=files, timeout=30)
        if r.status_code == 200:
            requests.post(
                base + "/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": texto_completo, "parse_mode": "Markdown"},
                timeout=10,
            )
            return True
    except Exception:
        pass
    requests.post(
        base + "/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": caption_corta + "\n\n" + texto_completo, "parse_mode": "Markdown"},
        timeout=10,
    )
    return False


def enviar_mensaje(texto: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"},
        timeout=10,
    )
    return r.status_code == 200


def enviar_sin_bandas(titulo: str, guid: str) -> bool:
    """Avisa de que no se pudieron extraer bandas y se bloquea hasta confirmación."""
    return enviar_mensaje(
        f"⚠️ *Episodio nuevo pero sin bandas*\n\n"
        f"*Título:* {titulo}\n"
        f"*Guid:* `{guid}`\n\n"
        "Responde con la lista de bandas (separadas por comas) para desbloquear y generar el borrador."
    )
