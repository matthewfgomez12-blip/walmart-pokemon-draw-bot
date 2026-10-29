import os
import json
import requests
from bs4 import BeautifulSoup

# ==========================================
# WALMART POKEMON DRAWING MONITOR
# ==========================================

URL = "https://www.walmart.com/shop/collectibles/draw"
STATE_FILE = "seen.json"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = ["pokemon", "pokémon"]


# ==========================================
# SEND TELEGRAM NOTIFICATION
# ==========================================

def send_telegram(message):

    telegram_url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    )

    response = requests.post(
        telegram_url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )

    response.raise_for_status()

    print("Telegram notification sent successfully!")


# ==========================================
# CHECK WALMART DRAWINGS
# ==========================================

def get_drawings():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    drawings = []

    closed_section = False
    found_closed_heading = False

    headings = soup.find_all(["h2", "h3"])

    for heading in headings:

        name = heading.get_text(
            " ",
            strip=True
        )

        name_lower = name.lower()

        # Detect closed drawing section
        if heading.name == "h2":

            if "closed drawings" in name_lower:

                closed_section = True
                found_closed_heading = True

            else:

                closed_section = False

        # Find Pokemon products outside closed section
        if heading.name == "h3" and not closed_section:

            if any(
                keyword in name_lower
                for keyword in KEYWORDS
            ):

                drawings.append(name)

    # Safety check
    if not found_closed_heading:

        raise RuntimeError(
            "Walmart page structure changed. "
            "Closed drawings section not found."
        )

    return list(dict.fromkeys(drawings))


# ==========================================
# LOAD DRAWING HISTORY
# ==========================================

def load_history():

    if not os.path.exists(STATE_FILE):

        return []

    with open(STATE_FILE, "r") as file:

        return json.load(file)


# ==========================================
# SAVE DRAWING HISTORY
# ==========================================

def save_history(seen):

    with open(STATE_FILE, "w") as file:

        json.dump(
            seen,
            file,
            indent=2
        )


# ==========================================
# MAIN MONITOR
# ==========================================

def main():

    print("Starting Walmart Pokemon Drawing Monitor...")

    # Get current drawings
    drawings = get_drawings()

    print("Pokemon drawing candidates found:", len(drawings))

    for drawing in drawings:

        print("Detected:", drawing)

    # Load previous history
    seen = load_history()

    # First run: establish baseline
    if len(seen) == 0:

        print("Initializing drawing history...")

        save_history(drawings)

        print("Initial history saved.")

        return

    # Find new drawings
    new_drawings = [
        drawing
        for drawing in drawings
        if drawing not in seen
    ]

    print("New drawing candidates:", len(new_drawings))

    # Send notifications
    for drawing in new_drawings:

        message = (
            "🚨 NEW WALMART POKÉMON DRAWING DETECTED!\n\n"
            f"🎴 {drawing}\n\n"
            "🔗 " + URL + "\n\n"
            "⚡ Check Walmart to confirm entry is open!"
        )

        send_telegram(message)

        # Add drawing to history
        seen.append(drawing)

        # Save after successful notification
        save_history(seen)

    print("Monitoring completed successfully!")


# ==========================================
# START BOT
# ==========================================

if __name__ == "__main__":

    main()
