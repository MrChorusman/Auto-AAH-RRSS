# -*- coding: utf-8 -*-
"""
Bot de Telegram para aprobar publicaciones.
Responde a: /publicar_x (publica en X), /ver (muestra borrador), /cancelar (borra borrador).
Puedes usar tu bot @MrChorusman_bot poniendo su token en TELEGRAM_BOT_TOKEN.
"""
import asyncio
import sys
from pathlib import Path

# Añadir raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.estado_borrador import cargar_borrador, limpiar_borrador
from src.telegram_send import enviar_mensaje
from src.twitter_post import publicar_x


async def cmd_ver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != str(TELEGRAM_CHAT_ID):
        await update.message.reply_text("No autorizado.")
        return
    b = cargar_borrador()
    if not b:
        await update.message.reply_text("No hay borrador pendiente.")
        return
    await update.message.reply_text(
        f"Borrador: {b['titulo']}\n"
        f"Bandas: {', '.join(b['bandas'])}\n"
        f"Usa /publicar_x para publicar en X."
    )


async def cmd_publicar_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != str(TELEGRAM_CHAT_ID):
        await update.message.reply_text("No autorizado.")
        return
    b = cargar_borrador()
    if not b:
        await update.message.reply_text("No hay borrador pendiente. Ejecuta antes el script principal.")
        return
    copy_x = b["copies"].get("x", {}).get("copy", "")
    img = b.get("imagen_path")
    ok = publicar_x(copy_x, Path(img) if img else None)
    if ok:
        await update.message.reply_text("✅ Publicado en X.")
    else:
        await update.message.reply_text(
            "❌ Error al publicar en X. Revisa TWITTER_* en .env y que el borrador tenga imagen."
        )


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != str(TELEGRAM_CHAT_ID):
        await update.message.reply_text("No autorizado.")
        return
    limpiar_borrador()
    await update.message.reply_text("Borrador cancelado.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        print("Falta TELEGRAM_BOT_TOKEN en .env")
        return
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("ver", cmd_ver))
    app.add_handler(CommandHandler("publicar_x", cmd_publicar_x))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
