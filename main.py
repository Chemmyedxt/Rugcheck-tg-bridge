import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIG ===
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === RUGCHECK SCRAPER ===
def get_rugcheck_data(ca: str) -> str:
    try:
        url = f"https://rugcheck.xyz/tokens/{ca}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"❌ Failed to fetch data for {ca}. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Rugcheck Score
        score_section = soup.find('div', string=lambda s: s and 'Score:' in s)
        score = score_section.text.strip() if score_section else "Score not found"

        # Analytics
        analytics = soup.find_all('div', class_='text-sm')
        extracted = [a.get_text(strip=True) for a in analytics[:6]]

        result = f"📊 Rugcheck Results for `{ca}`\n\n"
        result += f"{score}\n\n"
        result += "\n".join(extracted)
        result += f"\n\n🔗 https://rugcheck.xyz/tokens/{ca}"

        return result

    except Exception as e:
        logger.error(f"Error scraping rugcheck.xyz: {e}")
        return "⚠️ Error while checking the contract."

# === TELEGRAM HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) == 44:
        await update.message.reply_text("⏳ Checking rugcheck.xyz, please wait...")
        result = get_rugcheck_data(text)
        await update.message.reply_text(result, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Send a valid 44-character Solana contract address.")

# === MAIN FUNCTION ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
