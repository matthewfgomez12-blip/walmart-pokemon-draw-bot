import requests
from bs4 import BeautifulSoup
import os
import json

URL = "https://www.walmart.com/shop/collectibles/draw"
STATE_FILE = "seen.json"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    ).raise_for_status()


def get_drawings():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    drawings = {}

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)

        if "pokemon" in text.lower() or "pokémon" in text.lower():
            link = a["href"]

            if link.startswith("/"):
                link = "https://www.walmart.com" + link

            drawings[link] = text

    return drawings


def main():
    drawings = get_drawings()

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            seen = json.load(f)
    else:
        seen = []

    new = {
        link: name
        for link, name in drawings.items()
        if link not in seen
    }

    for link, name in new.items():
        send_telegram(
            f"🚨 NEW POKÉMON DRAWING DETECTED!\n\n"
            f"{name}\n\n"
            f"🔗 {link}"
        )

    with open(STATE_FILE, "w") as f:
        json.dump(list(set(seen) | set(drawings)), f, indent=2)

    print(f"Found {len(drawings)} drawings, {len(new)} new.")


if __name__ == "__main__":
    main()
