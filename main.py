import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Make sure BOT_TOKEN is set in environment

def start(update, context):
    update.message.reply_text("Send me a valid contract address (CA) and I'll give you the Rugcheck link.")

def get_rugcheck(update, context):
    ca = update.message.text.strip()
    
    # Check for EVM (42 chars, starts with 0x) or Solana (44 chars)
    if (len(ca) == 42 and ca.startswith("0x")) or len(ca) == 44:
        url = f"https://rugcheck.xyz/tokens/{ca}"
        button = InlineKeyboardButton("CHECK ON RUGCHECK", url=url)
        keyboard = InlineKeyboardMarkup([[button]])
        update.message.reply_text("Here you go:", reply_markup=keyboard)
    else:
        # Ignore invalid messages (does not reply)
        return

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_rugcheck))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
