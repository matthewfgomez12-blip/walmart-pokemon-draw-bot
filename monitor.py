import requests
from bs4 import BeautifulSoup

URL = "https://www.walmart.com/shop/collectibles/draw"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("HTTP STATUS:", response.status_code)

print("\n=== PAGE HEADINGS ===")

for heading in soup.find_all(
    ["h1", "h2", "h3", "h4"]
):
    print(
        heading.name,
        ":",
        heading.get_text(" ", strip=True)
    )

print("\n=== POKEMON PRODUCT LINKS ===")

for link in soup.find_all("a", href=True):

    text = link.get_text(" ", strip=True)

    if "pokemon" in text.lower() or "pokémon" in text.lower():

        print("\nPRODUCT:", text[:250])
        print("LINK:", link["href"])

        parent = link.parent

        for level in range(3):
            if parent:
                print(
                    f"PARENT {level}:",
                    parent.get_text(" ", strip=True)[:400]
                )
                parent = parent.parent

print("\n=== DRAWING STATUS BUTTONS ===")

for button in soup.find_all("button"):

    text = button.get_text(" ", strip=True)

    if any(
        word in text.lower()
        for word in ["enter", "draw", "closed", "open"]
    ):
        print("BUTTON:", text[:200])

print("\nDiagnostic complete.")
