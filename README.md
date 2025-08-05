# Rugcheck Telegram Bot

A simple Telegram bot that fetches RugCheck analytics and scores for Solana contract addresses.

## 🛠 Features
- Accepts 44-character Solana contract addresses
- Scrapes data from [rugcheck.xyz](https://rugcheck.xyz)
- Sends score and basic analytics back to user
- Works for anyone (no Telegram ID restriction)

## 🚀 How to Deploy (on Railway)
1. Clone or upload this project
2. Ensure `requirements.txt` and `main.py` are present
3. Railway auto-detects and installs dependencies
4. (Optional) Add `BOT_TOKEN` as an environment variable

## 🧾 Example Usage
Send a message like:
9vX3s8i##############UozWFQg [ca]
Bot responds with RugCheck score and key analytics.

## ⚙️ Built With
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [requests](https://docs.python-requests.org/)

## 📄 License
MIT
