# -*- coding: utf-8 -*-
"""
Publica en Instagram (feed) usando Instagram Graph API.
Requiere URL publica de imagen; para eso sube temporalmente a catbox.moe (gratis).
"""
from pathlib import Path
from typing import Optional, Tuple

import requests

from config import INSTAGRAM_BUSINESS_ID, LINK_BIO, META_ACCESS_TOKEN


def _subir_imagen_publica(image_path: Path) -> Optional[str]:
    """
    Sube la imagen a catbox.moe y devuelve URL publica.
    Servicio gratuito sin autenticacion.
    """
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


def publicar_instagram(copy_instagram: str, ruta_imagen: Path) -> Tuple[bool, str]:
    """
    Flujo IG:
    1) Subir imagen a URL publica
    2) POST /{ig_user_id}/media
    3) POST /{ig_user_id}/media_publish
    """
    if not (META_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ID):
        return False, "Faltan META_ACCESS_TOKEN o INSTAGRAM_BUSINESS_ID en .env"

    image_url = _subir_imagen_publica(ruta_imagen)
    if not image_url:
        return False, "No se pudo obtener URL publica de la imagen"

    caption = f"{copy_instagram}\n\n{LINK_BIO}".strip()
    try:
        create_r = requests.post(
            f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": META_ACCESS_TOKEN,
            },
            timeout=30,
        )
        create_data = create_r.json()
        creation_id = create_data.get("id")
        if not creation_id:
            err = create_data.get("error", {}).get("message", "Error creando contenedor IG")
            return False, err

        publish_r = requests.post(
            f"https://graph.facebook.com/v25.0/{INSTAGRAM_BUSINESS_ID}/media_publish",
            data={"creation_id": creation_id, "access_token": META_ACCESS_TOKEN},
            timeout=30,
        )
        publish_data = publish_r.json()
        if publish_data.get("id"):
            return True, f"Publicado en Instagram. Media ID: {publish_data['id']}"
        err = publish_data.get("error", {}).get("message", "Error publicando en Instagram")
        return False, err
    except Exception as e:
        return False, f"Excepcion Instagram: {e}"
