import os
import logging
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Rugcheck scraper
async def check_rugcheck(contract_address):
    url = f"https://rugcheck.xyz/tokens/{contract_address}"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            page = await context.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            cards = await page.query_selector_all("div.border.rounded-xl")
            result = {"contract_address": contract_address}

            for card in cards:
                key_elem = await card.query_selector("div.text-xs")
                value_elem = await card.query_selector("div.text-sm")
                if key_elem and value_elem:
                    key = await key_elem.inner_text()
                    value = await value_elem.inner_text()
                    result[key.lower().replace(" ", "_")] = value.strip()

            if len(result) <= 1:
                result["error"] = "No data found. Check selectors or contract address."

            await browser.close()
            return result

    except Exception as e:
        logger.error(f"Error scraping: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}
    finally:
        await asyncio.sleep(1)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📩 Send a Solana contract address and I’ll fetch Rugcheck data.\n\nExample:\n`7x8ZfY2qY2Yw1Z8bG1gP7Z6X6X6X6X6X6X6X6X6X6X6`",
        parse_mode="Markdown"
    )

# CA Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contract_address = update.message.text.strip()
    if len(contract_address) not in [43, 44] or not contract_address.isalnum():
        await update.message.reply_text("❌ Invalid Solana contract address (43–44 chars, alphanumeric).")
        return

    logger.info(f"Checking: {contract_address}")
    result = await check_rugcheck(contract_address)

    if "error" in result:
        await update.message.reply_text(result["error"])
    else:
        response = f"📊 Rugcheck Results for `{result['contract_address']}`:\n"
        for key, value in result.items():
            if key != "contract_address":
                response += f"• {key.replace('_', ' ').title()}: {value}\n"
        await update.message.reply_text(response, parse_mode="Markdown")

# Main bot
async def run_bot():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    await app.run_polling()

# Entry
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(run_bot())
