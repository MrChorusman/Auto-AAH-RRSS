# -*- coding: utf-8 -*-
"""
Guarda y carga el borrador actual pendiente de aprobación (para Telegram bot y publicación).
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import OUTPUT_DIR


BORRADOR_FILE = OUTPUT_DIR / "borrador_actual.json"


def guardar_borrador(
    guid: str,
    titulo: str,
    bandas: List[str],
    copies: Dict[str, Dict[str, Any]],
    imagen_path: str,
    imagenes_extra: Optional[List[str]] = None,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "guid": guid,
        "titulo": titulo,
        "bandas": bandas,
        "copies": copies,
        "imagen_path": imagen_path,
        "imagenes_extra": imagenes_extra or [],
    }
    with open(BORRADOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_borrador() -> Optional[Dict[str, Any]]:
    if not BORRADOR_FILE.exists():
        return None
    with open(BORRADOR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def limpiar_borrador() -> None:
    if BORRADOR_FILE.exists():
        BORRADOR_FILE.unlink()
