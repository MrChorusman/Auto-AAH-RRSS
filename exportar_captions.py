# -*- coding: utf-8 -*-
"""
Escribe en generado/ los textos listos para copiar en Instagram y TikTok.
Ejecutar después de que main.py haya generado el borrador.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR
from src.estado_borrador import cargar_borrador


def main() -> int:
    b = cargar_borrador()
    if not b:
        print("No hay borrador en generado/borrador_actual.json")
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for red in ("instagram", "tiktok"):
        c = b["copies"].get(red, {})
        copy = c.get("copy", "")
        tags = " ".join(c.get("hashtags", []))
        texto = f"{copy}\n\n{tags}"
        path = OUTPUT_DIR / f"caption_{red}.txt"
        path.write_text(texto, encoding="utf-8")
        print(f"Escrito: {path}")
    print("Listo. Usa los archivos para pegar en Instagram y TikTok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
