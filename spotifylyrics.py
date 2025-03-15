import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import os

# Load API keys from API.env explicitly
dotenv_path = os.path.join(os.path.dirname(__file__), "API.env")
load_dotenv(dotenv_path)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


# Debugging: Print values to verify they load
print(f"SPOTIFY_CLIENT_ID: {SPOTIFY_CLIENT_ID}")
print(f"SPOTIFY_CLIENT_SECRET: {SPOTIFY_CLIENT_SECRET}")
print(f"SPOTIFY_REDIRECT_URI: {SPOTIFY_REDIRECT_URI}")

# Authenticate Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
))

def get_current_song():
    """Get the currently playing track from Spotify."""
    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None and current_track['item'] is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            album_art_url = current_track['item']['album']['images'][0]['url']  # Get the first image URL
            return track_name, artist_name, album_art_url
    except Exception as e:
        print(f"Error fetching current track: {e}")
    return None, None, None