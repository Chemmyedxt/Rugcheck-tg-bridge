import os
import logging
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Function to scrape Rugcheck.xyz
async def check_rugcheck(contract_address):
    url = f"https://rugcheck.xyz/tokens/{contract_address}"
    result = {"contract_address": contract_address}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            # Try scraping individual fields
            try:
                result["risk_score"] = await page.locator("h4:has-text('Risk Analysis') + h4").inner_text()
            except: result["risk_score"] = "Not found"

            try:
                result["launch_status"] = await page.locator("h6:has-text('Launch Insights') + div").inner_text()
            except: result["launch_status"] = "Not found"

            try:
                result["supply"] = await page.locator("h4:has-text('Supply') + div").inner_text()
            except: result["supply"] = "Not found"

            try:
                result["creator"] = await page.locator("h4:has-text('Creator') + a").inner_text()
            except: result["creator"] = "Not found"

            try:
                result["market_cap"] = await page.locator("h4:has-text('Market Cap') + div").inner_text()
            except: result["market_cap"] = "Not found"

            try:
                result["holders"] = await page.locator("h4:has-text('Holders') + div").inner_text()
            except: result["holders"] = "Not found"

            try:
                result["lp_locked"] = await page.locator("h4:has-text('LP Locked') + div").inner_text()
            except: result["lp_locked"] = "Not found"

            try:
                result["top_holder_percent"] = await page.locator("h4:has-text('Top Holders') + h4").first.inner_text()
            except: result["top_holder_percent"] = "Not found"

            await browser.close()
            return result

    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a Solana contract address and I’ll fetch live stats from Rugcheck.xyz.\n\n"
        "Example: `E2gYJLgwup3DPaqYDXKj4kfHb6n4PR2CQyrvt6a2bonk`",
        parse_mode="Markdown"
    )
