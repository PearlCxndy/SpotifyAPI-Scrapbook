import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Authenticate Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
))

def get_current_song():
    """Get the currently playing song from Spotify."""
    current_track = sp.current_user_playing_track()
    if current_track is not None:
        song = current_track["item"]["name"]
        artist = current_track["item"]["artists"][0]["name"]
        return song, artist
    return None, None

# Example usage
song, artist = get_current_song()
print(f"Now Playing: {song} by {artist}")
