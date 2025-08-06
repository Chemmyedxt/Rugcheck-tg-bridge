import os
import logging
import asyncio
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging for Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Function to scrape Rugcheck.xyz using Playwright
async def check_rugcheck(contract_address):
    url = f"https://rugcheck.xyz/tokens/{contract_address}"
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = await browser.new_page()
            await page.goto(url, timeout=30000)  # 30s timeout
            await page.wait_for_load_state("networkidle")  # Wait for page to fully load
            
            # Extract stat cards (assuming Tailwind-style classes)
            cards = await page.query_selector_all("div.border.rounded-xl")  # Adjust based on inspection
            result = {"contract_address": contract_address}
            
            # Loop through cards to find key metrics
            for card in cards:
                key_elem = await card.query_selector("div.text-xs")  # Key label (e.g., "Risk Score")
                value_elem = await card.query_selector("div.text-sm")  # Value (e.g., "Low")
                if key_elem and value_elem:
                    key = await key_elem.inner_text()
                    value = await value_elem.inner_text()
                    result[key.lower().replace(" ", "_")] = value.strip() if value else "Not found"
            
            # Fallback if no data found
            if len(result) <= 1:  # Only contract_address exists
                result["error"] = "No data found. Check selectors or contract address."
            
            await browser.close()
            return result
    except Exception as e:
        logger.error(f"Error scraping Rugcheck.xyz for {contract_address}: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}
    finally:
        # Non-blocking delay to avoid rate limits
        await asyncio.sleep(1)

# Telegram bot command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a Solana contract address, and I'll check it on Rugcheck.xyz!\n"
        "Example: 7x8ZfY2qY2Yw1Z8bG1gP7Z6X6X6X6X6X6X6X6X6X6X6"
    )

# Handle incoming messages (contract addresses)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contract_address = update.message.text.strip()
    
    # Basic validation for Solana address (43-44 characters, base58)
    if len(contract_address) not in [43, 44] or not contract_address.isalnum():
        await update.message.reply_text("Please send a valid Solana contract address (43-44 characters, alphanumeric).")
        return
    
    # Log the request
    logger.info(f"Checking contract address: {contract_address}")
    
    # Check Rugcheck.xyz
    result = await check_rugcheck(contract_address)
    
    # Format response
    if "error" in result:
        await update.message.reply_text(result["error"])
    else:
        response = f"Results for {result['contract_address']}:\n"
        for key, value in result.items():
            if key != "contract_address":
                response += f"{key.replace('_', ' ').title()}: {value}\n"
        await update.message.reply_text(response)

# Main function to run the bot
async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
