import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load API keys from API.env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, "API.env")
load_dotenv(dotenv_path)

GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")

def get_lyrics(song, artist):
    """Fetch lyrics from Genius API"""
    if not GENIUS_API_KEY:
        return "Error: Genius API key is missing."

    base_url = "https://api.genius.com"
    search_url = f"{base_url}/search"
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}

    params = {"q": f"{song} {artist}"}
    response = requests.get(search_url, headers=headers, params=params)
    json_response = response.json()

    # Extract first song result
    if json_response['response']['hits']:
        song_url = json_response['response']['hits'][0]['result']['url']

        # Scrape lyrics from Genius webpage
        page = requests.get(song_url)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics_divs = soup.find_all("div", class_="Lyrics__Container-sc-1ynbvzw-6")

        lyrics = "\n".join([line.text for div in lyrics_divs for line in div])
        return lyrics if lyrics else "Lyrics not found."
    
    return "Lyrics not found."

# Debugging: Check if Genius API key is loaded correctly
print(f"GENIUS_API_KEY: {GENIUS_API_KEY}")  # Should print a valid key
