# -*- coding: utf-8 -*-
"""
Flujo principal: revisar RSS (lunes 8h/9h/10h), generar borrador y enviar a Telegram.
Ejecutar con: python main.py
Con bandas manuales (si no se extrajeron del feed): BANDAS="Artista 1, Artista 2" python main.py
Programar con cron: 0 8,9,10 * * 1 cd "/Applications/Auto AAH RRSS" && python main.py
"""
import os
import sys
from pathlib import Path

# Asegurar que se importe config desde la raíz
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR, LOGO_PATH, RSS_URL
from src.rss import (
    episodio_ya_procesado,
    marcar_episodio_procesado,
    obtener_ultimo_episodio,
)
from src.image_gen import generar_imagen
from src.image_collage import generar_collage, generar_collage_con_imagenes
from src.copy_gen import generar_copy_y_hashtags
from src.estado_borrador import guardar_borrador
from src.telegram_send import enviar_borrador, enviar_sin_bandas


ARCHIVO_ESTADO = OUTPUT_DIR / "ultimo_episodio.txt"


def main() -> int:
    if not RSS_URL:
        print("Configura RSS_URL en .env")
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ep = obtener_ultimo_episodio(RSS_URL)
    if not ep:
        print("No se pudo obtener el feed o no hay episodios.")
        return 0
    if episodio_ya_procesado(ep.guid, str(ARCHIVO_ESTADO)):
        print(f"Episodio ya procesado: {ep.titulo}")
        return 0

    # Si no hay bandas, usar BANDAS en env o avisar por Telegram y bloquear
    bandas_manual = os.getenv("BANDAS", "").strip()
    if not ep.bandas:
        if bandas_manual:
            ep.bandas = [b.strip() for b in bandas_manual.split(",") if b.strip()]
        if not ep.bandas:
            enviar_sin_bandas(ep.titulo, ep.guid)
            print("Episodio sin bandas. Enviado aviso a Telegram. Para desbloquear: BANDAS=\"A, B, C\" python main.py")
            return 0

    # Generar imágenes: collage con portadas reales (iTunes) como principal
    imagenes = []
    if ep.bandas_y_canciones:
        try:
            collage = generar_collage_con_imagenes(
                ep.bandas_y_canciones,
                ep.titulo,
                OUTPUT_DIR,
                prefijo="aah",
            )
            imagenes.append(collage)
        except Exception:
            try:
                collage = generar_collage(ep.bandas_y_canciones, ep.titulo, OUTPUT_DIR, prefijo="aah")
                imagenes.append(collage)
            except Exception:
                pass
    variantes_logo = generar_imagen(LOGO_PATH, ep.titulo, OUTPUT_DIR, prefijo="aah")
    imagenes.extend(variantes_logo)
    imagen_principal = imagenes[0]

    # Copy y hashtags por red
    copies = generar_copy_y_hashtags(ep.titulo, ep.bandas, usar_ia=True)

    # Guardar borrador para que el bot pueda publicar al aprobar
    guardar_borrador(
        guid=ep.guid,
        titulo=ep.titulo,
        bandas=ep.bandas,
        copies=copies,
        imagen_path=str(imagen_principal),
        imagenes_extra=[str(p) for p in imagenes[1:]],
    )

    # Enviar a Telegram para revisión
    ok = enviar_borrador(
        imagen_path=imagen_principal,
        titulo=ep.titulo,
        bandas=ep.bandas,
        copies=copies,
        guid=ep.guid,
    )
    if ok:
        marcar_episodio_procesado(ep.guid, str(ARCHIVO_ESTADO))
        print("Borrador enviado a Telegram. Revisa y usa /publicar_x en el bot para publicar en X.")
    else:
        print("Borrador generado en generado/ pero no se pudo enviar a Telegram (revisa TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
