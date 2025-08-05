import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === BOT TOKEN ===
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8371661313:AAGWn2jzvpp2J4M6G9Pb6dOLsKWG2gMawP4"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === SMART VALIDATOR ===
def is_valid_ca(text):
    return text.isalnum() and 32 <= len(text) <= 44

# === MESSAGE HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if is_valid_ca(text):
        rugcheck_link = f"https://rugcheck.xyz/tokens/{text}"
        await update.message.reply_text(f"🔗 [View on Rugcheck]({rugcheck_link})", parse_mode="Markdown")
    else:
        if update.message.chat.type != "private":
            return
        await update.message.reply_text("⚠️ Send a valid Solana contract address.")

# === BOT LAUNCH ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
