import requests
from bs4 import BeautifulSoup

URL = "https://www.walmart.com/shop/collectibles/draw"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)

print("HTTP STATUS:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

print("\nPAGE TITLE:")
print(soup.title.get_text(strip=True) if soup.title else "No title")

print("\nPOKEMON REFERENCES:")

for word in ["Pokemon", "Pokémon", "pokemon"]:
    print(f"{word}: {text.count(word)}")

print("\nDRAWING STATUS REFERENCES:")

for phrase in [
    "Open drawings",
    "Closed drawings",
    "Enter drawing",
    "Drawing results"
]:
    print(f"{phrase}: {text.lower().count(phrase.lower())}")

print("\nPAGE PREVIEW:")
print(text[:3000])
