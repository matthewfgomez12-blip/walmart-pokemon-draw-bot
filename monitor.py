import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

response = requests.post(
    url,
    json={
        "chat_id": CHAT_ID,
        "text": (
            "🚨 WALMART POKÉMON BOT TEST 🚨\n\n"
            "✅ GitHub Actions connected!\n"
            "✅ Telegram notifications working!\n\n"
            "🎯 Ready to monitor Walmart drawings."
        )
    },
    timeout=20
)

response.raise_for_status()

print("Telegram notification sent successfully!")
