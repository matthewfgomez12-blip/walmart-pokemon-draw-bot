import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.walmart.com/shop/collectibles/draw"
STATE_FILE = "seen.json"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = ["pokemon", "pokémon"]


def send_telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )
    response.raise_for_status()


def get_drawings():
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    drawings = []
    closed_section = False
    found_closed_heading = False

    for heading in soup.find_all(["h2", "h3"]):
        name = heading.get_text(" ", strip=True)

        if heading.name == "h2":
            if "closed drawings" in name.lower():
                closed_section = True
                found_closed_heading = True
            else:
                closed_section = False

        if heading.name == "h3" and not closed_section:
            if any(word in name.lower() for word in KEYWORDS):
                drawings.append(name)

    if not found_closed_heading:
        raise RuntimeError(
            "Walmart page structure changed: "
            "Closed drawings heading not found."
        )

    return list(dict.fromkeys(drawings))


def main():
    drawings = get_drawings()

    print("Active Pokémon drawing candidates:", drawings)

        if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            seen = json.load(f)
    else:
        seen = []

    # Initialize history without sending alerts
    if seen == []:
        with open(STATE_FILE, "w") as f:
            json.dump(drawings, f, indent=2)

        print("Initial drawing history saved.")
        return

# Initialize history without sending alerts.
if seen == []:
    with open(STATE_FILE, "w") as f:
        json.dump(drawings, f, indent=2)

    print("Initial drawing history saved.")
    return

    # First run establishes a baseline without alerts.
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(drawings, f, indent=2)

        print("Initial baseline saved.")
        return

    new_drawings = [
        name for name in drawings
        if name not in seen
    ]

    for name in new_drawings:
        message = (
            "🚨 POSSIBLE NEW WALMART POKÉMON DRAWING!\n\n"
            f"🎴 {name}\n\n"
            "🔗 " + URL + "\n\n"
            "Check Walmart to confirm entry is open."
        )

        send_telegram(message)
        print("Alert sent:", name)

        seen.append(name)

        # Save after each successful alert.
        with open(STATE_FILE, "w") as f:
            json.dump(seen, f, indent=2)

    print("Monitoring complete.")


if __name__ == "__main__":
    main()
