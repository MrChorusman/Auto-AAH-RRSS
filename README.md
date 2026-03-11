# Auto AAH RRSS

Automatización **gratuita** para publicar en **X**, **Instagram** y **TikTok** cuando sale un nuevo episodio de **A Altas Horas** (Ivoox). Incluye revisión previa por Telegram.

## Qué hace

1. **Lunes 8:00, 9:00 y 10:00** (o cuando ejecutes el script): consulta el feed RSS del podcast.
2. Si hay **episodio nuevo**:
   - Extrae **bandas** de la descripción del episodio.
   - Si no hay bandas → te avisa por **Telegram** y **bloquea** hasta que confirmes (respondiendo con la lista).
   - Si hay bandas → genera **variantes de imagen** (logo + título) y **textos** por red (X, Instagram, TikTok) con tono cercano/irónico y “enlace en bio”.
3. Te envía el **borrador a Telegram** (imagen + textos + hashtags).
4. Tú **revisas** y, cuando quieras, usas el bot: **/publicar_x** para publicar en X. Para Instagram y TikTok se generan los assets en la carpeta `generado/` para que puedas subirlos manualmente (o conectar APIs después).

## Requisitos (todo gratuito)

- Python 3.10+
- Cuenta en **X** (Twitter) y en **Telegram**
- Opcional: **Groq** (gratis) para generar copy con IA; si no, se usa plantilla

## Instalación

```bash
cd "/Applications/Auto AAH RRSS"
python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus claves
```

## Configuración (.env)

1. **RSS_URL**: URL del feed RSS del podcast en Ivoox (en la página del podcast, opción RSS/suscripción).
2. **Telegram**: crea un bot con [@BotFather](https://t.me/BotFather), copia el token a `TELEGRAM_BOT_TOKEN`. Envía `/start` a tu bot y obtén tu `TELEGRAM_CHAT_ID` (puedes usar [@userinfobot](https://t.me/userinfobot) tras escribir al bot).
3. **X (Twitter)**: en [developer.twitter.com](https://developer.twitter.com) crea un proyecto y una app, genera API Key, Secret, Access Token y Access Token Secret; rellena las variables `TWITTER_*` en `.env`.
4. **Opcional – Groq**: en [groq.com](https://groq.com) crea una API key y ponla en `GROQ_API_KEY` para que el copy se genere con IA.

Puedes usar tu bot **@MrChorusman_bot**: pon su token en `TELEGRAM_BOT_TOKEN` y tu chat id en `TELEGRAM_CHAT_ID`.

## Uso

### Revisar si hay episodio nuevo y generar borrador

```bash
python main.py
```

Si hay episodio nuevo y bandas, se generan las imágenes en `generado/`, se guarda el borrador y se envía a Telegram.

### Bot de Telegram (revisión y publicación en X)

Arranca el bot (en otra terminal o en segundo plano) para poder aprobar desde Telegram:

```bash
python bot/bot.py
```

Comandos del bot:

- **/ver** – Ver el borrador pendiente.
- **/publicar_x** – Publicar en X el borrador actual (texto + imagen).
- **/cancelar** – Borrar el borrador pendiente.

### Programar revisión los lunes (8h, 9h, 10h)

En macOS/Linux, con `cron`:

```bash
crontab -e
```

Añade (ajusta la ruta si cambias de carpeta):

```
0 8,9,10 * * 1 cd "/Applications/Auto AAH RRSS" && ./venv/bin/python main.py
```

O usando el script: `chmod +x ejecutar_revision.sh` y en crontab:

```
0 8,9,10 * * 1 "/Applications/Auto AAH RRSS/ejecutar_revision.sh"
```

Si usas `launchd` en macOS, puedes crear un plist que ejecute `main.py` a esas horas los lunes.

## Instagram y TikTok

- **Imágenes** (post + variantes para story): en `generado/` (por ejemplo `aah_episodio_abajo.png`, `aah_episodio_arriba.png`).
- **Textos y hashtags**: se envían en el mensaje de Telegram.
- La sintonía del programa (*Blue Lining, white trenchcoat* – Mando Diao) puedes añadirla al subir la Story/Reel manualmente; el script no incluye audio por defecto para evitar temas de derechos.
- Para **TikTok**: de momento se genera la imagen y el texto; puedes crear el vídeo con otra herramienta (p. ej. imagen + audio) y subirlo, o más adelante integrar la API de TikTok si la tienes.

## Estructura

- `main.py` – Flujo: RSS → bandas → imagen → copy → Telegram.
- `config.py` – Variables de entorno.
- `src/rss.py` – Lectura del feed y extracción de bandas.
- `src/image_gen.py` – Variantes logo + título.
- `src/copy_gen.py` – Textos y hashtags (plantilla + opcional Groq).
- `src/telegram_send.py` – Envío del borrador por Telegram.
- `src/twitter_post.py` – Publicación en X.
- `src/estado_borrador.py` – Guardar/cargar borrador para el bot.
- `bot/bot.py` – Bot de Telegram (comandos /ver, /publicar_x, /cancelar).
- `generado/` – Imágenes y borrador actual (creado al ejecutar).

## Sin presupuesto

Todo lo que usa el proyecto tiene plan gratuito: Python, feedparser, Pillow, Telegram Bot API, Twitter API (nivel free), Groq (free tier). Instagram y TikTok se apoyan en assets generados y publicación manual hasta que conectes sus APIs si lo deseas.
