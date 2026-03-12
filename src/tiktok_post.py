# -*- coding: utf-8 -*-
"""
Publica en TikTok usando Content Posting API (foto).
Endpoint base: https://open.tiktokapis.com
"""
from pathlib import Path
from typing import Optional, Tuple

import requests

from config import TIKTOK_ACCESS_TOKEN


def _subir_imagen_publica(image_path: Path) -> Optional[str]:
    """Sube imagen a URL publica temporal (catbox.moe)."""
    if not image_path or not Path(image_path).exists():
        return None
    try:
        with open(image_path, "rb") as f:
            files = {"fileToUpload": (Path(image_path).name, f, "image/png")}
            data = {"reqtype": "fileupload"}
            r = requests.post("https://catbox.moe/user/api.php", data=data, files=files, timeout=30)
        if r.status_code == 200:
            url = r.text.strip()
            if url.startswith("http"):
                return url
    except Exception:
        pass
    return None


def _query_creator_info() -> Tuple[bool, dict]:
    if not TIKTOK_ACCESS_TOKEN:
        return False, {"error": "Falta TIKTOK_ACCESS_TOKEN"}
    try:
        r = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
            headers={
                "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json={},
            timeout=20,
        )
        d = r.json()
        if r.status_code == 200 and d.get("error", {}).get("code") in ("ok", None):
            return True, d
        return False, d
    except Exception as e:
        return False, {"error": {"message": str(e)}}


def publicar_tiktok(copy_tiktok: str, ruta_imagen: Path) -> Tuple[bool, str]:
    """
    Publica una foto en TikTok.
    Si no hay permisos de direct post en app auditada, puede limitarse a SELF_ONLY.
    """
    if not TIKTOK_ACCESS_TOKEN:
        return False, "Falta TIKTOK_ACCESS_TOKEN en .env"

    image_url = _subir_imagen_publica(ruta_imagen)
    if not image_url:
        return False, "No se pudo obtener URL publica de la imagen para TikTok"

    ok_info, info = _query_creator_info()
    privacy = "SELF_ONLY"
    if ok_info:
        # Intentar usar privacidad publica si el creator lo permite
        levels = info.get("data", {}).get("privacy_level_options", []) or []
        if "PUBLIC_TO_EVERYONE" in levels:
            privacy = "PUBLIC_TO_EVERYONE"
        elif levels:
            privacy = levels[0]

    title = (copy_tiktok or "").strip()
    if len(title) > 90:
        title = title[:87] + "..."

    payload = {
        "post_info": {
            "title": title,
            "privacy_level": privacy,
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "photo_images": [image_url],
            "photo_cover_index": 0,
        },
        "post_mode": "DIRECT_POST",
        "media_type": "PHOTO",
    }

    try:
        r = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/content/init/",
            headers={
                "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json=payload,
            timeout=30,
        )
        d = r.json()
        if r.status_code == 200 and d.get("error", {}).get("code") in ("ok", None):
            publish_id = d.get("data", {}).get("publish_id", "")
            return True, f"Publicacion TikTok iniciada. publish_id={publish_id or 'n/a'}"
        err = d.get("error", {}).get("message", "Error en TikTok publish init")
        return False, err
    except Exception as e:
        return False, f"Excepcion TikTok: {e}"
