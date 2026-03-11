# Auto AAH RRSS - Project Info

## 1) Objetivo del proyecto

Automatizar el flujo de deteccion de episodios nuevos de **A Altas Horas** (Ivoox), generar assets y copy para redes, y pasar por validacion en Telegram antes de publicar.

Estado actual:
- **X**: publicacion automatizable desde el bot de Telegram.
- **Instagram / TikTok**: flujo de preparacion de assets y copys listo; publicacion automatica pendiente de conectar APIs oficiales.

## 2) Flujo funcional (actual)

1. `main.py` consulta RSS (Ivoox).
2. Detecta episodio nuevo y evita reprocesar GUID ya tratado.
3. Extrae bandas y canciones del bloque tipo `Banda - Cancion`.
4. Genera imagenes:
   - Collage principal 2x2 con 4 portadas reales encontradas (iTunes Search API).
   - Variantes logo + titulo.
5. Genera copy por red (CTA breve, sin mencionar bandas) y hashtags.
6. Guarda borrador en `generado/borrador_actual.json`.
7. Envia a Telegram en dos mensajes:
   - Mensaje 1: imagen + caption corta.
   - Mensaje 2: textos por red + hashtags + GUID.
8. Desde Telegram, comando `/publicar_x` publica en X.

## 3) Arquitectura de archivos

- `main.py`: orquestacion principal.
- `config.py`: lectura de variables desde `.env`.
- `src/rss.py`: parseo RSS, extraccion de bandas/canciones.
- `src/image_collage.py`: collage con portadas reales (iTunes).
- `src/image_gen.py`: variantes del logo con titulo.
- `src/copy_gen.py`: copy y hashtags por red.
- `src/telegram_send.py`: envio del borrador por Telegram.
- `src/twitter_post.py`: publicacion en X con imagen.
- `src/estado_borrador.py`: persistencia del borrador actual.
- `bot/bot.py`: comandos Telegram (`/ver`, `/publicar_x`, `/cancelar`).
- `exportar_captions.py`: exporta captions de Instagram/TikTok a txt.
- `ejecutar_revision.sh`: helper para cron.

## 4) Variables de entorno usadas

En `.env`:

- `RSS_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`
- `GROQ_API_KEY` (opcional)
- `LOGO_PATH`
- `LINK_BIO`
- `LINK_X` (enlace directo para X)

Nota: no subir credenciales reales a GitHub.

## 5) Comandos de uso

Instalacion:

```bash
cd "/Applications/Auto AAH RRSS"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Ejecutar flujo:

```bash
python main.py
```

Bot Telegram:

```bash
python bot/bot.py
```

Export captions:

```bash
python exportar_captions.py
```

Cron lunes 8/9/10:

```bash
0 8,9,10 * * 1 cd "/Applications/Auto AAH RRSS" && ./venv/bin/python main.py
```

## 6) Decisiones de producto implementadas

- Telegram en 2 mensajes para evitar problemas de limites/caption.
- Copy en estilo CTA breve.
- En **X** se usa enlace directo (`LINK_X`).
- En **Instagram/TikTok** se usa CTA tipo "enlace en bio".
- Collage homogeneo: solo 4 portadas encontradas (2x2), sin celdas vacias.
- Franja superior de marca "A ALTAS HORAS".
- Footer simplificado con CTA visual.

## 7) Limitaciones actuales

- Instagram y TikTok no publican automaticamente todavia (falta OAuth/API de cada plataforma).
- iTunes puede no devolver portada para algunas combinaciones banda/cancion.
- El bot Telegram publica solo en X por ahora.

## 8) Pendiente recomendado (siguiente fase)

1. Integrar Instagram Graph API (publicacion feed).
2. Integrar TikTok API (subida de video/foto).
3. Crear generador de video vertical 9:16 para TikTok/Stories.
4. Mejorar control de errores y logs persistentes.
5. Añadir tests basicos de parseo RSS y generacion de assets.

## 9) Seguridad y buenas practicas

- Este repo incluye `.gitignore` para excluir `.env`, `venv` y `generado`.
- Rotar claves expuestas previamente en chats/entornos de pruebas.
- Mantener tokens en gestor seguro y no en codigo.

