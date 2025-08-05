import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === SCRAPER FUNCTION ===
def get_rugcheck_data(ca: str) -> str:
    try:
        url = f"https://rugcheck.xyz/tokens/{ca}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return f"❌ Failed to fetch data for `{ca}`. Status code: {res.status_code}"

        soup = BeautifulSoup(res.text, "html.parser")
        result = f"📊 Rugcheck Analytics for `{ca}`\n\n"

        # === Scrape Main Info Cards (LP, Renounced, Mint, etc.)
        cards = soup.find_all("div", class_="border rounded-xl")
        for card in cards:
            key = card.find("div", class_="text-xs")
            value = card.find("div", class_="text-sm")
            if key and value:
                result += f"{key.get_text(strip=True)}: {value.get_text(strip=True)}\n"

        # === Scrape Any Warnings (Red Texts)
        warnings = soup.find_all("div", class_="text-red-500")
        if warnings:
            result += "\n⚠️ *Warnings:*\n"
            for w in warnings:
                result += f"• {w.get_text(strip=True)}\n"

        # === Scrape Top Holders
        holders_section = soup.find("div", string=lambda t: t and "Top Holders" in t)
        if holders_section:
            holders_table = holders_section.find_next("table")
            if holders_table:
                result += "\n👥 *Top Holders:*\n"
                rows = holders_table.find_all("tr")[1:4]  # Show top 3
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        wallet = cols[0].get_text(strip=True)
                        percent = cols[1].get_text(strip=True)
                        result += f"- {wallet}: {percent}\n"

        # === Fallback
        if len(result.strip().splitlines()) <= 2:
            result += "No analytics found. Token might not be indexed yet."

        result += f"\n\n🔗 [View on Rugcheck](https://rugcheck.xyz/tokens/{ca})"
        return result

    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return "⚠️ An unexpected error occurred while scraping rugcheck."

# === MESSAGE HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isalnum() and len(text) >= 32:
        await update.message.reply_text("🔍 Fetching rugcheck analytics, please wait...")
        data = get_rugcheck_data(text)
        await update
